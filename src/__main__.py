import os, sys, urllib, urllib2, console, re
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) \
	AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11'
header = { 'User-Agent': user_agent }
(width, height) = console.getTerminalSize()

def getPage(url):
	req = urllib2.Request(url, None, header)
	return urllib2.urlopen(req).read()

def getSoup(url):
	return BeautifulSoup(getPage(url))

def clrlns(num_lines):
	num_lines += 1
	def moveCursorUp(n):
		print '\033[%sA' % n
	moveCursorUp(num_lines)
	for i in range(num_lines -1): print ' ' * width
	moveCursorUp(num_lines)

def fix_url(s):
	patt = '(%\w\w)'
	for quote in re.findall(patt, s):
		s = s.replace(quote, urllib2.unquote(quote))
	return s

def fixdir(fdir):
	for c in '/?<>\:*|"': 
		fdir = fdir.replace(c, '-')
	return fdir

def downloadb(url, filename=''):
	def fileName(url):
		return url[(url.rindex('/') +1):]
	if filename == '': filename = fileName(fix_url(url))
	filename = fixdir(filename)
	url = urllib.urlopen(url).geturl()
	
	def byte_convert(b):
		n, b = 0, float(b)
		while b / 1024 >= 1:
			b = b / 1024
			n += 1
		return '%.2f%s' % (b, 'BKMGT'[n])
	
	def dlProgress(am, bls, ts):
		per = am * bls * 100.0 / ts
		if per > 100: per = 100.0
		s = '\r%s[%s]' % (('%.1f%%' % per).ljust(6, ' '), (('=' * int(per * 75 / 100))[:-1]+'>').ljust(75, ' '))
		s += ' Size: ' + byte_convert(ts)
		sys.stdout.write(s + ' ' * (width - len(s)))
		sys.stdout.flush()
	
	try:	
		urllib.urlretrieve(url, filename, reporthook=dlProgress)
		print
	except:
		if os.path.isfile(filename): os.remove(filename)
		return False

url = 'http://megatokyo.com/strips/'

mg = 'Megatokyo'
if not os.path.isdir(mg): os.mkdir(mg)
os.chdir(mg)

search = 'http://megatokyo.com/archive.php?list_by=date'
soup = getSoup(search)
L = []
for x in soup.findAll('div'):
	if x.has_key('class'):
		if x['class'] == 'content' and x.h2.string == 'Comics by Date':
			for y in x.findAll('li'): L.append(y.a.string)

for i in L:
	s = str(i)[:4].rjust(4, '0') + '.gif'
	fname = fixdir(i + s[-4:])
	if not os.path.isfile(fname):
		print 'Downloading', i
		if not downloadb(url + s, filename=fname):
			s = s[:-3] + 'jpg'
			fname = fixdir(i + s[-4:])
			if not os.path.isfile(fname):
				if not downloadb(url + s, filename=fname):
					s = s[:-3] + 'png'
					fname = fixdir(i + s[-4:])
					if not os.path.isfile(fname): downloadb(url + s, filename=fname)
	clrlns(2)
