#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import re
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

USER_RE=re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
USER_PW=re.compile(r"^.{3,20}$")
USER_EL=re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
    return USER_PW.match(password)

def valid_email(email):
    return USER_EL.match(email)

class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.write(*a,**kw)

    def render_str(self,template,**params):
        t=jinja_env.get_template(template)
        self.write(t.render(params))

class ShoppingHandler(Handler):
    def get(self):
        items = self.request.get_all('food')
        self.render_str("shopping_list.html",items=items)


class MainHandler(Handler):
    def error(self,name="",name_error="",password_error="",verify_error="",email_error="",email=""):
        self.render_str("sign_up.html",
                        name=name,
                        name_error=name_error,
                        password_error=password_error,
                        verify_error=verify_error,
                        email_error=email_error,
                        email=email
                        )
    
    def get(self):
        self.error()

    def post(self):
        
        name_error="invalid username"
        password_error="invalid password"
        verify_error="your password's didn't match"
        email_error="invalid email id"
        
        username=self.request.get('username')
        password=self.request.get('password')
        verify=self.request.get('verify')
        email=self.request.get('email')

        # user input validation starts

        if valid_username(username):
            name_error=""

        if email:
            if valid_email(email):
                email_error=""
        else:
            email_error=""

        if password and valid_password(password):
            password_error=""
            if password==verify:
                verify_error=""
        else:
            verify_error=""
            
        #user input validation ends

        if name_error=="" and password_error=="" and verify_error=="" and email_error=="":
            self.redirect('/welcome?username=%s'%(username))
        else:
            self.error(username,name_error,password_error,verify_error,email_error,email)


class WelcomeHandler(Handler):
    def get(self):
        if valid_username(self.request.get('username')):
            self.render_str("welcome.html",username=self.request.get('username'))
        else:
            self.redirect('/signup')

class FizzBuzz(Handler):
    def get(self):
        self.render_str("fizzbuzz.html",n=self.request.get('n'))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class AsciArt(Handler):
    def error(self,title="",art="",error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        self.render_str("AsciArt.html",
                        title=title,
                        art=art,
                        error=error,
                        arts = arts
                        )
    
    def get(self):
        self.error()

    def post(self):
        title=self.request.get('art_name')
        art=self.request.get('art')

        if art and title:
            a = Art(title = title , art = art)
            a.put()

            self.redirect('/')
        else:
            self.error(title,art,"we need both title and art")

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified=db.DateTimeProperty(auto_now = True)


class NewPostHandler(Handler):
    def error(self,subject="",content="",error=""):
        self.render_str('blog_new_post.html',
                        subject=subject,
                        content=content,
                        error=error
                        )
    
    def get(self):
        self.error()

    def post(self):
        subject=self.request.get('subject')
        content=self.request.get('content')
        if subject and content:
            a=Blog(subject=subject,content=content)
            a.put()
            self.redirect('/blog/%s'%a.key().id())
        else:
            self.error(subject,content,'we need both subject and content')

class PermaHandler(Handler):
    def get(self,user_id):
        p=Blog.get_by_id(int(user_id))
        if p:
            self.render_str('perma.html',subject=p.subject.replace('\n','</br>'),content=p.content.replace('\n','<br>'))
        else:
            self.write('error')

class MainPage(Handler):
    def get(self):
        curser=db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC LIMIT 30')
        self.render_str('mainpage.html',wrap=curser)


app = webapp2.WSGIApplication([
    ('/',AsciArt),
    ('/signup', MainHandler),
    ('/welcome',WelcomeHandler),
    ('/shopping',ShoppingHandler),
    ('/fizzbuzz',FizzBuzz),
    ('/blog/newpost',NewPostHandler),
    ('/blog/([0-9]+)',PermaHandler),
    ('/blog',MainPage)
], debug=True)


























