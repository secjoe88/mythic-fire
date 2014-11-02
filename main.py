#!/usr/bin/env python

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.db import NeedIndexError

# / page simply shows the most recently updated ip address and when it was updated
class MainPage(webapp2.RequestHandler):
    def get(self):
	try:
		iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
		recent=iplog_query.fetch(20)
		response_text=''
		for result in recent:
			response_text=response_text + '\n'+result.address +" "+ result.date.strftime('%c')
		self.response.write(response_text.replace('\n', '<br />'))
	except NeedIndexError:
		self.response.write("No recent IP Address Updates")
	

		

## method to create parent key for ip_log
DEFAULT_IPLOG_NAME='iplog'
def ip_log_key():
	return ndb.Key("IPLog", DEFAULT_IPLOG_NAME)
##constructor for IPAddr entities in the Datastore
class IPAddr(ndb.Model):
	address=ndb.StringProperty()
	date=ndb.DateTimeProperty(auto_now_add=True)

	
## /post page receives POST request that updates server ip address, then stores it in the datastore	
class postpage(webapp2.RequestHandler):	
	def post(self):
		ip_address=self.request.body
		ipaddr=IPAddr(parent=ip_log_key())
		ipaddr.address=ip_address
		ipaddr.put()
		self.response.write("IP Address: " + ip_address+ " stored in database")

## /cp redirects to couchpotato		
class couchpotato(webapp2.RequestHandler):
	def get(self):
		try:
			iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
			recent=iplog_query.fetch(1)
			self.redirect(str("https://"+recent[0].address+":8083"))
		except NeedIndexError:
			self.response.write("No recent IP Address Updates")

## /sb redirects to sickbeard			
class sickbeard(webapp2.RequestHandler):
	def get(self):
		try:
			iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
			recent=iplog_query.fetch(1)
			self.redirect(str("https://"+recent[0].address+":8081"))
		except NeedIndexError:
			self.response.write("No recent IP Address Updates")
			
## /plex redirects to plex			
class plex(webapp2.RequestHandler):
	def get(self):
		try:
			iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
			recent=iplog_query.fetch(1)
			self.redirect(str("http://"+recent[0].address+":32400/manage"))
		except NeedIndexError:
			self.response.write("No recent IP Address Updates")
			
			
## /trans redirects to transmission
class transmission(webapp2.RequestHandler):
	def get(self):
		try:
			iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
			recent=iplog_query.fetch(1)
			self.redirect(str("http://"+recent[0].address+":9091"))
		except NeedIndexError:
			self.response.write("No recent IP Address Updates")
			
			
## /deluge redirects to deluge
class deluge(webapp2.RequestHandler):
	def get(self):
		try:
			iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
			recent=iplog_query.fetch(1)
			self.redirect(str("https://"+recent[0].address+":8112"))
		except NeedIndexError:
			self.response.write("No recent IP Address Updates")
			
			

application = webapp2.WSGIApplication([
    ('/.*', MainPage),
	('/post', postpage),
	('/cp.*', couchpotato),
	('/sb.*', sickbeard),
	('/plex', plex),
	('/trans.*', transmission),
	('/deluge.*', deluge)
], debug=True)