from apps.accounts.permissions import user_is_author


def can_moderate_comments(user, post) -> bool:
    return bool(
        user and user.is_authenticated
        and (user.is_staff or (user_is_author(user) and post.author_id == user.pk))
    )
