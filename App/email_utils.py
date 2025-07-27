from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(user):
    """
    Send a confirmation email to the user after registration
    """
    subject = 'Welcome to Enibla Recipe Sharing!'
    message = f'''
    Hello {user.first_name or user.username},

    Thank you for registering on Enibla Recipe Sharing!
    
    Your account has been successfully created. Start sharing and discovering amazing recipes today!
    
    Best regards,
    The Enibla Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
