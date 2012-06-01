import webapp2
import logging


class UserHandler(webapp2.RequestHandler):

    def admin(self):
        """ Admin interface
        """
        user = users.get_current_user()

        if user:
            if users.is_current_user_admin():
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write('Hello, ' + user.nickname())
            else:
                logging.warning('Admin: someone tried to use admin', user)
                self.redirect('/')
        else:
            self.redirect(users.create_login_url(self.request.uri))


class ErrorHandlers:

    @staticmethod
    def handle_401(request, response, exception):
        logging.warning(exception)
        response.write('And what are you doing?')
        response.set_status(401)

    @staticmethod
    def handle_404(request, response, exception):
        logging.warning(exception)
        response.write('Oops! I could swear this page was here!')
        response.set_status(404)

    @staticmethod
    def handle_500(request, response, exception):
        logging.error(exception)
        response.write('A server error occurred!')
        response.set_status(500)
