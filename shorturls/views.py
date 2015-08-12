#-*- coding: utf-8 -*-

from datetime import datetime
from google.appengine.api import memcache
from google.appengine.api import users
from shorturls.models import RedirectTable, AccessHistory
from shorturls.template import get_template

import webapp2



class Index(webapp2.RequestHandler):
  def get(self):

    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['user'] = user

    template = get_template('index.html')
    self.response.write(template.render(template_values))
    


class Redirect(webapp2.RequestHandler):
  
  @staticmethod
  def get_url(tag):
    # get from memcache first
    is_cached = False
    url = memcache.get(tag)
    if url == None:
      # get from RedirectTable
      item = RedirectTable.get(tag)
      if item != None:
        url = item.url
        # max memcache key size is 250-bytes
        # max memcache value size is 250-Mbytes - key size
        memcache.add(tag, url)
    else:
      is_cached = True
    return url, is_cached

  def get(self):
    
    # check processing time
    now = datetime.now()
    tag = self.request.path[1:]
    url, is_cached = self.get_url(tag)

    if url == None:
      self.abort(404)

    ## get access information
    headers = {}
    for key in self.request.headers.keys():
      headers[key] = self.request.headers[key]
    cookies = {}
    for key in self.request.cookies.keys():
      cookies[key] = self.request.cookies[key]

    access_info = {
        'client': self.request.remote_addr,
        'headers': headers,
        'cookies': cookies
      }

    record = AccessHistory.record(tag, url, access_info, is_cached)
    record.execution_time_sec = (datetime.now() - now).total_seconds()
    record.put()
    return self.redirect(str(url), permanent=True)



app = webapp2.WSGIApplication([
  ('/', Index),
  ('/[a-zA-Z0-9]{6}', Redirect),
], debug=True)