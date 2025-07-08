from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six as mi_util

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            mi_util.text_type(user.pk) + mi_util.text_type(timestamp) +
            mi_util.text_type(user.email)
        )

account_activation_token = AccountActivationTokenGenerator()