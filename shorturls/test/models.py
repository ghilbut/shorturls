# -*- coding:utf-8 -*-

from google.appengine.ext import ndb

import logging
import os
import MySQLdb
import string



# for 1st test
class TestRDBStringKey():
  
  @staticmethod
  def connect():
    env = os.getenv('SERVER_SOFTWARE')
    if (env and env.startswith('Google App Engine/')):
      return MySQLdb.connect(unix_socket='/cloudsql/shorturls-1032:shorturls-rdb', db='shorturls', user='root', charset='utf8')
    else:
      return None
    
  @staticmethod
  def all():
    rdb = TestRDBStringKey.connect()
    if rdb == None:
      return

    cursor = rdb.cursor()
    cursor.execute('SELECT * FROM `test_string_key`')
    rows = cursor.fetchall()
    return [ { 'key': row['key'], 'url': row['url'] } for row in rows ]

  @staticmethod
  def get(cursor, key):
    cursor.execute("SELECT `url` FROM `test_string_key` WHERE `key`='%s'" % key)
    url = cursor.fetchone()[0]
    #cursor.execute('SELECT * FROM `test_string_key`')
    #url = cursor.fetchall()[0]['url']
    return { 'key': key, 'url': url }

  @staticmethod
  def set(cursor, key, url):
    cursor.execute("INSERT INTO test_string_key (`key`, `url`) VALUES ('%s', '%s')" % (key, url))
  
  @staticmethod
  def clear():
    rdb = TestRDBStringKey.connect()
    if rdb == None:
      return
    cursor = rdb.cursor()
    if cursor == None:
      return

    cursor.execute('DROP TABLE IF EXISTS test_string_key')
    cursor.execute('CREATE TABLE test_string_key ( `id` INT PRIMARY KEY AUTO_INCREMENT, `key` VARCHAR(6), `url` VARCHAR(250) )')



# for 2nd test
# for 3rd test  
class TestStringKey(ndb.Model):
  key = ndb.StringProperty()
  url = ndb.StringProperty()
  
  @staticmethod
  def all():
    return TestStringKey.query().fetch()

  @staticmethod
  def get(key):
    qry = TestStringKey.query(TestStringKey.key == key)
    r = qry.fetch()
    return r[0]

  @staticmethod
  def remove(key):
    key = ndb.Key(TestStringKey, key)
    key.delete()
  
  @staticmethod
  def clear():
    ndb.delete_multi(TestStringKey.query().fetch(keys_only=True))



# for 2nd test
# for 3rd test
class TestIntegerKey(ndb.Model):
  key = ndb.IntegerProperty()
  url = ndb.StringProperty()
  
  @staticmethod
  def all():
    return TestIntegerKey.query().fetch()
  
  @staticmethod
  def get(key):
    qry = TestIntegerKey.query(TestIntegerKey.key == key)
    r = qry.fetch()
    return r[0]

  @staticmethod
  def remove(key):
    key = ndb.Key(TestIntegerKey, key)
    key.delete()

  @staticmethod
  def clear():
    ndb.delete_multi(TestIntegerKey.query().fetch(keys_only=True))



# for 4th test    
class TestUnusedKeySet(ndb.Model):
  key = ndb.StringProperty()
  
  @staticmethod
  def clear():
    ndb.delete_multi(TestUnusedKeySet.query().fetch(keys_only=True))



# test history
class TestResult(ndb.Model):
  type = ndb.StringProperty()
  test_count = ndb.IntegerProperty()
  diff = ndb.StringProperty()
  valid = ndb.BooleanProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  
  @staticmethod
  def all():
    return TestResult.query().fetch()