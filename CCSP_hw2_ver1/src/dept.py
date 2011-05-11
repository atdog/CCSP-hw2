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
            dept = db.GqlQuery("SELECT * FROM Dept ORDER BY id")
            
            deptList = []
            for deptObj in dept:
                deptList.append({deptObj.id:deptObj.name})
            
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(deptList, ensure_ascii=False))
        else:
            deptData = []
            dept = db.GqlQuery("select * from Dept where id =" + id).get()
            if(dept != None):
                deptData.append({"id":dept.id})
                deptData.append({"name":dept.name})
                doctorList = []
                timeList = []
                links = db.GqlQuery("select * from Link where deptId = "+id)
                if links != None:
                    for link in links:
                        doctor = db.GqlQuery("select * from Doctor where id ="+ str(link.doctorId)).get()
                        if(doctor != None):
                            doctorList.append({doctor.id:doctor.name})
                            timeList.extend(gettime.getTime(doctor.page))
                deptData.append({"doctor": doctorList})
                deptData.append({"time":timeList})
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(json.dumps(deptData, ensure_ascii=False))
        
    
application = webapp.WSGIApplication([('/ntuh/dept', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
