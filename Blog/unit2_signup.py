from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
import re
    
def escape_html(s):
    return cgi.escape(s, quote = True)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def isvalid(text_re, text):
    return text_re.match(text)

page = """
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="">
          </td>
          <td class="error">
            %(invalid_username)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">
            %(invalid_password)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
            %(invalid_verified_password)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="">
          </td>
          <td class="error">
            %(invalid_email)s
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
    """
welcome_page = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Signup</title>
  </head>

  <body>
    <h2>Welcome, %(username)s!</h2>
  </body>
</html>
    """

class Signup(webapp.RequestHandler):
    def write_page(self, invalid_username="", invalid_password="", invalid_verified_password="", invalid_email=""):
        self.response.out.write(page % {"invalid_username": invalid_username,
                                        "invalid_password": invalid_password,
                                        "invalid_verified_password": invalid_verified_password,
                                        "invalid_email": invalid_email})    
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_page()

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
            self.redirect("/welcome?username="+username)
        else:
            self.write_page(in_user, in_pass, in_verify, in_email)

class Welcome(webapp.RequestHandler):
    def write_page(self, username=""):
        self.response.out.write(welcome_page % {"username": username})    
        
    def get(self):
        username = self.request.get('username')
        self.response.headers['Content-Type'] = 'text/html'
        self.write_page(username)
    
application = webapp.WSGIApplication([('/unit2/signup', Signup),
                                      ('/unit2/welcome', Welcome)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
