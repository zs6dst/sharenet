#!/usr/bin/python

import ConfigParser
import sys
import os
import logging
import shutil
import glob
import datetime as dt
import MySQLdb
from bs4 import BeautifulSoup
from importexception import *


def parseSoup(soup):
	tr = [x for x in soup.find_all("tr") if "Short Name" in x.strings]
	if len(tr) == 0:
		raise Exception("Short name not found as expected")
	tr = tr[-1:][0] #Assume the last one is the required one
	data = [x for x in tr.parent.stripped_strings]
	name = data[data.index("Short Name") + 1]
	name = name[:name.index("(")].replace(" ","")
	
	suspended = (0 != len([a for a in soup.find_all("a") if "This share has been suspended..." in a.strings]))
	
	if suspended:
		date = None
		close = hi = lo = vol = 0L
	else:
		tr = [x for x in soup.find_all("tr") if "Closing Prices" in x.strings]
		if len(tr) == 0:
			raise Exception("Closing Prices not found as expected")
		tr = tr[-1:][0] #Assume the last one is the required one
		data = [x for x in tr.parent.stripped_strings]

		s = data[data.index("Closing Prices") + 1]
		date = dt.datetime.strptime(s, "( %d/%m/%Y )").date()
		close = int(data[data.index("Close") + 1])
		hi = int(data[data.index("High") + 1])
		lo = int(data[data.index("Low") + 1])
		vol = int(data[data.index("Volume") + 1])
		
	return name, suspended, date, close, hi, lo, vol

	
def main():    
	logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

	config = ConfigParser.ConfigParser()
	config.readfp(open("sharenet.ini"))
	dbHost = config.get("Database", "host")
	dbName = config.get("Database", "name")
	dbUser = config.get("Database", "uid")
	dbPwd = config.get("Database", "pwd")
	baseDir = config.get("Directories",os.name)
	dataDir = config.get("Directories", "data")
	dataDir = os.path.join(baseDir, *dataDir.split("|"))
	inDir = os.path.join(dataDir,"in")
	doneDir = os.path.join(dataDir,"done")
	
	#Sanity check
	files = glob.glob(os.path.join(inDir,"*.html"))
	if len(files) == 0:
		logging.warning("Nothing to import.")
		sys.exit(0)
	files.sort()
		
	#Connect to database
	try:
		logging.info("Connecting to database...")
		db = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPwd, db=dbName)
		logging.info("Database connected")
	except:
		logging.critical("FAILED TO CONNECT TO DATABASE")
		sys.exit(1)

	try:
		cmd = db.cursor()
		for file in files:
			path,fileName = os.path.split(file)
			logging.debug(fileName)
			
			statinfo = os.stat(file)
			if statinfo.st_size == 0L:
				logging.warning("{0} is empty".format(fileName))
				continue
				
			logging.info("Importing {0}...".format(fileName))
			try:
				soup = BeautifulSoup(open(file), "html.parser")
				if soup.title.string.startswith("502"):
					logging.warning("{0} contains no data".format(fileName))
					os.unlink(file)
					continue
				
				name, suspended, date, price, hi, lo, vol = parseSoup(soup)
				if suspended:
					logging.warning("{0} is suspended".format(name))
					sql = "call suspendShare('{0}')".format(name)
				else:
					sql = "call importRawClosing('{0}','{1}',{2},{3},{4},{5})".format(name, date.strftime("%d%m%y"), price, hi, lo, vol)
				logging.debug(sql)
				cmd.execute(sql)
				shutil.move(file, os.path.join(doneDir, fileName))
				db.commit()
				logging.info("{0} imported".format(fileName))
			except ImportWarning, e:
				logging.error(e.msg)
				break
			except ImportError, e:
				logging.error(e.msg)
				raise
			except:
				logging.error(sys.exc_info()[0])
				db.rollback()
				raise
		logging.info("Processing raw closing prices...")
		cmd.execute("call importClosing()")
		db.commit()
		logging.info("Import done.")
	finally:
		db.close()

		
if __name__ == "__main__":
	main()
