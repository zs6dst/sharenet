from ftplib import FTP
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

DIR = "shares/sharenet/scrapings"
ACT = "D"

try:
	logging.info("Logging in...")
	ftp = FTP("www.zeniton.co.za", "username","password")
	logging.info("Logged in.")
	
	ftp.cwd(DIR)
	files = [f for f in ftp.nlst() if f.endswith("html")]
	if len(files) > 0:
		for f in files:
			logging.info("%s..." % f)
			if "G" in ACT:
				file = open("/home/cava/Dropbox/%s/%s" % (DIR,f), 'wb')
				ftp.retrbinary("RETR %s" % f, file.write)
				file.close()
			if "D" in ACT:
				ftp.delete(f)
	else:
		logging.info("Nothing to do.")
	
	logging.info("Logging out...")
	ftp.quit()
	logging.info("Logged out.")
except Exception as e:
	logging.error(e)
