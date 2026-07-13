from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token, password_reset_token


def _uid_for(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def send_verification_email(user):
    uid = _uid_for(user)
    token = email_verification_token.make_token(user)
    link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"

    send_mail(
        subject="Verify your IssueHub email address",
        message=(
            f"Hi {user.get_short_name()},\n\n"
            f"Please verify your email address by visiting the link below:\n"
            f"{link}\n\n"
            f"This link expires in {settings.EMAIL_TOKEN_EXPIRY_HOURS} hours.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_password_reset_email(user):
    uid = _uid_for(user)
    token = password_reset_token.make_token(user)
    link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

    send_mail(
        subject="Reset your IssueHub password",
        message=(
            f"Hi {user.get_short_name()},\n\n"
            f"You (or someone else) requested a password reset. Visit the "
            f"link below to choose a new password:\n{link}\n\n"
            f"This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS} hours.\n"
            f"If you didn't request this, you can safely ignore this email.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
