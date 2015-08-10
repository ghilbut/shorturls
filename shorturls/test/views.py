#-*- coding: utf-8 -*-
from datetime import datetime
from sets import Set

from google.appengine.api import memcache
from google.appengine.api import users

from shorturls.template import get_template
from shorturls.test.models import *

import random
import string
import webapp2



def make_string_keys(max):
  r = Set([])
  base = string.ascii_lowercase + string.ascii_uppercase + string.digits
  while len(r) < max:
    key = ''.join(random.SystemRandom().choice(base) for _ in range(6))
    r.add(key)
  return list(r)

def string_key_to_long_key(key):
  r = 0L
  for c in key:
    r = r << 8 | ord(c)
  return r



def test_rdb_vs_ndb(total_test_count):
  
  skeys = [item.key for item in TestStringKey.all()]
  
  idxs = []
  target = range(len(skeys))
  for _ in range(total_test_count):
    idx = random.SystemRandom().choice(target)
    idxs.append(idx)

  # test rdb
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    rdb = TestRDBStringKey.connect()
    cursor = rdb.cursor()
    assert key == TestRDBStringKey.get(cursor, key)['key']
    rdb.close()
  t0 = datetime.now() - now
  
  # test ndb
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    assert key == TestStringKey.get(key).key
  t1 = datetime.now() - now
  
  # save result
  valid = t0 > t1
  type = 'test_rdb_vs_ndb'
  if valid:
    diff = str(t0 - t1)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
  else:
    diff = '- ' + str(t1 - t0)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
  
  return str(t0 - t1)



def test_string_key_vs_integer_key(total_test_count):
  
  skeys = [item.key for item in TestStringKey.all()]
  lkeys = Set([item.key for item in TestIntegerKey.all()])
  assert len(skeys) == len(lkeys)

  for skey in skeys:
    assert string_key_to_long_key(skey) in lkeys

  idxs = []
  target = range(len(skeys))
  for _ in range(total_test_count):
    idx = random.SystemRandom().choice(target)
    idxs.append(idx)
  
  
  # test get from TestStringKey
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    assert key == TestStringKey.get(key).key
  t0 = datetime.now() - now
  
  # test get from TestIntegerKey
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    key = string_key_to_long_key(key)
    assert key == TestIntegerKey.get(key).key
  t1 = datetime.now() - now
  
  # save result
  valid = t0 > t1
  type = 'test_string_key_vs_integer_key'
  if valid:
    diff = str(t0 - t1)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
  else:
    diff = '- ' + str(t1 - t0)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
  
  return str(t0 - t1)



def test_direct_get_vs_memcache(total_test_count):
  # https://cloud.google.com/appengine/docs/python/memcache/
  
  memcache.flush_all()

  skeys = []
  for item in TestStringKey.all():
    skey = item.key
    memcache.add(skey, item.url)
    skeys.append(skey)
  
  idxs = []
  target = range(len(skeys))
  for _ in range(total_test_count):
    idx = random.SystemRandom().choice(target)
    idxs.append(idx)
  
  # test get from TestStringKey
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    assert key == TestStringKey.get(key).key
  t0 = datetime.now() - now
  
  # test get from memcache
  now = datetime.now()
  for idx in idxs:
    key = skeys[idx]
    url = memcache.get(key)
    if url == None:
      assert key == TestStringKey.get(key).key
  t1 = datetime.now() - now
  
  # save result
  valid = t0 > t1
  type = 'test_direct_get_vs_memcache'
  if valid:
    diff = str(t0 - t1)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
  else:
    diff = '- ' + str(t1 - t0)
    TestResult(type=type, test_count=total_test_count, diff=diff, valid=valid).put()
    
  return str(t0 - t1)


class Test(webapp2.RequestHandler):
  def get(self):
    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['user'] = user

    #r0 = TestResult.query(TestResult.type=='test_rdb_vs_ndb').order(-TestResult.created_at).fetch()
    #template_values['r0'] = { 'name': 'test_rdb_vs_ndb', 'results': r0 }
    r1 = TestResult.query(TestResult.type=='test_string_key_vs_integer_key').order(-TestResult.created_at).fetch()
    r2 = TestResult.query(TestResult.type=='test_direct_get_vs_memcache').order(-TestResult.created_at).fetch()

    template_values['results'] = [
        { 'name': 'test_string_key_vs_integer_key', 'results': r1 },
        { 'name': 'test_direct_get_vs_memcache', 'results': r2 }
      ]
    
    template = get_template('test.html')
    self.response.write(template.render(template_values))
    



class TestResetData(webapp2.RequestHandler):
  def get(self):

    user = users.get_current_user()
    if user:

      TestRDBStringKey.clear()
      rdb = TestRDBStringKey.connect()
      if rdb != None:
        cursor = rdb.cursor()
      else:
        cursor = None

      TestStringKey.clear()
      TestIntegerKey.clear()
      
      kMaxKeyCount = 100
      string_key_list = make_string_keys(kMaxKeyCount)

      # init TestStringKey table
      for skey in string_key_list:
        ikey = string_key_to_long_key(skey)
        value = 'url:' + skey
        
        if cursor != None:
          TestRDBStringKey.set(cursor, skey, value)
          rdb.commit()

        TestStringKey(key=skey, url=value).put()
        TestIntegerKey(key=ikey, url=value).put()

    self.redirect('/test')



class TestStart(webapp2.RequestHandler):
  def get(self):
    
    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['user'] = user
      
      kTotalTestCount = 1000
      #template_values['test_rdb_vs_ndb'] = test_rdb_vs_ndb(kTotalTestCount)
      template_values['test_string_key_vs_integer_key'] = test_string_key_vs_integer_key(kTotalTestCount)
      template_values['test_direct_get_vs_memcache'] = test_direct_get_vs_memcache(kTotalTestCount)

      #template = get_template('test.html')
      #self.response.write(template.render(template_values))
      self.redirect('/test')
    else:
      self.redirect(users.create_login_url('/test'))

    

class TestCron(webapp2.RequestHandler):
  def get(self):
    kTotalTestCount = 10000
    #test_rdb_vs_ndb(kTotalTestCount)
    test_string_key_vs_integer_key(kTotalTestCount)
    test_direct_get_vs_memcache(kTotalTestCount)
    self.response.headers.add('X-Appengine-Cron', 'true')
    self.response.write("")



app = webapp2.WSGIApplication([
  ('/test', Test),
  ('/test/reset/data', TestResetData),
  ('/test/start', TestStart),
  ('/test/cron', TestCron),
], debug=True)