from google.appengine.ext import webapp

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

class Signup(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../www/signup.html')
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
            self.redirect("/login")
        else:
            template_values = {'invalid_username' :in_user,
                               'invalid_password' :in_pass,
                               'invalid_verified_password' :in_verify,
                               'invalid_email' :in_email
                               }
            path = os.path.join(os.path.dirname(__file__), '../www/signup.html')
            self.response.out.write(template.render(path, template_values))

class Login(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../www/login.html')
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
            self.redirect("/welcome")
        else:
            template_values = {'error':'invalid login'}
            path = os.path.join(os.path.dirname(__file__), '../www/login.html')
            self.response.out.write(template.render(path, template_values))

class Logout(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')
        self.redirect("../www/signup")
