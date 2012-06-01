import webapp2
import string
from xml.dom.minidom import parseString

from google.appengine.ext.webapp import template
from google.appengine.api import users

from site.utils import admin_required
from blog.models import Article


class BlogHandler(webapp2.RequestHandler):

    def main(self):
        """ Handle request to main page
        """
        articles = Article.all().order('-created')
        self.response.out.write(template.render(
            'blog/templates/index.html', {'articles': articles}))

    def get_article(self, slug):
        """ Get article
        """
        article = Article.get_by_key_name(slug)
        if article:
            self.response.out.write(template.render(
                'blog/templates/article.html', {'article': article}))
        else:
            self.redirect('/')

    @admin_required
    def update_article(self, slug):
        """ Update existing article
        """
        article = Article.get_by_key_name(slug)
        if not article:
            self.redirect('/')
        if not self.request.POST:
            self.response.out.write(template.render('blog/templates/edit.html',
                {'article': article,
                 'title': 'Edit article',
                 'action': webapp2.uri_for('update_article', slug=slug)}))
        else:
            slug = self.request.get('slug')
            article.key_name = slug
            article.title = self.request.get('title')
            article.description = self.request.get('description')
            article.keywords = map(string.strip,
                self.request.get('keywords').split(','))
            article.content = self.request.get('content')
            article.put()
            self.redirect('/' + slug)

    @admin_required
    def create_article(self):
        """ Create new article
        """
        if not self.request.POST:
            self.response.out.write(template.render('blog/templates/edit.html',
                {'article': None,
                 'title': 'New article',
                 'action': webapp2.uri_for('create_article')}))
        else:
            slug = self.request.get('slug')
            article = Article.get_by_key_name(slug)
            if article:
                slug = slug + '_to_change'
            keywords = map(string.strip,
                self.request.get('keywords').split(','))
            article = Article(key_name=slug,
                              title=self.request.get('title'),
                              description=self.request.get('description'),
                              keywords=keywords,
                              content=self.request.get('content'))
            article.put()
            self.redirect('/' + slug)
