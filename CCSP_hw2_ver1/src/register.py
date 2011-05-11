# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from BeautifulSoup import BeautifulSoup
from google.appengine.ext import db
import urllib2
import urllib
import re

def fetchHtml(url):
    r = urllib2.Request(url)
    r.add_header('User-Agent', 'Mozilla 5.0')
    page = urllib2.urlopen(r)
    return page

def getRegisterPage(url, time):
    page = fetchHtml(url)
    soup = BeautifulSoup(page)
    match = re.match("(\d{4})-(\d{2})-(\d{2})-(.)", time)
    year = str(int(match.groups(1)[0]) - 1911)
    month = str(int(match.groups(1)[1]))
    day = str(int(match.groups(1)[2]))
    if match.groups(1)[3] == "A":
        clock = unicode("上午", 'utf-8')
    elif match.groups(1)[3] == "B":
        clock = unicode("下午", 'utf-8')
    else:
        clock = unicode("晚上", 'utf-8')
    timeTable = soup.findAll('table', {"id":"DtDataTable"})
    registerPage = None
    for row in timeTable[0].findAll('tr'):
        if len(row.contents) > 4:
            match = re.match(year + "\." + month + "\." + day, row.contents[4].contents[0].contents[0])
            if match == None:
                continue
            webTime = re.split(" ", row.contents[4].contents[0].contents[2])[1]
            if webTime != clock:
                continue
            if len(row.contents[2].contents[0].contents) > 1:
                registerPage = row.contents[2].a['href']

    return registerPage

def register(registerUrl, id, birthday):
    match = re.match("(\d{4})-(\d{2})-(\d{2})", birthday)
    birthYear = match.groups(1)[0]
    birthMonth = match.groups(1)[1]
    birthDay = match.groups(1)[2]
    # First request without data
    page = fetchHtml(registerUrl)
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    
    postValue = {
'scrollLeft':'0',                                                                                                   
'scrollTop':'0',
'__EVENTTARGET':'radInputNum$1',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE':viewstate,
'__EVENTVALIDATION':eventvalidation,
'radInputNum':'1',
'ddlBirthYear':'1961',
'ddlBirthMonth':'',
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(registerUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', registerUrl)
    page = urllib2.urlopen(r)
    # second request with year
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    postValue = {
'scrollLeft':'0',                                                                                                   
'scrollTop':'0',
'__EVENTTARGET':'ddlBirthYear',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE':viewstate,
'__EVENTVALIDATION':eventvalidation,
'radInputNum':'1',
'txtIdno':id,
'ddlBirthYear':birthYear,
'ddlBirthMonth':'',
    }
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(registerUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', registerUrl)
    page = urllib2.urlopen(r)
    # Third request with month
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    postValue = {
'scrollLeft':'0',                                                                                                   
'scrollTop':'0',
'__EVENTTARGET':'ddlBirthMonth',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE':viewstate,
'__EVENTVALIDATION':eventvalidation,
'radInputNum':'1',
'txtIdno':id,
'ddlBirthYear':birthYear,
'ddlBirthMonth':birthMonth,
    }
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(registerUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', registerUrl)
    page = urllib2.urlopen(r)
    # submit register form
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    postValue = {
'scrollLeft':'0',                                                                                                   
'scrollTop':'0',
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE':viewstate,
'__EVENTVALIDATION':eventvalidation,
'radInputNum':'1',
'txtIdno':id,
'ddlBirthYear':birthYear,
'ddlBirthMonth':birthMonth,
'ddlBirthDay':birthDay,
'btnOK':'確定',
    }
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(registerUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', registerUrl)
    page = urllib2.urlopen(r)
    return page.read()
#    return eventvalidation
    
class MainPage(webapp.RequestHandler):
    def post(self):
        doctorId = self.request.get('doctor')
        time = self.request.get('time')
        id = self.request.get('id')
        birthday = self.request.get('birthday')
        doctor = db.GqlQuery("select * from Doctor where id = " + doctorId).get()
        registerPage = getRegisterPage(doctor.page, time)
        if registerPage is None:
            data = {"status":"1",
                "message":"No time"}
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(data, ensure_ascii=False))
        else:
            outputPage = register('https://reg.ntuh.gov.tw/WebAdministration/' +registerPage, id, birthday)
      
            soup = BeautifulSoup(outputPage)
            num = soup.find('table',{'id':'ShowResult'}).findAll('tr')[5].contents[2].contents[0].contents[0].string
            data = {"status":"0",
                    "message":num}
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(data, ensure_ascii=False))
        
    
application = webapp.WSGIApplication([('/ntuh/register', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
