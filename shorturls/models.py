# -*- coding:utf-8 -*-

from datetime import datetime
from google.appengine.ext import ndb

import logging
import os
import random
import string


class KeySet(ndb.Model):
  begin = ndb.IntegerProperty()
  now = ndb.IntegerProperty()
  end = ndb.IntegerProperty()
  next = ndb.IntegerProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
  
  @staticmethod
  #@ndb.transactional(retries=10)
  def get_next():
    # keys = KeySet.query().order(-KeySet.created_at).fetch(1)
    # TODO(ghilbut): this is temp codes
    
    base = string.ascii_lowercase + string.ascii_uppercase + string.digits
    key = None
    while key == None:
      key = ''.join(random.SystemRandom().choice(base) for _ in range(6))
      if RedirectTable.get(key) != None:
        key = None
    return key



class RestoredKeySet(ndb.Model):
  key = ndb.StringProperty()
  
  @staticmethod
  #@ndb.transactional(retries=10)
  def get_and_remove():
    keys = RestoredKeySet.query().fetch(1)
    if len(keys) == 1:
      return keys[0]
    else:
      return None


class RedirectTable(ndb.Model):
  key = ndb.StringProperty(indexed=True)
  url = ndb.StringProperty()
  owner = ndb.StringProperty(indexed=True)
  used_count = ndb.IntegerProperty(default=0)
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)
  deleted_at = ndb.DateTimeProperty(indexed=True)

  @staticmethod
  def get(key):
    items = RedirectTable.query(RedirectTable.key==key, RedirectTable.deleted_at==None).fetch()
    if items != None and len(items) == 1:
      return items[0]
    else:
      # TODO(ghilbut): logging error case.
      return None
  
  @staticmethod
  def new(url, owner):
    key = RestoredKeySet.get_and_remove()
    if key == None:
      key = KeySet.get_next()
    if key == None:
      # TODO(ghilbut): logging error
      return None, 'key generation is failed.'

    RedirectTable(key=key, url=url, owner=owner).put()
    return key, None
  
  @staticmethod
  def get_by_owner(owner):
    items = RedirectTable.query(RedirectTable.owner==owner, RedirectTable.deleted_at==None).fetch()
    return items

  @staticmethod
  #@ndb.transactional(retries=10)
  def increase_used_count(key):
    item = RedirectTable.get(key)
    if item != None:
      item.used_count += 1
      item.put()
  
  @staticmethod
  def delete(key):
    item = RedirectTable.get(key)
    if item != None:
      item.deleted_at = datetime.now()
      item.put()
  
  @staticmethod
  def clear():
    ndb.delete_multi(RedirectTable.query().fetch(keys_only=True))



class AccessHistory(ndb.Model):
  key = ndb.StringProperty(indexed=True)
  url = ndb.StringProperty(indexed=True)
  access_info = ndb.JsonProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  
  @staticmethod
  def record(key, url, access_info):
    AccessHistory(key=key, url=url, access_info=access_info).put()