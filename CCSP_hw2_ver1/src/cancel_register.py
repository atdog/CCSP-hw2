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

def cancel_register(id, birthday):
    match = re.match("(\d{4})-(\d{2})-(\d{2})", birthday)
    birthYear = match.groups(1)[0]
    birthMonth = match.groups(1)[1]
    birthDay = match.groups(1)[2]
    

    cancelRegisterUrl = 'https://reg.ntuh.gov.tw:443/WebAdministration/Query.aspx'
    # First request without data
    page = fetchHtml(cancelRegisterUrl)
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    
    postValue = {   '__EVENTTARGET':'radInputNum$1',                                                                                    
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE':viewstate,
    '__EVENTVALIDATION':eventvalidation,
    'radInputNum':'1',                                                                                                  
    'ddlBirthMonth':'',
    'txtVerifyCode':'',
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(cancelRegisterUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', cancelRegisterUrl)
    page = urllib2.urlopen(r)
    # Second request with year
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    
    postValue = {   
    '__EVENTTARGET':'ddlBirthYear',                                                                                    
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE':viewstate,
    '__EVENTVALIDATION':eventvalidation,
    'radInputNum':'1',           
    'txtIdno':id,                                                                                       
    'ddlBirthYear':birthYear,
    'ddlBirthMonth':'',
    'txtVerifyCode':'',
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(cancelRegisterUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', cancelRegisterUrl)
    page = urllib2.urlopen(r)
    # Third reqeust with month
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    
    postValue = {   
    '__EVENTTARGET':'ddlBirthMonth',                                                                                    
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE':viewstate,
    '__EVENTVALIDATION':eventvalidation,
    'radInputNum':'1',           
    'txtIdno':id,                                                                                       
    'ddlBirthYear':birthYear,
    'ddlBirthMonth':birthMonth,
    'txtVerifyCode':'',
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(cancelRegisterUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', cancelRegisterUrl)
    page = urllib2.urlopen(r)
    # request to register time table
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    codeUrl = soup.find('img',{'id':'imgVlid'})['src']
    
    postValue = {   
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
    'txtVerifyCode':re.match('ValidNumber\.aspx\?checkCode=(.*)',codeUrl).groups(1)[0],
    'btnQuery':'查詢',
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(cancelRegisterUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', cancelRegisterUrl)
    page = urllib2.urlopen(r)
    return page.read()
    
#    return eventvalidation
    
    
def cancel(url):
    cancelUrl = 'https://reg.ntuh.gov.tw/WebAdministration/'+url
    page = fetchHtml(cancelUrl)
    soup = BeautifulSoup(page)
    viewstate = soup.find('input',{'name':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input',{'name':'__EVENTVALIDATION'})['value']
    postValue = {
        '__VIEWSTATE':viewstate,
        '__EVENTVALIDATION':eventvalidation,
        'btnYes':'是'
    }
    
    postData = urllib.urlencode(postValue)
    r = urllib2.Request(cancelUrl, postData)
    r.add_header('User-Agent', 'Mozilla 5.0')
    r.add_header('Referer', cancelUrl)
    page = urllib2.urlopen(r)
    return page.read()
    
        
class MainPage(webapp.RequestHandler):
    def post(self):
        doctorId = self.request.get('doctor')
        time = self.request.get('time')
        id = self.request.get('id')
        birthday = self.request.get('birthday')
        
        outputPage = cancel_register(id, birthday)

        #define variables
        match = re.match("(\d{4})-(\d{2})-(\d{2})-(.)", time)
        regYear = str(int(match.groups(1)[0]) - 1911)
        regMonth = str(int(match.groups(1)[1]))
        regDay = str(int(match.groups(1)[2]))
        regClock = None
        if match.groups(1)[3] == "A":
            regClock = "上午"
        elif match.groups(1)[3] == "B":
            regClock = "下午"
        else:
            regClock = "晚上"

        soup = BeautifulSoup(outputPage)
        resultRows = soup.find('table',{'id':'ResultTable'}).findAll('tr')
        prog = re.compile(regYear+"\."+regMonth+"\."+regDay)
        cancelLink = None
        for row in resultRows:
            rowTime = row.contents[5].contents[0].contents[0]
            rowClock =  row.contents[6].contents[0].contents[0]
            match = prog.match(rowTime)
            if match != None:
                if len(row.contents[5].contents[0].contents) > 1:
                    if rowClock == unicode(regClock, 'utf-8'):
                        link = row.find('a',href=re.compile(r'^CancelForm\.aspx\?.*'))
                        if link != None:
                            cancelLink = link['href']
                            break
        if cancelLink == None:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps({'status':'1','status':'Error'},ensure_ascii=False))
        else:
            outputPage = cancel(cancelLink)
#            print cancelLink
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps({'status':'0'},ensure_ascii=False))
        
    
application = webapp.WSGIApplication([('/ntuh/cancel_register', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
