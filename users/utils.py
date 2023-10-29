def check_blocked(user, requested_by_user):
    blocked_users = user.user_settings.blocked_users.all()
    return requested_by_user in blocked_users
