# System packages
import os
import sys
import urllib
import urllib2
import re

# Local packages
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import console
import ANSI

COLS, ROWS = console.getTerminalSize()

def getSoup(url):
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    header = { 'User-Agent' : agent }
    req = urllib2.Request(url, None, header)
    data = urllib2.urlopen(req).read()
    return BeautifulSoup(data)

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
        s = '\r%s[%s]' % (('%6.1f%%' % per), (('=' * int(per * 75 / 100))[:-1]+'>').ljust(75, ' '))
        s += ' Size: ' + byte_convert(ts)
        sys.stdout.write(s + ' ' * (COLS - len(s)))
        sys.stdout.flush()

    try:
        urllib.urlretrieve(url, filename, reporthook=dlProgress)
        print
    except:
        if os.path.isfile(filename):
            os.remove(filename)
        return False


def main():
    print 'Downloading info...',
    url = 'http://megatokyo.com/strips/'

    mg = 'Megatokyo'
    if not os.path.isdir(mg):
        os.mkdir(mg)
    os.chdir(mg)

    search = 'http://megatokyo.com/archive.php?list_by=date'
    soup = getSoup(search)

    found = None
    for div in soup.findAll('div'):
        if div.has_key('class') and div['class'] == 'content' and div.h2.string == 'Comics by Date':
            found = div
            break
    else:
        print('Error: Could not find list of comics')
        exit(1)

    titles = [li.a.string for li in found.findAll('li')]
    print('found %d titles' % len(titles))
    exit(0)

    for i in titles:
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
        ANSI.clear(2)

if __name__ == '__main__':
    main()

