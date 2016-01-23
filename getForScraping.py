import urllib
import datetime as dt

DIR = '/home/stoffel/shares/sharenet/scrapings/'
CODES = ['ADI','BCX','CCL','DTC','EOH','FRT','GIJ','ISA','MOR','PCN','SDH','SQE','CVN']
t = dt.date.today()

for code in CODES:
    try:
        print 'Getting page for %s...' % code
        url = "http://www.sharenet.co.za/v3/quickshare.php?scode=" + code + 'x'
        html = urllib.urlopen(url).read()
        fileName = '%s%s-%s.html' % (DIR, code, t.strftime('%Y%m%d'))
        f = open(fileName, 'w')
        f.write(html)
        f.close()
    except Exception, e:
        print e.message
        
