import datetime
import json
import random
import re
import string
from dataclasses import dataclass, field
from typing import Literal

import docx
import requests
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail as core_send_mail
from django.db.models.query import QuerySet

from main.bot import bot

TYPE_USER = Literal['participant', 'judge', 'sponsor', 'manager', 'leader', 'admin']

def send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    html_message=None,
    fail_silently=False,
):
    return core_send_mail(subject, message, from_email, recipient_list, html_message, fail_silently)
    try:
        resp = requests.post('http://127.0.0.1:8443/send_email', data={
            'subject': subject,
            'message': message,
            'recipient': recipient_list,
            'html_message': html_message,
        }, timeout=30000)
        if resp.status_code != 200:
            raise TimeoutError(resp.text)

        return len(recipient_list) if isinstance(recipient_list, list) else 1
    except Exception as e:
        if not fail_silently:
            raise

        args = f'{subject}, {message}, {from_email}, {recipient_list}, {fail_silently}, {html_message}'
        print(f'${send_mail.__module__}.{send_mail.__name__} ({args}) Exception: {e}')
        return 0


def get_random_string(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def create_user(email, type_user: TYPE_USER = ''):
    user = User.objects.filter(email=email).first()
    if user:
        return (user, 'Ранее вы участвали в чемпионате. Проверьте почту или восстановите пароль', False)

    password = get_random_string(10)
    user = User.objects.create_user(username=email, email=email, password=password)

    group = Group.objects.get(name=type_user + 's')
    if group:
        user.groups.add(group)
        user.save()

    return user, password, True


@bot.check_bot
def notify_user_tg(subject: str, message: str, tg: list[str] | str, fail_silently=False):
    if isinstance(tg, str):
        tg = [tg]

    for t in list(set(tg)):
        t = t.strip().split('/')[-1].rstrip('/')
        if not (t.isnumeric() or t.startswith('@') or t.startswith('-') or t.startswith('+')):
            t = '@' + t
        bot.callfunc(bot.bot.send_message, t, f'{subject}\n\n{message}', fail_silently=fail_silently)


def get_group_tg():
    users = User.objects.filter(is_superuser=True)
    return list(set([user.profileadmin.telegram for user in users if user.profileadmin.telegram])) or ['-4713095754']


def notify_user(subject: str, message: str, recipient: list[str] | str, fail_silently=False, tg: list[str] | str = ""):
    if len(recipient) > 0:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            (list(set(recipient)) if isinstance(recipient, list) else [recipient]),
            fail_silently=fail_silently,
        )
    if tg:
        notify_user_tg(subject, message, tg, fail_silently=fail_silently)


def notify_admin(
    subject: str,
    message: str,
    recipient: list[str] | str | Literal['All'],
    fail_silently=True,
    tg: list[str] | str | Literal['ALL'] = "",
):
    need_tg = isinstance(tg, str) and tg == 'ALL'
    tgs = [] if need_tg else (tg if isinstance(tg, list) else [tg])

    if isinstance(recipient, str) and recipient == 'ALL':
        recipient = []
        users = User.objects.filter(is_superuser=True)
        for user in users:
            if need_tg:
                tgs.append(user.profile_admin.telegram)
            recipient.append(user.email)

    notify_user(subject, message, recipient, fail_silently, tg=tgs)


def notify_new_user(email: str, password: str, fail_silently=False, tg: str = ""):
    subject = "Заявка на Чемпионат"
    message = f"Ваша заявка на чемпионат принята!\n\nИспользуйте для входа:\nЛогин: {email}\nПароль: {password}"
    notify_user(subject, message, email, fail_silently=fail_silently)  # , tg=tg)


def marks_to_form_value(marks: QuerySet['Mark', 'Mark']):
    # criteries-<judge_id>-<block_id>-<critery_id>-<name>
    # comments-<judge_id>-<block_id>-<critery_id>-<name>
    marks_dict: dict[str, int | str] = {}

    for mark in marks:
        block_id, id, name = mark.critery.split('. ')
        critery = f"criteries-{mark.judge.id}-{block_id}-{id}-{name}"
        comment = f"comments-{mark.judge.id}-{block_id}-{id}-{name}"
        marks_dict[critery] = int(mark.mark)
        marks_dict[comment] = mark.comment

    print(marks_dict)

    return marks_dict


def parse_criteries(file_path: str, dst_path: str = ""):
    """
    Parse criteria from .docx file and save it to .json file.

    :param file_path: Path to .docx file
    :param dst_path: Path to .json file. If empty, will be saved to \<file_path\>.json
    :return: None
    """

    def to_number(string):
        if not string:
            return 0

        if '.' in string:
            return float(string)
        return int(string)

    @dataclass
    class Block:
        number: str
        name: str
        blocks: list["UnionBlock"] = field(default_factory=list)

        def to_dict(self):
            return {"№": to_number(self.number), "Блок": self.name, "Подблоки": [block.to_dict() for block in self.blocks]}

    @dataclass
    class SubBlock:
        subname: str
        blocks: list["UnionBlock"] = field(default_factory=list)

        def to_dict(self):
            return {"Подназвание": self.subname, "Подблоки": [block.to_dict() for block in self.blocks]}

    UnionBlock = Block | SubBlock

    def parse_text(text: str) -> list[UnionBlock]:
        lines = text.split("\n")
        blocks = []
        current_subblock = None

        for line in lines:
            line = line.strip()
            if line.startswith("КРИТЕРИИ"):
                continue

            if line.startswith("БЛОК"):
                line = line.replace("БЛОК:", "").strip()

            if re.match(r"\d+\.\d+", line):
                match = re.match(r"(\d+)\.(\d+).?\ ?(.*)", line)
                if match:
                    number = match.group(1).strip()
                    sub_number = match.group(2).strip()
                    number = f"{number}.{sub_number}"
                    name = match.group(3).strip()
                    block = Block(number, name)
                    current_subblock.blocks.append(block)
            elif re.match(r"\d+\.", line):
                match = re.match(r"(\d+)\. (.*)", line)
                if match:
                    number = match.group(1).strip()
                    name = match.group(2).strip()
                    block = Block(number, name)
                    blocks.append(block)
                    current_subblock = block
            elif line.strip() != "":
                block = Block("", line)
                blocks.append(block)
                current_subblock = block

        return blocks

    def parse_docx(file_path):
        doc = docx.Document(file_path)
        criteries = []

        for table in doc.tables:
            blocks = [block.to_dict() for block in parse_text(table.rows[0].cells[0].text)]
            blocks_criteries = []
            for row in table.rows[2:-1]:
                number = row.cells[0].text.strip()
                if number.endswith("."):
                    number = number[:-1]
                blocks_criteries.append(
                    {
                        "№": to_number(number),
                        "Критерий": row.cells[1].text.strip(),
                        "Описание критерия": row.cells[2].text.strip(),
                        "Максимальная оценка": to_number(row.cells[3].text.strip().split(" ")[0]),
                    }
                )

            criteries.append({"Блоки": blocks, "Критерии": blocks_criteries})

        for critery in criteries:
            for block in critery["Блоки"]:
                if block["№"] == 0 and len(block["Подблоки"]) > 0:
                    block["№"] = int(str(block["Подблоки"][0]["№"]).split(".", 1)[0])



        return criteries

    if not dst_path:
        dst_path = file_path + ".json"
    
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump({"Критерии": parse_docx(file_path)}, f, indent=4, ensure_ascii=False)
