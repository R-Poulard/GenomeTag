from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class EmailOrUsernameModelBackend(object):
    """
    This is a ModelBackend that allows authentication with either a username or an email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password):
                    return user
            except CustomUser.DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
