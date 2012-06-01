from google.appengine.api import users


def admin_required(method):
    def wrapped(*args, **kwargs):
        user = users.get_current_user()
        if not user and not users.is_current_user_admin():
            logging.warning('Admin: someone tried to use admin method',
                method, user)
            return webapp2.redirect('/')
        else:
            return method(*args, **kwargs)
    return wrapped
