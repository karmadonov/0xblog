import logging
import string
import webapp2

from google.appengine.api import users

from blog.handlers import BlogHandler
from site.handlers import UserHandler, ErrorHandlers


urlconf = [
    webapp2.Route(r'/0xadmin',
        UserHandler, handler_method='admin', name='admin'),
    webapp2.Route(r'/', BlogHandler, handler_method='main'),
    webapp2.Route(r'/0xadmin/new',
        BlogHandler, handler_method='create_article', name='create_article'),
    webapp2.Route(r'/0xadmin/update/<slug>',
        BlogHandler, handler_method='update_article', name='update_article'),
    webapp2.Route(r'/<slug>',
        BlogHandler, handler_method='get_article', name='get_article')]

app = webapp2.WSGIApplication(urlconf, debug=True)
app.error_handlers[401] = ErrorHandlers.handle_401
app.error_handlers[404] = ErrorHandlers.handle_404
app.error_handlers[500] = ErrorHandlers.handle_500
