import os
import threading
from django.core.mail import EmailMessage


# @shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()


def send_pw_reset_email(token, user):
    frontend_url = os.getenv('FRONTEND_URL')
    email_body = f"<html>" \
                 f"<head>" \
                 f"</head>" \
                 f"<body>" \
                 f"<p>Hi {user.first_name},</p>" \
                 f"<p>You requested for a password reset on <b>WareHouse</b></p>" \
                 f"<p>Kindly click on the link below to reset your password</p>" \
                 f"<a href=\"{frontend_url}?email={user.email}&token={token}\">Reset password</a>" \
                 f"</body>" \
                 f"</html>"

    payload = {
        'subject': 'Password Reset',
        'html_content': email_body,
        'to_email': user.email
    }
    pw_reset_thread = threading.Thread(
        target=send_email, args=(payload,)
    )
    pw_reset_thread.start()
    return
