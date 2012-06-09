from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
    
def escape_html(s):
    return cgi.escape(s, quote = True)

def rot13(text):
    crypted = ''
    for i in range(len(text)):
        if text[i].isalpha():
            if text[i].isupper():
                char = chr((ord(text[i])-ord('A') + 13)%26 + ord('A'))
            else:
                char = chr((ord(text[i])-ord('a') + 13)%26 + ord('a'))
            crypted = crypted + char
        else:
            crypted = crypted + text[i]
    return crypted

page = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%(response)s</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
    """
   
class Rot13(webapp.RequestHandler):
    def write_page(self, response=""):
        self.response.out.write(page % {"response": escape_html(response)})    
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_page()

    def post(self):
        user_text = self.request.get('text')
        self.write_page(rot13(user_text))

application = webapp.WSGIApplication([('/unit2/rot13', Rot13)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
