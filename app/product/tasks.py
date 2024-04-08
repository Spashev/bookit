from core.celery import app
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
import mimetypes


@app.task
def send_email_message(subject: str, message: str, email_from: str, email_to: list):
    send_mail(
        subject,
        message,
        email_from,
        email_to,
        fail_silently=False,
    )
