from google.appengine.ext import webapp

import os
import re
import logging
import time

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import db

class Page(db.Model):
    path    = db.StringProperty(multiline=False)
    content = db.StringProperty(multiline=True)
    edited  = db.DateTimeProperty(auto_now_add = True)
    
class EditPage(webapp.RequestHandler):
    def get(self, path):
        user = self.request.cookies.get('name', '')
        if user == "":
            self.redirect('/login')
        #login = 'login'
        #signup = 'signup'
        login = user
        signup = 'logout'    
        content = ""
        pages = db.GqlQuery("SELECT * FROM Page")
        for page in pages:
            if page.path==path:
                content = page.content
        template_values = {
                           "login": login,
                           "signup": signup,
                           "action": "/_edit"+path,
                           "content": content
                           }
        path = os.path.join(os.path.dirname(__file__), '../www/newpage.html')
        self.response.out.write(template.render(path, template_values))
    
    def post(self, path):
        content = self.request.get('content')
        page = Page(path= path, content= content)
        page.put()
        self.redirect(path)
            
            
class WikiPage(webapp.RequestHandler):
    def get(self, path):
        pages = db.GqlQuery("SELECT * FROM Page")
        found = False
        content = ""
        for page in pages:
            if page.path==path:
                found = True
                content = page.content
        if not found:
            self.redirect("/_edit"+path)
        else:
            template_values = {
                        "path": path,
                        "content": content
                           }
            path = os.path.join(os.path.dirname(__file__), '../www/page.html')
            self.response.out.write(template.render(path, template_values))
            
class HistoryPage(webapp.RequestHandler):
    def get(self, path):
        user = self.request.cookies.get('name', '')
        if user == "":
            login = "login"
            signup = 'signup'  
        else:
            login = user
            signup = 'logout'  
          
        history = db.GqlQuery("SELECT * FROM Page "
                              "ORDER BY edited DESC ")
        history = list(history)
        """
        for update in history:
            if path != update.path:
                history.remove(update)
        """
        template_values = {
                        "login": login,
                        "signup": signup,
                        "path": path,
                        "history": history
                           }
        path = os.path.join(os.path.dirname(__file__), '../www/history.html')
        self.response.out.write(template.render(path, template_values))
                