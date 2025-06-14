from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(user):
    subject = 'Welcome to Enibla!'
    message = f'Hi {user.username}, thanks for registering.'
    recipient_list = [user.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
