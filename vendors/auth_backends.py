
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        User = get_user_model()
        if email:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        return super().authenticate(request, username=username, password=password, **kwargs)
