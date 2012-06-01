from google.appengine.ext import db


class Article(db.Model):
    """ Article model
    """
    created = db.DateTimeProperty(auto_now_add=True)
    edited = db.DateTimeProperty(auto_now=True)
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)
    keywords = db.StringListProperty()
    content = db.TextProperty(required=True)
