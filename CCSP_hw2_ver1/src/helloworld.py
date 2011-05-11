from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from BeautifulSoup import BeautifulSoup
import urllib2
import re

def fetchHtml(url):
    r = urllib2.Request(url)
    r.add_header('User-Agent', 'Mozilla 5.0')
    page = urllib2.urlopen(r)
    return page

class MainPage(webapp.RequestHandler):
    def get(self):
        hospitalUrl = 'https://reg.ntuh.gov.tw/webadministration/ClinicTable.aspx '
        indexPage = fetchHtml(hospitalUrl)
        
        soup = BeautifulSoup(indexPage)
        
        dept = soup.findAll('a',href=re.compile(r'^DoctorTable\.*'))
        deptList = []
        for deptObj in dept:
            id = len(deptList)+1
            jsonObj = {id: deptObj.font.string}
            deptList.append(json.dumps(jsonObj, ensure_ascii=False));
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(deptList)
        
    
application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
