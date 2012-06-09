from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
import re
import logging
import time

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import db


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

CACHE = {}     
queried = 0 
updated = False   
class Blog(webapp.RequestHandler):      
    def get(self):
        global queried
        global updated
        global CACHE
        key = 'top'
        #posts = memcache.get(key)
        #if updated or posts is None:
        if updated or key not in CACHE:
            #before = time.time()
            logging.error("DB Query")
            posts = db.GqlQuery("SELECT * FROM Post "
                                "ORDER BY created DESC ")
            posts = list(posts)
            #memcache.set(key, posts)
            CACHE[key] = posts
            updated = False
            #queried = time.time() - before
            queried = 0            
        else:    
            queried = queried + 1    

        posts = CACHE[key]
        
        template_values = {
            'posts':posts,
            'queried':queried,
        }
        path = os.path.join(os.path.dirname(__file__), 'blog.html')
        self.response.out.write(template.render(path, template_values))

class BlogJson(webapp.RequestHandler):      
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC ")
        jb = '['
        for post in posts:
            month = str(post.created.month)
            day  = str(post.created.day) 
            hour = str(post.created.hour)
            minute = str(post.created.minute)
            second = str(post.created.second)           
            year = str(post.created.year)
            jb += '{"subject": "'+ post.title+'", "content": "'+ post.content+'", "created": "'+month+' '+day+' '+hour+':'+minute+':'+second+' '+ year +'"},'
        jb = jb[:-1] + ']'
        #pyjb = json.loads(jb)    
        #self.response.out.write(pyjb.dumps())
        self.response.out.write(jb)
        self.response.headers.add_header("Content-Type", "application/json")
        
        
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
        global updated
        title = self.request.get('subject')
        content = self.request.get('content')
        if title and content:
            p = Post(title= title, content= content)
            p.put()
            updated = True
            id = p.key().id()
            self.redirect("/unit6/blog/"+str(id))
        else:
            error = 'We need both title and content of the post.'
            self.render_front(title, content, error)

   
class PostHandler(webapp.RequestHandler):
    def get(self, post_id):
        global CACHE
        logging.error(Post.get_by_id(int(post_id)))
        #posts = memcache.get('p'+post_id)
        #if posts is None:
        if post_id not in CACHE: 
            logging.error("DB Query")
            id = int(post_id)
            #posts = [Post.get_by_id(id)]
            CACHE[post_id] = Post.get_by_id(id)            
            #memcache.set('p'+post_id, posts)
            pq = 0
            memcache.set('pq'+post_id, str(pq))     
        else:
            pq = memcache.get('pq'+post_id)
            if pq is not None:
                pq = int(pq) + 1
                memcache.set('pq'+post_id, str(pq)) 
            else:
                pq = 0 
        posts = [CACHE[post_id]]    
        template_values = {
            'posts':posts,
            'queried':pq,
        }
        path = os.path.join(os.path.dirname(__file__), 'blog.html')
        self.response.out.write(template.render(path, template_values))

class PostJsonHandler(webapp.RequestHandler):
    def get(self, post_id):
        #id = int(self.request.path.replace('/unit3/blog/', ''))
        id = int(post_id)
        posts = [Post.get_by_id(id)]
        jb = ''
        for post in posts:
            month = str(post.created.month)
            day  = str(post.created.day) 
            hour = str(post.created.hour)
            minute = str(post.created.minute)
            second = str(post.created.second)           
            year = str(post.created.year)
            jb += '{"subject": "'+ post.title+'", "content": "'+ post.content+'", "created": "'+month+' '+day+' '+hour+':'+minute+':'+second+' '+ year +'"},'
        jb = jb[:-1]
        self.response.out.write(jb)
        self.response.headers.add_header("Content-Type", "application/json")
        
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
            self.redirect("/unit6/welcome")
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
            self.redirect("/unit6/welcome")
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
        self.redirect("/unit6/signup")

class FlushHandler(webapp.RequestHandler):
    def get(self):
        global queried
        global updated
        global CACHE
        memcache.flush_all()
        CACHE.clear()
        queried = 0
        
        self.redirect("/unit6/blog")
        
application = webapp.WSGIApplication([('/unit6/blog', Blog),
                                      ('/unit6/blog.json', BlogJson),
                                      ('/unit6/.json', BlogJson),
                                      (r'/unit6/blog/(\d+)', PostHandler),
                                      (r'/unit6/blog/(\d+)\.json', PostJsonHandler),
                                      ('/unit6/newpost', NewPost),
                                      ('/unit6/signup', SignupHandler),
                                      ('/unit6/welcome', WelcomeHandler),
                                      ('/unit6/', Blog),
                                      ('/unit6', Blog),
                                      #('/unit6/', WelcomeHandler),
                                      #('/unit6', WelcomeHandler),
                                      ('/unit6/login', LoginHandler),
                                      ('/unit6/logout', LogoutHandler),
                                      ('/unit6/flush', FlushHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
