'''
Created on 2011/5/8

@author: atdog
'''
from google.appengine.ext import db

class Dept(db.Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    

class Doctor(db.Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    page = db.StringProperty()

class Link(db.Model):
    doctorId = db.IntegerProperty()
    deptId = db.IntegerProperty()
    
