#-*- coding: utf-8 -*-

import os.path
import jinja2

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../shorturls_media/templates')
TEMPLATE_PATH = os.path.abspath(TEMPLATE_PATH)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def get_template(relpath):
  return JINJA_ENVIRONMENT.get_template(relpath)