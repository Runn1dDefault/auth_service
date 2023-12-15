import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from jinja2 import Environment, FileSystemLoader

from config import SMTP_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_PASSWORD, TEMPLATES_DIR


def send_mail_text(email: str, subject: str, message: str):
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, email, msg.as_string())
    server.quit()


def send_mail_html(email: str, subject: str, template_name: str, context: dict[str, Any]):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(template_name)
    html_message = template.render(context)

    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = email
    msg['Subject'] = subject

    html_part = MIMEText(html_message, 'html')
    msg.attach(html_part)

    server.sendmail(SMTP_EMAIL, email, msg.as_string())
    server.quit()


if __name__ == '__main__':
    send_mail_html(
        email="runniddefault@gmail.com",
        subject="Verify your email",
        template_name="restore_code.html",
        context={'subject': "Kaimono", "code": "123456", "warning_text": "Be c"}
    )
