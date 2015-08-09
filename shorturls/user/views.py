#-*- coding: utf-8 -*-

from google.appengine.api import users
import webapp2

class Login(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url('/'))

class Logout(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      self.redirect(users.create_logout_url('/'))

app = webapp2.WSGIApplication([
  ('/user/login', Login),
  ('/user/logout', Logout),
], debug=True)