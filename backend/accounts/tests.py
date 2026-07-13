from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .tokens import email_verification_token, password_reset_token

User = get_user_model()


class RegisterTests(APITestCase):
    def test_register_creates_user_and_sends_verification_email(self):
        url = reverse("auth-register")
        payload = {
            "email": "new.user@example.com",
            "password": "S3cure-Passw0rd!",
            "password2": "S3cure-Passw0rd!",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        user = User.objects.get(email="new.user@example.com")
        self.assertFalse(user.is_email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].to)

    def test_register_rejects_mismatched_passwords(self):
        url = reverse("auth-register")
        payload = {
            "email": "mismatch@example.com",
            "password": "S3cure-Passw0rd!",
            "password2": "different",
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="mismatch@example.com").exists())

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(email="taken@example.com", password="S3cure-Passw0rd!")
        url = reverse("auth-register")
        payload = {
            "email": "taken@example.com",
            "password": "S3cure-Passw0rd!",
            "password2": "S3cure-Passw0rd!",
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="login@example.com", password="S3cure-Passw0rd!")

    def test_login_with_correct_credentials(self):
        url = reverse("auth-login")
        response = self.client.post(url, {"email": "login@example.com", "password": "S3cure-Passw0rd!"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "login@example.com")

    def test_login_with_wrong_password_fails(self):
        url = reverse("auth-login")
        response = self.client.post(url, {"email": "login@example.com", "password": "wrong"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        login = self.client.post(
            reverse("auth-login"), {"email": "login@example.com", "password": "S3cure-Passw0rd!"}
        )
        access = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "login@example.com")

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            reverse("auth-login"), {"email": "login@example.com", "password": "S3cure-Passw0rd!"}
        )
        access, refresh = login.data["access"], login.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = self.client.post(reverse("auth-logout"), {"refresh": refresh})
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post(reverse("auth-refresh"), {"refresh": refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="verify@example.com", password="S3cure-Passw0rd!")

    def _uid_and_token(self, user):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        return uid, token

    def test_verify_email_with_valid_token(self):
        uid, token = self._uid_and_token(self.user)
        response = self.client.post(reverse("auth-verify-email"), {"uid": uid, "token": token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_with_invalid_token_fails(self):
        uid, _ = self._uid_and_token(self.user)
        response = self.client.post(reverse("auth-verify-email"), {"uid": uid, "token": "bogus-token"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)

    def test_resend_verification_sends_email_for_unverified_user(self):
        response = self.client.post(reverse("auth-resend-verification"), {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_verification_is_silent_for_unknown_email(self):
        response = self.client.post(
            reverse("auth-resend-verification"), {"email": "nobody@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="reset@example.com", password="Old-Passw0rd!")

    def _uid_and_token(self, user):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)
        return uid, token

    def test_password_reset_request_sends_email_for_existing_user(self):
        response = self.client.post(reverse("auth-password-reset"), {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_request_is_silent_for_unknown_email(self):
        response = self.client.post(reverse("auth-password-reset"), {"email": "nobody@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_changes_password(self):
        uid, token = self._uid_and_token(self.user)
        response = self.client.post(
            reverse("auth-password-reset-confirm"),
            {"uid": uid, "token": token, "new_password": "Brand-New-Passw0rd!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        login = self.client.post(
            reverse("auth-login"), {"email": self.user.email, "password": "Brand-New-Passw0rd!"}
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_rejects_reused_token(self):
        uid, token = self._uid_and_token(self.user)
        first = self.client.post(
            reverse("auth-password-reset-confirm"),
            {"uid": uid, "token": token, "new_password": "Brand-New-Passw0rd!"},
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post(
            reverse("auth-password-reset-confirm"),
            {"uid": uid, "token": token, "new_password": "Another-Passw0rd!"},
        )
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)


class UserModelTests(TestCase):
    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="S3cure-Passw0rd!")

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_email_verified)

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="S3cure-Passw0rd!")
