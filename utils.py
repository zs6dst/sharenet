import ConfigParser

def readConfig():
	config = ConfigParser.ConfigParser()
	config.readfp(open("sharenet.ini"))
	binDir = config.get("Import", "bin")
	inDir = config.get("Import", "in")
	workDir = config.get("Import", "work")
	doneDir = config.get("Import", "done")
	dbHost = config.get("Database", "host")
	dbName = config.get("Database", "name")
	dbUser = config.get("Database", "uid")
	dbPwd = config.get("Database", "pwd")

def intParse(s):
	if s.replace(" ","") == "":
		return 0
	else:
		try:
			return int(s)
		except:
			try:
				return int(float(s))
			except:
				return 0

