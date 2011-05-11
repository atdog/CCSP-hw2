from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
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


class MainPage(webapp.RequestHandler):
    def get(self):
        hospitalUrl = 'http://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx'
        indexPage = fetchHtml(hospitalUrl)
        
        soup = BeautifulSoup(indexPage)
        ############find doctors##############
        doctor = soup.findAll('tr',{"class":"ms-alternating-0"})
        doctorList = []
        id = 1
        docId = 1
        for doctorObj in doctor:
            deptName = doctorObj.contents[0].string
            dept_res = db.GqlQuery("SELECT * FROM Dept where name = '"+deptName+"'")
            dept_Id = None
            if dept_res.count() == 0:
                dept_db = Dept()
                dept_db.id = id
                deptId = id
                dept_db.name = deptName.decode('big5')
                dept_db.put()
                id+=1 
            else:
                deptId = dept_res.get().id
                
            for doctorIns in doctorObj.findAll('a'):
                if doctorIns.string is not None and doctorIns.string != " " and doctorIns.string != "":
                    doctorName = doctorIns.string
                    doctorName = unicode(doctorName).replace(u'\xa0','').replace(u'\u6052','').replace(u'\u5553','').replace(u'\u5cef','').replace(u'\ue6ee','')
                    doctor_res = db.GqlQuery("SELECT * FROM Doctor where name = '"+doctorName+"'")
                    doctorId = None
                    if doctor_res.count() == 0:
                        doctor_db = Doctor()
                        doctor_db.name = doctorName.decode('big5')
                        doctor_db.id = docId
                        doctor_db.page = doctorIns['href']
                        doctorId = docId
                        doctor_db.put()
                        docId+=1
                    else:
                        doctorId = doctor_res.get().id
                    link_db = Link()
                    link_db.deptId = deptId
                    link_db.doctorId = doctorId
                    link_db.put()
                    jsonObj = {"doctorId":doctorId,"name":doctorName,"dept":deptName,"deptId":deptId,"href":doctorIns['href']}
                    doctorList.append(jsonObj) 
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(json.dumps(doctorList,ensure_ascii=False))
        
    
application = webapp.WSGIApplication([('/ntuh/update', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
