#!/usr/bin/python

import ConfigParser
import urllib2
import datetime
import sys
import os
import logging

def name2date(name):
	return datetime.date(int(name[0:2])+2000, int(name[3:5]), int(name[6:8]))
	
def date2name(date):
	return '%.02d-%.02d-%.02d.lzh' % (date.year-2000, date.month, date.day)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

appDir = os.path.join(os.environ["HOME"], "shares/sharenet")

config = ConfigParser.ConfigParser()
config.readfp(open(os.path.join(appDir, "sharenet.ini")))
url = config.get("Download", "url")
realm = config.get("Download", "realm")
uid = config.get("Download", "uid")
pwd = config.get("Download", "pwd")
inDir = config.get("Import", "in")

try:
	lastfile = open(os.path.join(appDir, "lastfile"),"r")
except:
	logging.error("Cannot find 'lastfile'")
	sys.exit(1)
name = lastfile.readline()
lastfile.close()

pwdMan = urllib2.HTTPPasswordMgr()
pwdMan.add_password(realm, "www.sharenet.co.za", uid, pwd)
handler = urllib2.HTTPBasicAuthHandler(pwdMan)
opener = urllib2.build_opener(handler)

d = name2date(name) + datetime.timedelta(1) 
while (d <= datetime.date.today()):
	name = date2name(d)
	logging.info("Downloading " + name)
	try:
		response = opener.open(url + name)
		lzh = response.read()
		response.close()
		f = open(os.path.join(inDir, name), "wb")
		f.write(lzh)
		f.close()
		lastfile = open(os.path.join(appDir, "lastfile"),"w")
		lastfile.write(name + "\n")
		lastfile.close()
		logging.info("Done.")
	except urllib2.HTTPError, e:
		if (e.code == 404):
			logging.warning(name + " not found")
		else:
			logging.error("HTTP ERROR: " + str(e.code) + " " + e.msg)
	except:
		print sys.exc_info()[0]

	d = d + datetime.timedelta(1)

logging.info("Download done.")
