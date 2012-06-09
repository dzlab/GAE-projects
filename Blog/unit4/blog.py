from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import re

""" configuring jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
"""

class User(db.Model):
    username = db.StringProperty(multiline=False)
    password = db.StringProperty(multiline=False)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def isvalid(text_re, text):
    return text_re.match(text)

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
class Blog(webapp.RequestHandler):  
    
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC ")
        template_values = {
            'posts':posts,
        }
        path = os.path.join(os.path.dirname(__file__), 'blog.html')
        self.response.out.write(template.render(path, template_values))

class NewPost(webapp.RequestHandler):  
    def render_front(self, title="", content="", error=""):
        template_values = {
            'title':title,
            'content': content,
            'error' : error,
        }
        path = os.path.join(os.path.dirname(__file__), 'newpost.html')
        self.response.out.write(template.render(path, template_values))
        
    def get(self):
        self.render_front()
        
    def post(self):
        title = self.request.get('subject')
        content = self.request.get('content')
        if title and content:
            p = Post(title= title, content= content)
            p.put()
            id = p.key().id()
            self.redirect("/unit3/blog/"+str(id))
        else:
            error = 'We need both title and content of the post.'
            self.render_front(title, content, error)
    
class PostHandler(webapp.RequestHandler):
    def get(self, post_id):
        #id = int(self.request.path.replace('/unit3/blog/', ''))
        id = int(post_id)
        posts = [Post.get_by_id(id)]
        template_values = {
            'posts':posts,
        }
        path = os.path.join(os.path.dirname(__file__), 'blog.html')
        self.response.out.write(template.render(path, template_values))
        
class SignupHandler(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'signup.html')
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        redirect = True
        in_user = ''
        if not isvalid(USER_RE, username):
            redirect = False
            in_user = 'That\'s not a valid username.'    
        in_pass = ''
        if not isvalid(PASS_RE, password):
            redirect = False
            in_pass = 'That wasn\'t a valid password.'
        in_verify=''
        if password != verify:
            redirect = False
            in_verify = 'Your password didn\'t match.'
        in_email =''
        if email and not isvalid(EMAIL_RE, email):
            redirect = False
            in_email = 'That\'s not a valid email'
        if redirect:
            user = User(username= username, password= password)
            user.put()
            self.response.headers.add_header('Set-Cookie', 'name='+username+'; Path=/')
            self.redirect("/unit4/welcome")
        else:
            template_values = {'invalid_username' :in_user,
                               'invalid_password' :in_pass,
                               'invalid_verified_password' :in_verify,
                               'invalid_email' :in_email
                               }
            path = os.path.join(os.path.dirname(__file__), 'signup.html')
            self.response.out.write(template.render(path, template_values))
            
class WelcomeHandler(webapp.RequestHandler):        
    def get(self):
        name = self.request.cookies.get('name', '')
        
        template_values = {
            'name':name,
        }
        path = os.path.join(os.path.dirname(__file__), 'welcome.html')
        self.response.out.write(template.render(path, template_values))


class LoginHandler(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'login.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        redirect = True
        in_user = ''
        if not isvalid(USER_RE, username):
            redirect = False
            in_user = 'That\'s not a valid username.'    
        in_pass = ''
        if not isvalid(PASS_RE, password):
            redirect = False
            in_pass = 'That wasn\'t a valid password.'

        if redirect:
            self.response.headers.add_header('Set-Cookie', 'name='+username+'; Path=/')
            self.redirect("/unit4/welcome")
        else:
            template_values = {'error':'invalid login'}
            path = os.path.join(os.path.dirname(__file__), 'login.html')
            self.response.out.write(template.render(path, template_values))
"""
        users = db.GqlQuery("SELECT * FROM User")
        user = None
        for u in users:
            if u.username==username and u.password==password:
                found = True
                break
        if user:
"""

class LogoutHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')
        self.redirect("/unit4/signup")

application = webapp.WSGIApplication([('/unit3/blog', Blog),
                                      (r'/unit3/blog/(\d+)', PostHandler),
                                      ('/unit3/blog/newpost', NewPost),
                                      ('/unit4/signup', SignupHandler),
                                      ('/unit4/welcome', WelcomeHandler),
                                      ('/unit4/login', LoginHandler),
                                      ('/unit4/logout', LogoutHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
