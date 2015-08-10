#-*- coding: utf-8 -*-

from google.appengine.api import users
from shorturls.models import *
from shorturls.template import get_template

import webapp2



class Index(webapp2.RequestHandler):

  def get_template_values(self):
    template_values = {}
    
    user = users.get_current_user()
    if not user:
      self.redirect('/')
    template_values['user'] = user
    
    urls = RedirectTable.get_by_owner(user.email())
    template_values['urls'] = urls

    return template_values

  def get(self):

    template_values = self.get_template_values()

    template = get_template('user.html')
    self.response.write(template.render(template_values))
  
  def post(self):
    
    template_values = self.get_template_values()
    
    POST = self.request.POST
    op = POST['op']

    if op == 'insert':
      
      url = POST['url']
      owner = POST['owner']

      key, _ = RedirectTable.new(url, owner)
      if key != None:
        template_values['result'] = { 'key': key, 'url': url }

    elif op == 'remove':
      
      key = POST['key']
      RedirectTable.delete(key)
      template_values['result'] = { 'key': key, 'url': '-' }

    else:
      # TODO(ghilbut): logging invalid op
      pass

    template = get_template('user.html')
    self.response.write(template.render(template_values))



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
  ('/user', Index),
  ('/user/login', Login),
  ('/user/logout', Logout),
], debug=True)