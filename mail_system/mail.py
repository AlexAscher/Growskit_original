import cgi
import json
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv()

# Configuration for the mail server
MAIL_HOST = os.environ.get('MAIL_HOST')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
MAIL_HOST_USERNAME = os.environ.get('MAIL_HOST_USERNAME')
MAIL_HOST_PASSWORD = os.environ.get('MAIL_HOST_PASSWORD')

def send_email(title: str, message: str, sender: str, receiver: str,
               html_message: str = None,
               attachments: list[cgi.FieldStorage] = None, images: list[cgi.FieldStorage] = None):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = title

    msg.attach(MIMEText(message, 'plain'))
    if html_message:
        msg.attach(MIMEText(html_message, 'html'))

    for attachment in attachments or []:
        part = MIMEApplication(attachment.file.read(), Name=attachment.filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        msg.attach(part)

    for image in images or []:
        part = MIMEImage(image.file.read())
        part.add_header('Content-ID', f'<{image.filename}>')
        msg.attach(part)

    print(msg.as_string())
    return

    if MAIL_USE_SSL:
        server = smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT)
    else:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
        server.starttls()

    server.login(MAIL_HOST_USERNAME, MAIL_HOST_PASSWORD)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()


class RequestHandler(BaseHTTPRequestHandler):
    clean_data: dict

    
    def _get_files(self, form: cgi.FieldStorage, field_name: str):
        files: list[cgi.FieldStorage] = []
        for key in form.keys():
            if key.startswith(field_name):
                file = form[key]
                if isinstance(file, cgi.FieldStorage):
                    files.append(file)
        return files

    def _do(self, status: int, headers: list[tuple[str, str]], body: bytes):
        self.send_response(status)
        for header in headers:
            self.send_header(header[0], header[1])

        self.end_headers()
        self.wfile.write(body.encode('utf-8'))
    
    def _validate(self, form: cgi.FieldStorage) -> tuple[bool, str]:
        for key in ['title', 'message', 'sender', 'receiver']:
            if form.getvalue(key) is None:
                return False, f'{key} is missing'
        
        self.clean_data = {
            'title': form['title'],
            'message': form['message'],
            'sender': form['sender'],
            'receiver': form['receiver'],
        }

        html = form.getvalue('html_message')
        if html is not None:
            self.clean_data['html_message'] = html

        for key in ['attachments', 'images']:
            files = self._get_files(form, key)
            self.clean_data[key] = files
        
        return True, ''

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        form = cgi.FieldStorage(fp=body, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

        is_valid, message = self._validate(form)
        if not is_valid:
            self._do(400, [('Content-Type', 'application/json')], json.dumps({'error': message}))
            return

        try:
            send_email(**self.clean_data)
            self._do(200, [('Content-type', 'application/json')], json.dumps({'message': 'Email sent successfully'}))
        except Exception as e:
            self._do(500, [('Content-type', 'application/json')], json.dumps({'error': str(e)}))

def run_server():
    server_address = ('', 8443)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print('Mail service running at http://localhost:8443/')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
