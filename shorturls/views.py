#-*- coding: utf-8 -*-

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
  def get(self):

    key = self.request.path[1:]
    
    # get from memcache first
    url = memcache.get(key)
    
    if url == None:
      # get from RedirectTable
      item = RedirectTable.get(key)
      
      if item != None:
        url = item.url
      
        # max memcache value length is 250  
        if len(url) <= 250:
          memcache.add(key, url)
    
    if url == None:
      self.abort(404)

    ## get access information
    access_info = {}

    RedirectTable.increase_used_count(key)
    AccessHistory.record(key, url, access_info)
    return self.redirect(str(url), permanent=True)



app = webapp2.WSGIApplication([
  ('/', Index),
  ('/[a-zA-Z0-9]{6}', Redirect),
], debug=True)