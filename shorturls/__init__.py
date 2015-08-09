#-*- coding: utf-8 -*-

from google.appengine.api import users

import os.path
import jinja2
import webapp2

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../shorturls_media/templates')
TEMPLATE_PATH = os.path.abspath(TEMPLATE_PATH) 

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Index(webapp2.RequestHandler):
  def get(self):
    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['user'] = user

    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
  ('/', Index),
], debug=True)