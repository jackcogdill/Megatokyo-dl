# System packages
import os
import re
import glob
import urllib.request
import collections
from bs4 import BeautifulSoup

# Local packages
import console
import ANSI

COLS, ROWS = 0, 0

def getSoup(url):
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    header = { 'User-Agent' : agent }
    req = urllib.request.Request(url, None, header)

    try:
        data = urllib.request.urlopen(req).read()
    except:
        print('Could not open url: \'%s\'' % url)
        exit(1)

    return BeautifulSoup(data, 'lxml')

def fix_url(s):
    patt = '(%\w\w)'
    for quote in re.findall(patt, s):
        s = s.replace(quote, urllib2.unquote(quote))
    return s

def fixdir(s):
    for c in '/?<>\:*|"':
        s = s.replace(c, '-')
    return s

def byte_convert(b):
    n, b = 0, float(b)
    while b / 1024 >= 1:
        b = b / 1024
        n += 1
    return '%.2f%s' % (b, 'BKMGT'[n])

def dlProgress(am, bls, ts):
    per = am * bls * 100.0 / ts
    if per > 100:
        per = 100

    max_size = 75
    arrow_len = int(per * max_size / 100.0)
    arrow = '=' * (arrow_len - 1) + '>'
    arrow = ('%%-%ds' % max_size) % arrow
    if per < 100:
        arrow = ANSI.color(arrow, 'yellow')

    prog = '\r%6.1f%% [%s] Size: %-5s' % (per, arrow, byte_convert(ts))
    print(prog, end='', flush=True)

def downloadb(url, filename=None):
    if not filename:
        temp = fix_url(url)
        filename = temp[(temp.rindex('/') +1):]
        filename = fixdir(filename)

    try:
        urllib.request.urlretrieve(url, filename, reporthook=dlProgress)
        print()
    except KeyboardInterrupt:
        if os.path.isfile(filename):
            os.remove(filename)
        print()
        print('User quit')
        exit(1)
    except:
        return False

    return True

def getNumber(s):
    prog = re.compile('\d{4}')
    match = prog.match(s)
    if match:
        return match.group(0)
    else:
        return None

def getDownloaded():
    types = ('.gif', '.png', '.jpg')
    downloaded = set()

    for ext in types:
        for file in glob.glob('*' + ext):
            number = getNumber(file)
            if number:
                downloaded.add(number)

    return downloaded

def getLinks():
    url = 'http://megatokyo.com/strips/'
    soup = getSoup(url)
    links = {}

    prog = re.compile('(\d{4})\.')
    for link in soup.find_all('a'):
        href = link.get('href')
        match = prog.match(href)
        if match:
            number = match.group(1)
            links[number] = href

    return links

def getTitles():
    search = 'http://megatokyo.com/archive.php?list_by=date'
    soup = getSoup(search)
    found = None
    for div in soup.find_all('div', 'content'):
        if div.h2.string == 'Comics by Date':
            found = div
            break
    else:
        return None

    titles = collections.OrderedDict()
    for li in found.find_all('li'):
        title = li.a.string
        number = getNumber(title)
        if number:
            titles[number] = title

    return titles

def getExtension(s):
    match = re.search('\.[^\.]+$', s)
    if match:
        return match.group(0)
    else:
        return None

# Print without newline: add a space and flush
def print_nonl(s):
    print(s, end=' ', flush=True)

def main():
    global COLS, ROWS
    COLS, ROWS = console.getTerminalSize()

    mg = 'Megatokyo'
    if not os.path.isdir(mg):
        os.mkdir(mg)
    os.chdir(mg)

    print_nonl('Downloading info...')
    titles = getTitles()
    links = getLinks()
    if not titles:
        print('Error: Could not find list of comics.')
        exit(1)
    print('found %d titles.' % len(titles))

    print_nonl('Finding download links...')
    links = getLinks()
    print('done.')

    downloaded = getDownloaded()

    url = 'http://megatokyo.com/strips/'
    for number, title in titles.items():
        if number in downloaded:
            continue

        if number not in links:
            print('Error: Could not find download link for %s' % number)
            continue

        print('Downloading %s...' % number)
        link = links[number]
        ext = getExtension(link)
        if not ext:
            print('Error: Could not download \'%s\'', title)
            continue

        link = url + link
        filename = fixdir(title + ext)
        if not downloadb(link, filename=filename):
            print('Error: Could not download \'%s\'', title)

if __name__ == '__main__':
    main()

