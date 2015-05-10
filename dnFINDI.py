import logging
import utils
import MySQLdb

def parse(fileName, db):
	n = 0
	logging.info("Parsing " + fileName)
	f = open(fileName)
	cursor = db.cursor()
	for line in f:
		name = line[4:13]
		if (not name.startswith('JT-FINDI')):
			continue
		if name == 'U-27FBFOF':
			n += 1
			if n > 1:
				continue
		if name == "EOFEOFEOF":
			break
		date = line[19:21] + line[17:19] + line[15:17]
		price = utils.intParse(line[22:30])
		hi = utils.intParse(line[31:39])
		lo = utils.intParse(line[40:48])
		vol = utils.intParse(line[49:57])
		sql = "call importRawClosing('%s','%s',%d,%d,%d,%d)" % (name.strip(" "), date, price, hi, lo, vol)
		logging.debug(sql)
		cursor.execute(sql)
	f.close()
	logging.info(fileName + " done.")
