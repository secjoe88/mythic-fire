#!/usr/bin/env python
import re
import httplib
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
	
#method to create parent key for api_request_log
DEFAULT_APILOG_NAME='apilog'
def api_log_key():
	return ndb.Key("APILog", DEFAULT_APILOG_NAME)
##constructor for APIRequest entitities in the Datastore
class APIRequest(ndb.Model):
	url=ndb.StringProperty();
	
## /post page receives POST request that updates server ip address, then stores it in the datastore	
class postpage(webapp2.RequestHandler):	
	def post(self):
		ip_address=self.request.body
		ipaddr=IPAddr(parent=ip_log_key())
		ipaddr.address=ip_address
		ipaddr.put()
		self.response.write("IP Address: " + ip_address+ " stored in database")

## /cp.* redirects to couchpotato	
class couchpotato(webapp2.RequestHandler):
	def get(self):
		#if the request is for the root object, http redirect to CouchPotato Server
		if self.request.path=='/cp':
			try:
				iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
				recent=iplog_query.fetch(1)
				self.redirect(str("https://"+recent[0].address+":8083"))
			except NeedIndexError:
				self.response.write("No recent IP Address Updates")
		#otherwise, assume it is an api request, send the api request to cp, get a response
		#and return the response 
		else:
			try:
				iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
				recent=iplog_query.fetch(1)
				cpcon=httplib.HTTPSConnection(str(recent[0].address+":8083"), timeout=100)
				cpcon.connect()
				apicall=re.findall('/api.*',self.request.path).pop()
				cpcon.request("GET", apicall)
				self.response.headerlist=cpcon.getresponse().getheaders()
				self.response.body=cpcon.getresponse().read()
				self.response.status=cpcon.getresponse().status
				#self.response.write(str(cpcon.getresponse().getheaders())+'\n'+str(self.response.headerlist))
				cpcon.close()
			except NeedIndexError:
				self.response.write("No recent IP Address Updates")
			
## /sb redirects to sickbeard			
class sickbeard(webapp2.RequestHandler):
	def get(self):
		#if the request is for the root object, http redirect to SickBeard Server
		if self.request.path=='/sb':
			try:
				iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
				recent=iplog_query.fetch(1)
				self.redirect(str("https://"+recent[0].address+":8081"))
			except NeedIndexError:
				self.response.write("No recent IP Address Updates")
		#otherwise, assume it is an api request, send the api request to sb, get a response
		#and return the response
		else:
			try:
				iplog_query=IPAddr.query(ancestor=ip_log_key()).order(-IPAddr.date)
				recent=iplog_query.fetch(1)
				sbcon=httplib.HTTPSConnection(str(recent[0].address+":8081"), timeout=300)
				sbcon.connect()
				apicall=re.findall('/api.*',self.request.path).pop()
				sbcon.request("GET", apicall)
				self.response.headerlist=sbcon.getresponse().getheaders()
				self.response.body=sbcon.getresponse().read()
				self.response.status=sbcon.getresponse().status
				#self.response.write(str(cpcon.getresponse().getheaders())+'\n'+str(self.response.headerlist))
				sbcon.close()
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
## /other is used for testing api request support
class apitest(webapp2.RequestHandler):
	def get(self):
		self.response.write(self.request.path)
		
class proxy(webapp2.RequestHandler):
	def get(self):
		url=self.request.path.split('/api/')
		self.response.write(url)
	
			
			

application = webapp2.WSGIApplication([
    ('/', MainPage),
	('/post', postpage),
	('/cp.*', couchpotato),
	('/sb.*', sickbeard),
	('/plex', plex),
	('/trans.*', transmission),
	('/deluge.*', deluge),
	('/.*api.*', apitest),
	('/proxy,proxy)
], debug=True)
