#-*- coding: utf-8 -*-

from google.appengine.api import memcache
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
    html = template.render(template_values)
    self.response.write(html)
  
  def post(self):
    POST = self.request.POST
    op = POST['op']
    template_values = {}

    if op == 'insert':
      url = POST['url']
      if url == None or len(url) == 0:
        self.abort(400)
        
      owner = POST['owner']
      tag, _ = RedirectTable.new(url, owner)
      if tag != None:
        template_values['result'] = { 'tag': tag, 'url': url }

    elif op == 'remove':
      tag = POST['tag']
      RedirectTable.delete(tag)

    else:
      # TODO(ghilbut): logging invalid operation
      pass
    
    template_values.update(self.get_template_values())
    template = get_template('user.html')
    html = template.render(template_values)
    self.response.write(html)



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



class TagInfo(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user == None:
      self.abort(404)
    
    tag = self.request.GET['tag']
    tag_info = RedirectTable.get(tag)
    if tag_info == None:
      self.abort(404)

    items = AccessHistory.get_by_tag(tag)

    template_values = { 'user': user, 'tag': tag_info, 'items': items }
    template = get_template('tag_info.html')
    html = template.render(template_values)
    self.response.write(html)



class FlushMemcache(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user == None:
      self.abort(404)
    
    tag = self.request.GET['tag']
    memcache.delete(tag)
    self.response.write('')



app = webapp2.WSGIApplication([
  ('/user', Index),
  ('/user/login', Login),
  ('/user/logout', Logout),
  ('/user/tag/info', TagInfo),
  ('/user/flush/memcache', FlushMemcache),
], debug=True)