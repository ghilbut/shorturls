# -*- coding:utf-8 -*-

from datetime import datetime
from google.appengine.ext import ndb

import logging
import os
import random
import string


ROOT_EMAIL = 'ghilbut@gmail.com'


class Account(ndb.Model):
  email = ndb.StringProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
  
  @staticmethod
  def get_or_create(email):
    emails = Account.query(Account.email==email).order(-Account.created_at).fetch()
    size = len(emails)
    if size == 0:
      return Account(email=email).put()
    else:
      if size > 1:
        # TODO(ghilbut): logging error case
        pass
      return emails[0].key



class TagSet(ndb.Model):
  begin = ndb.IntegerProperty()
  now = ndb.IntegerProperty()
  end = ndb.IntegerProperty()
  next = ndb.IntegerProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
  
  @staticmethod
  #@ndb.transactional(retries=10)
  def get_next():
    # tags = TagSet.query().order(-TagSet.created_at).fetch(1)
    # TODO(ghilbut): this is temp codes
    
    base = string.ascii_lowercase + string.ascii_uppercase + string.digits
    tag = None
    while tag == None:
      tag = ''.join(random.SystemRandom().choice(base) for _ in range(6))
      if RedirectTable.query(RedirectTable.tag==tag).count() != 0:
        tag = None
    return tag



class RestoredTagSet(ndb.Model):
  tag = ndb.StringProperty()

  @staticmethod
  @ndb.transactional(retries=10)
  def new(account_key, tag):
    RestoredTagSet(parent=account_key, tag=tag).put()

  @staticmethod
  @ndb.transactional(retries=10)
  def get_and_remove(account_key):
    items = RestoredTagSet.query(ancestor=account_key).fetch(1)
    if len(items) == 1:
      item = items[0]
      tag = item.tag
      item.delete()
      return tag
    else:
      return None


class RedirectTable(ndb.Model):
  tag = ndb.StringProperty(indexed=True)
  url = ndb.StringProperty()
  owner = ndb.StringProperty(indexed=True)
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  deleted_at = ndb.DateTimeProperty(indexed=True)

  @staticmethod
  def get(tag):
    items = RedirectTable.query(RedirectTable.tag==tag, RedirectTable.deleted_at==None).fetch()
    if items != None and len(items) == 1:
      return items[0]
    else:
      # TODO(ghilbut): logging error case.
      return None
  
  @staticmethod
  def new(url, owner):
    account_key = Account.get_or_create(ROOT_EMAIL)
    tag = RestoredTagSet.get_and_remove(account_key)
    if tag == None:
      tag = TagSet.get_next()
    if tag == None:
      # TODO(ghilbut): logging error
      return None, 'tag generation is failed.'

    account = Account.get_or_create(owner)
    RedirectTable(parent=account, tag=tag, url=url, owner=owner).put()
    return tag, None
  
  @staticmethod
  def get_by_owner(owner):
    account = Account.get_or_create(owner)
    items = RedirectTable.query(ancestor=account).filter(RedirectTable.owner==owner, RedirectTable.deleted_at==None).fetch()
    return items

  @staticmethod
  def delete(tag):
    item = RedirectTable.get(tag)
    if item != None:
      item.deleted_at = datetime.now()
      item.put()
  
  @staticmethod
  def clear():
    ndb.delete_multi(RedirectTable.query().fetch(keys_only=True))



class AccessHistory(ndb.Model):
  tag = ndb.StringProperty(indexed=True)
  url = ndb.StringProperty(indexed=True)
  access_info = ndb.JsonProperty()
  is_cached = ndb.BooleanProperty()
  execution_time_sec = ndb.FloatProperty(default=0.0)
  created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
  
  @staticmethod
  def record(tag, url, access_info, is_cached):
    return AccessHistory(tag=tag, url=url, access_info=access_info, is_cached=is_cached).put().get()
  
  @staticmethod
  def get_by_tag(tag):
    return AccessHistory.query(AccessHistory.tag==tag).order(-AccessHistory.created_at).fetch()