#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import main.bot as bot


def setup_mysql():
    if os.getenv('USE_LOCAL_DB') == 'True':
        return

    from MySQLdb.connections import Connection
    from MySQLdb.cursors import BaseCursor

    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    db: Connection = None
    cursor: BaseCursor = None

    try:
        db = Connection(host=db_host, user=db_user, passwd=db_password)
        cursor: BaseCursor = db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def automigrate(execute_from_command_line, AUTO_MIGRATE=False):
    if 'runserver' not in sys.argv:
        return

    if not AUTO_MIGRATE:
        return

    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])


def run_mail_system():
    # run mail system as another process
    print('Mail system starting...')
    #os.execl('python3', 'mail_system/mail.py')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growskit.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    from dotenv import load_dotenv

    load_dotenv()

    setup_mysql()
    automigrate(execute_from_command_line, os.getenv('AUTO_MIGRATE') == 'True')

    run_mail_system()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
