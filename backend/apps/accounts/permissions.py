from django.contrib.auth import get_user_model

User = get_user_model()


def user_is_author(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == 'author')


def user_can_write_content(user) -> bool:
    return user_is_author(user)
