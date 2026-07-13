from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class TimedTokenGenerator(PasswordResetTokenGenerator):
    """Like PasswordResetTokenGenerator, but reads its expiry window from a
    project setting instead of the global PASSWORD_RESET_TIMEOUT, so email
    verification and password reset links can expire on different schedules.
    """

    timeout_setting_name = "PASSWORD_RESET_TOKEN_EXPIRY_HOURS"

    def check_token(self, user, token):
        if not (user and token):
            return False

        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(self._make_token_with_timestamp(user, ts, secret), token):
                break
        else:
            return False

        timeout_seconds = getattr(settings, self.timeout_setting_name) * 3600
        if (self._num_seconds(self._now()) - ts) > timeout_seconds:
            return False

        return True


class EmailVerificationTokenGenerator(TimedTokenGenerator):
    """Invalidated once the address has been verified, once the account
    password changes, or after EMAIL_TOKEN_EXPIRY_HOURS - whichever first."""

    timeout_setting_name = "EMAIL_TOKEN_EXPIRY_HOURS"

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{user.is_email_verified}{timestamp}"


class PasswordResetTimedTokenGenerator(TimedTokenGenerator):
    timeout_setting_name = "PASSWORD_RESET_TOKEN_EXPIRY_HOURS"


email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTimedTokenGenerator()
