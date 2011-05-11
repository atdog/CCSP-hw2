# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from django.utils import simplejson as json
from BeautifulSoup import BeautifulSoup
from dbTable import Dept,Doctor,Link
from google.appengine.ext import db

import urllib2
import re

def fetchHtml(url):
    r = urllib2.Request(url)
    r.add_header('User-Agent', 'Mozilla 5.0')
    page = urllib2.urlopen(r)
    return page


def getTime(url):
    page = fetchHtml(url)
    
    soup = BeautifulSoup(page)
    timeTable= soup.findAll('table',{"id":"DtDataTable"})
    timeList = []
#    for time in timeTable:
    prog = re.compile(r'(\d{3})\.(\d{1,2})\.(\d{1,2})')
    for row in timeTable[0].findAll('tr'):
        if len(row.contents) > 4:
            date = row.contents[4].contents[0].contents[0]
            match = prog.match(date)
            if( match != None):
                time = re.split(" ",row.contents[4].contents[0].contents[2])[1]
                tag = row.contents[2].contents[0].contents
                year = str(int(match.groups(1)[0]) + 1911)
                month = None
                day = None
                if int(match.groups(1)[1]) < 10:
                    month = "0"+match.groups(1)[1] 
                else:
                    month = match.groups(1)[1]
                if int(match.groups(1)[2]) < 10:
                    day = "0" + match.groups(1)[2]
                else:
                    day = match.groups(1)[2]
                if len(tag) > 1:
                    if time == unicode("上午",'utf-8'):
                        timeList.append(year +"-"+month+"-"+day+"-A")
    #                    print match.groups(1)[0]+"-"+match.groups(1)[1]+"-"+match.groups(1)[2]+"-A"
                    elif time == unicode("下午",'utf-8'):
                        timeList.append(year +"-"+month+"-"+day+"-B")
                    else:
                        timeList.append(year +"-"+month+"-"+day+"-C")
    #                    print match.groups(1)[0]+"-"+match.groups(1)[1]+"-"+match.groups(1)[2]+"-B"

    return timeList 
    
        
