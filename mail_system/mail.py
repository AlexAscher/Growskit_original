import os
import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.datastructures import FileStorage, ImmutableMultiDict

load_dotenv()


EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


def send_email(subject: str, message: str, recipient: str,
               html_message: str = None,
               attachments: list = None, images: list = None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain', 'utf-8'))
    if html_message:
        msg.attach(MIMEText(html_message, 'html', 'utf-8'))

    for attachment in attachments or []:
        part = MIMEApplication(attachment.stream.read(), Name=attachment.filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        msg.attach(part)

    for image in images or []:
        part = MIMEImage(image.stream.read())
        part.add_header('Content-ID', f'<{image.filename}>')
        msg.attach(part)

    if EMAIL_USE_SSL:
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        server.connect(EMAIL_HOST, EMAIL_PORT)
    else:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.connect(EMAIL_HOST, EMAIL_PORT)
        server.starttls()

    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_HOST_USER, recipient, text)
    server.quit()

def validate(form: dict, files: dict[str, FileStorage]):
    clean_data = {}
    required_fields = ['subject', 'message', 'recipient']
    for field in required_fields:
        if field not in form:
            return {}, f'{field} is required'
    
    clean_data = {
        'subject': form['subject'],
        'message': form['message'],
        'recipient': form['recipient']
    }

    if 'html_message' in form:
        clean_data['html_message'] = form['html_message']
    
    attachments = []
    images = []
    for key, file in files.items():
        if key.startswith('attachments'):
            attachments.append(file)
        elif key.startswith('images'):
            images.append(file)

    if len(attachments) > 0:
        clean_data['attachments'] = attachments
    if len(images) > 0:
        clean_data['images'] = images

    return clean_data, ''

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email_view():
    start = time.time()
    if len(request.form.keys()) == 0:
        data: dict = request.get_json()
        request.form = request.form.copy()
        for key, value in data.items():
            request.form.setdefault(key, value)

    clean_data, error_msg = validate(request.form, request.files)
    if error_msg:
        return jsonify({'error': error_msg}), 400

    try:
        send_email(**clean_data)
        print(f"Time taken to send email: {time.time() - start}")
        return jsonify({'message': 'OK'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=8443)
