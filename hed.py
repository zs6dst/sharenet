import sys
import logging
import utils
import MySQLdb
from importexception import * 

def parse(fileName, db):
	logging.info("Parsing " + fileName)
	f = open(fileName)
	cursor = db.cursor()
	try:
		for line in f:
			logging.debug(line)
			if len(line) < 10 or line[0] != '*':
				continue
			x = line.strip("*\r\n").replace("  ", " ").split(" ")
			if x[0] == "EHD": #End of file
				break
			elif x[0] == "NSH": #New share
				#Check if the share exists
				shareCursor = db.cursor()
				shareCursor.execute("select count(*) from share where name = '%s'" % x[1])
				result = shareCursor.fetchone()
				shareCursor.close()
				if result[0] != 0:
					continue
				#HED contain bad data to create some shares
				if x[1] == "Select": #WTF line
					continue
				if x[1] == "ASCEN" or x[1] == "NEW" or x[1] == "JDG": #Names contain spaces
					logging.warning(line)
					raise ImportWarning("Create share manually")
				if len(x) != 4:
					if x[1] == '38': continue
					raise ImportError("Missing fields: *NSH [name] [SN sector] YYYYYY");
				secCursor = db.cursor()
				secCursor.execute("select count(*) from sn_sector where id = '%s'" % x[2])
				result = secCursor.fetchone()
				secCursor.close()
				if result[0] == 0:
					raise ImportError("Unknown Sharenet sector: %s" % x[2])
				cursor.execute("call addShare('%s','%s')" % (x[1], x[2]))
			elif x[0] == "DSH": #Delisting
				cursor.execute("call delistShare('%s')" % x[1].strip(" "))
			elif x[0] == "RSH": #Rename
				cursor.execute("call renameShare('%s','%s')" % (x[1].strip(" "), x[3].strip(" ")))
			elif x[0] == "MSH": #Change sector
				cursor.execute("call changeShareSector('%s','%s')" % (x[1].strip(" "), x[2].strip(" ")))
			elif x[0] == "ERR": #Correction
				if x[1] == "ASCEN" or x[1] == "NEW" or x[1] == "JDG":
					logging.warning(line)
					raise ImportWarning("Update manually")
				else:
					cursor.execute("call fixShare('%s','%s',%d,%d,%d,%d)" % (x[1].strip(" "), x[3].strip(" "), utils.intParse(x[4]), utils.intParse(x[5]), utils.intParse(x[6]), utils.intParse(x[7])))
			elif x[0] == "SPL": #Splits & consolidations
				cursor.execute("call splitShare('%s','%s',%s,%s)" % (x[1].strip(" "), x[5].strip(" "), x[3], x[4]))
			elif x[0] == "NSE": #Sector new/change
				updateCursor = db.cursor()
				updateCursor.execute("call updateSector('%s','%s')" % (x[1].strip(" "), x[2].strip(" ")))
				result = updateCursor.fetchone()
				newSector = (result[0] == 'NEW')
				updateCursor.close()
				if newSector:
					raise ImportError("New sector: %s" % x[2])
			elif x[0] == "SPL2":
				continue
			else:
				raise ImportError("Unknown command: %s" % x[0])
		f.close()
	except ValueError, e:
		f.close()
		raise ImportError("Value error on %s: %s" % (x[0], line))
	except:
		f.close()
		logging.error(line)
		raise
