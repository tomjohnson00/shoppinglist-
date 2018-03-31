import os

import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

#
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



def shoppinglist_key(email):

    return ndb.Key('Item', email)


class Item(ndb.Model):
    name = ndb.StringProperty(indexed=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        logout = '<a href="{}">sign out</a>'.format(logout_url) 


        user_email=users.get_current_user().email()
        items_query = Item.query(ancestor=shoppinglist_key(user_email)).order(Item.name)


        items = items_query.fetch()      

        template_values = {
            'title': "success",
            'logout': logout,
            'items': items
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



class AddItem(webapp2.RequestHandler):

    def post(self):
        itemName = self.request.get('itemName', 'empty item')
        user_email=users.get_current_user().email()
        item = Item(parent=shoppinglist_key(user_email))
        item.name = itemName
        item.put()
        self.redirect('/')

class RemoveItem(webapp2.RequestHandler):
    def post(self):

        itemId = self.request.get('id')
        ndb.Key(urlsafe=itemId).delete()
        
        self.redirect('/')

class UpdateItem(webapp2.RequestHandler):
    def post(self):

        itemId=self.request.get('id')
        item = ndb.Key(urlsafe=itemId).get()
        item.name = self.request.get('name')
        item.put()
        self.redirect('/')

class DeleteAll(webapp2.RequestHandler):
    def get(self):
        user_email=users.get_current_user().email()
        items_query = Item.query(ancestor=shoppinglist_key(user_email)).order(Item.name)
        items = items_query.fetch() 
        for item in items:
           # ndb.Key(urlsafe=item.key.id()).delete()  
           item.key.delete()         
        self.redirect('/')


# [START app]
app = webapp2.WSGIApplication([

    ('/', MainPage),
    ('/addItem', AddItem),
    ('/removeItem', RemoveItem),
    ('/updateItem', UpdateItem),
    ('/deleteAll', DeleteAll)

], debug=True)
# [END app]