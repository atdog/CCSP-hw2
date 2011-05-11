from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from BeautifulSoup import BeautifulSoup
from google.appengine.ext import db
import urllib2
import re
import gettime

from dbTable import Dept, Doctor

class MainPage(webapp.RequestHandler):
    def get(self):
        id = self.request.get('id')
        if id == "":
            doctor = db.GqlQuery("SELECT * FROM Doctor ORDER BY id")
            
            doctorList = []
            for doctorObj in doctor:
                doctorList.append({doctorObj.id:doctorObj.name})
        
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(doctorList, ensure_ascii=False))
        else:
            doctor = db.GqlQuery("select * from Doctor where id = " + id).get()
            doctorData = []
            
            if doctor != None:
                doctorData.append({"id":doctor.id})
                doctorData.append({"name":doctor.name})
                deptList = []
                links = db.GqlQuery("select * from Link where doctorId = "+id)
                if links != None:
                    for link in links:
                        dept = db.GqlQuery("select * from Dept where id ="+ str(link.deptId)).get()
                        if(dept != None):
                            deptList.append({dept.id:dept.name})
                doctorData.append({"dept": deptList})           
                doctorData.append({"time": gettime.getTime(doctor.page)}) 
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(doctorData, ensure_ascii=False))  
        
    
application = webapp.WSGIApplication([('/ntuh/doctor', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
