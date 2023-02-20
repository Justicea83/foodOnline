from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.models import User
from foodOnline import settings


def detect_user(user):
    url = None
    if user.role == 1:
        url = 'vendor-dashboard'
    elif user.role == 2:
        url = 'dashboard'
    elif user.role is None and user.is_superadmin:
        url = '/admin'
    return url


def send_verification_email(request, user: User, subject: str, template_name: str):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(template_name, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMessage(subject, message, from_email, to=[to_email])
    mail.send()