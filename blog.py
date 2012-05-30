import logging
import string
import webapp2

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache


################################### SETTINGS ##################################

blog_author = '0xKirill'
blog_title = '0xKirill::Blog'
blog_description = '0xKirill::Blog about Python, Math, Life'
blog_keywords = '0xKirill, Kirill, Python, Math'
blog_css = '/static/main.css'

google_analitics = ('<script type="text/javascript">'
    'var _gaq = _gaq || [];'
    '_gaq.push(["_setAccount", "UA-32210871-1"]);'
    '_gaq.push(["_trackPageview"]);'
    '(function() {'
        'var ga = document.createElement("script"); '
        'ga.type = "text/javascript"; ga.async = true;'
        'ga.src = ("https:" == document.location.protocol ? "https://ssl" '
        ': "http://www") + ".google-analytics.com/ga.js";'
        'var s = document.getElementsByTagName("script")[0];'
        's.parentNode.insertBefore(ga, s);'
    '})();</script>')

blog_head = (
    '<link rel="stylesheet" href="{}">'
    '<meta name="author" content="{}">'
    '<meta name="description" content="{}">'
    '<meta name="keywords" content="{}">'
    '<title>{}</title>').format(blog_css, blog_author, blog_description,
        blog_keywords, blog_title) + google_analitics
blog_menu = ('<nav><a href="/" class="logo">0xKirill</a>'
                  '<a href="/about">About</a></nav>')
disquse_code = ('<div id="disqus_thread"></div>'
    '<script type="text/javascript">'
    'var disqus_shortname = "kirill";'
    '(function() {'
        'var dsq = document.createElement("script"); '
        'dsq.type = "text/javascript"; dsq.async = true;'
        'dsq.src = "http://" + disqus_shortname + ".disqus.com/embed.js";'
        '(document.getElementsByTagName("head")[0] '
        '|| document.getElementsByTagName("body")[0]).appendChild(dsq);'
    '})();'
    '</script>'
    '<noscript></noscript>'
    '<a href="http://disqus.com" class="dsq-brlink">comments powered by '
    '<span class="logo-disqus">Disqus</span></a>')


#################################### UTILS ####################################

def tag(tagname, content='', **attributes):
    empty_tags = ('br', 'hr', 'meta', 'link', 'base', 'img', 'embed', 'param',
        'area', 'col', 'input')
    result = '<' + tagname
    for attr in attributes:
        if attr == 'htmlclass':
            result += ' class="' + str(attributes[attr]) + '"'
        else:
            result += ' ' + str(attr) + '="' + str(attributes[attr]) + '"'
    result += '>'
    if tagname in empty_tags:
        return result
    if content:
        result += content
    result += '</' + tagname + '>'
    return result


def formfield(tagname, content='', **attributes):
    return attributes['name'].capitalize() + ': ' + tag(tagname,
        content, **attributes)


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


################################## MODELS #####################################

class Article(db.Model):
    """ Article model
    """
    created = db.DateTimeProperty(auto_now_add=True)
    edited = db.DateTimeProperty(auto_now=True)
    title = db.StringProperty()
    description = db.StringProperty(multiline=True)
    keywords = db.StringListProperty()
    content = db.TextProperty(required=True)


################################### HANDLERS ##################################

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


class BlogHandler(webapp2.RequestHandler):

    def main(self):
        """ Handle request to main page
        """
        blog_cached = memcache.get("blog")
        if blog_cached is not None:
            self.response.out.write(blog_cached)
        else:
            articles = ''
            all_articles = Article.all().order('-created')
            for article in all_articles:
                created = article.created.strftime('%Y-%m-%d')
                time = tag('div', htmlclass='time', content=created)
                link = tag('a', href=webapp2.uri_for('get_article',
                    slug=article.key().name()), content=article.title)
                title = tag('h1', htmlclass='title', content=link)
                description = tag('div', htmlclass='description',
                    content=article.description)
                articles += tag('article', time + title + description)
            blog = tag('section', htmlclass='blog', content=articles)
            head = tag('head', content=blog_head)
            body = tag('body', content=blog_menu + blog)
            html = '<!doctype html>' + tag('html', content=head + body)
            memcache.add(key="blog", value=html)
            self.response.out.write(html)

    def get_article(self, slug):
        """ Get article
        """
        article_cached = memcache.get(slug)
        if article_cached is not None:
            self.response.out.write(article_cached)
        else:
            a_key = db.Key.from_path('Article', slug)
            article = Article.get(a_key)
            if article:
                created = article.created.strftime('%Y-%m-%d')
                content = tag('div', htmlclass='time', content=created)
                content += tag('div', htmlclass='title', content=article.title)
                content += tag('div', htmlclass='text',
                    content=article.content + disquse_code)
                a_body = tag('article', content=content)
                section = tag('section', htmlclass="article", content=a_body)
                body = tag('body', content=blog_menu + section)

                a_head = '<link rel="stylesheet" href="{}">'.format(blog_css)
                a_head += '<meta name="author" content="{}">'.format(
                    blog_author)
                a_head += '<meta name="description" content="{}">'.format(
                    article.description)
                a_head += '<meta name="keywords" content="{}">'.format(
                    ', '.join(map(string.strip, article.keywords)))
                head = tag('head', content=a_head + google_analitics)

                html = '<!doctype html>' + tag('html', content=head + body)
                memcache.add(key=slug, value=html)
                self.response.out.write(html)
            else:
                self.redirect('/')

    @admin_required
    def update_article(self, slug):
        """ Update existing article
        """
        a_key = db.Key.from_path('Article', slug)
        article = Article.get(a_key)
        if not article:
            self.redirect('/')
        if not self.request.POST:
            formfields = formfield('input', type='text', name='slug',
                value=slug)
            formfields += formfield('input', type='text', name='title',
                value=article.title)
            formfields += formfield('textarea', name='description', rows=3,
                cols=60, content=article.description)
            formfields += formfield('input', type='text', name='keywords',
                value=', '.join(map(string.strip, article.keywords)))
            formfields += formfield('textarea', name='content', rows=3,
                cols=100, content=article.content)
            formfields += tag('input', type='submit', value='Submit post')
            postform = tag('form', action=webapp2.uri_for('update_article',
                slug=slug), method='POST', content=formfields)
            title = tag('title', content='Add new article')
            head = tag('head', content=title)
            body = tag('body', content=blog_menu + postform)
            html = '<!doctype html>' + tag('html', content=head + body)
            self.response.out.write(html)
        else:
            slug = self.request.get('slug')
            article.key_name = slug
            article.title = self.request.get('title')
            article.description = self.request.get('description')
            article.keywords = map(string.strip,
                self.request.get('keywords').split(','))
            article.content = self.request.get('content')
            article.put()
            memcache.delete(key="blog")
            memcache.delete(key=slug)
            self.redirect('/' + slug)

    @admin_required
    def create_article(self):
        """ Create new article
        """
        if not self.request.POST:
            formfields = formfield('input', type='text', name='slug')
            formfields += formfield('input', type='text', name='title')
            formfields += formfield('textarea', name='description', rows=3,
                cols=60)
            formfields += formfield('input', type='text', name='keywords')
            formfields += formfield('textarea', name='content', rows=3,
                cols=100)
            formfields += tag('input', type='submit', value='Submit post')
            postform = tag('form', action=webapp2.uri_for('create_article'),
                method='POST', content=formfields)
            title = tag('title', content='Add new article')
            head = tag('head', content=title)
            body = tag('body', content=blog_menu + postform)
            html = '<!doctype html>' + tag('html', content=head + body)
            self.response.out.write(html)
        else:
            slug = self.request.get('slug')
            a_key = db.Key.from_path('Article', slug)
            article = Article.get(a_key)
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
            memcache.delete(key="blog")
            self.redirect('/' + slug)


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


################################## ROUTES #####################################

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
