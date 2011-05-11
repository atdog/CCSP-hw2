from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db


class MainPage(webapp.RequestHandler):
    def get(self):
        link = db.GqlQuery("select * from Link")
        for linkObj in link:
            linkObj.delete()
        
        doctor = db.GqlQuery("SELECT * FROM Doctor ORDER BY id")        
        for doctorObj in doctor:
            doctorObj.delete()
        
        dept = db.GqlQuery("select * from Dept")
        for deptObj in dept:
            deptObj.delete()
        

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("Clean successful")
        
    
application = webapp.WSGIApplication([('/ntuh/clean', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
