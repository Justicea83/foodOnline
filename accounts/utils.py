def detect_user(user):
    url = None
    if user.role == 1:
        url = 'vendor-dashboard'
    elif user.role == 2:
        url = 'dashboard'
    elif user.role is None and user.is_superadmin:
        url = '/admin'
    return url
