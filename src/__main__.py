# System packages
import os
import re
import glob
import urllib.request
from bs4 import BeautifulSoup

# Local packages
import console
import ANSI

COLS, ROWS = 0, 0

def getSoup(url):
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    header = { 'User-Agent' : agent }
    req = urllib.request.Request(url, None, header)
    data = urllib.request.urlopen(req).read()
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

def downloadb(url, filename=None):
    if not filename:
        temp = fix_url(url)
        filename = temp[(temp.rindex('/') +1):]
        filename = fixdir(filename)

    try:
        url = urllib.request.urlopen(url).geturl()
    except urllib.error.HTTPError:
        return False

    def byte_convert(b):
        n, b = 0, float(b)
        while b / 1024 >= 1:
            b = b / 1024
            n += 1
        return '%.2f%s' % (b, 'BKMGT'[n])

    def dlProgress(am, bls, ts):
        per = am * bls * 100.0 / ts
        if per > 100:
            per = 100.0

        max_size = 75
        arrow_len = int(per * max_size / 100.0)
        arrow = '=' * (arrow_len - 1) + '>'

        prog = '\r%6.1f%% [%-75s] Size: %-5s' % (per, arrow, byte_convert(ts))
        print(prog, end='', flush=True)

    try:
        urllib.request.urlretrieve(url, filename, reporthook=dlProgress)
        print()
    except urllib.error.HTTPError:
        return False

    return True


def main():
    print('Setting up...', end=' ', flush=True)
    global COLS, ROWS
    COLS, ROWS = console.getTerminalSize()

    mg = 'Megatokyo'
    if not os.path.isdir(mg):
        os.mkdir(mg)
    os.chdir(mg)
    print('done.')

    print('Downloading info...', end=' ', flush=True)
    search = 'http://megatokyo.com/archive.php?list_by=date'
    soup = getSoup(search)
    print('done.')

    print('Parsing...', end=' ', flush=True)
    found = None
    for div in soup.findAll('div'):
        if div.has_attr('class') and 'content' in div['class'] and div.h2.string == 'Comics by Date':
            found = div
            break
    else:
        print('Error: Could not find list of comics.')
        exit(1)

    titles = [li.a.string for li in found.findAll('li')]
    print('found %d titles.' % len(titles))

    types = ('.gif', '.png', '.jpg')
    files = set()
    for ext in types:
        for file in glob.glob('*' + ext):
            files.add(file)

    url = 'http://megatokyo.com/strips/'
    for title in titles:
        number = title[:4]
        print('Downloading %s...' % number)

        found = False
        downloaded = False
        for ext in types:
            strip = url + number + ext
            fname = fixdir(title + ext)

            if fname in files:
                found = True
                break
            elif downloadb(strip, filename=fname):
                downloaded = True
                break

        if found:
            ANSI.clear(2)
        elif not downloaded:
            print('Error: Could not download \'%s\'', title)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print('User quit')

