import cStringIO
import gzip
import httplib
import os
import re
import socket
import sys
import time
import urllib
import urllib2
import urlparse

FILE_RE = re.compile(r'href\s*="([^"]+)"', re.IGNORECASE)

def MakeURLRequest(urlList, data=None, headers={}, timeoutInSecs=60, maxRetries=5, retryDelayInSecs=60, proxies=None, unzip=False, debug=False, sanitise_url=False):
    '''Send URL request and returns File-like results'''
    urlList = isinstance(urlList,list) and urlList or [urlList]

    if debug:
        httplib.HTTPConnection.debuglevel = 1
    else:
        httplib.HTTPConnection.debuglevel = 0

    if timeoutInSecs: socket.setdefaulttimeout( timeoutInSecs )
    if data and type(data) is not str:
        data = urllib.urlencode(data)

    if not headers or not isinstance(headers,dict):
        headers = {}

    retries = 0
    while retries <= maxRetries:
        try:
            for i, url in enumerate(urlList):
                try:
                    i += 1
                    print 'MakeURLRequest: Requesting {0}'.format(url)
                    url = urlSafeEncode(url, spaces_only=(not sanitise_url))
                    request = urllib2.Request(url,data=data,headers=headers)
                    opener = None
                    if proxies is not None:
                        proxy_handler = urllib2.ProxyHandler(proxies)
                        opener = urllib2.build_opener( proxy_handler )
                    else:
                        opener = urllib2.build_opener()
                    feeddata = opener.open(request)
                    if unzip and feeddata.info().get('content-encoding')=='gzip':
                        feeddata=gzip.GzipFile(fileobj=cStringIO.StringIO(feeddata.read()))
                    return feeddata
                except:
                    exctype, value.message = sys.exc_info()[:2]
                    print "MakeURLRequest: Failed for url {0} with exception {1} and message.".format(url, exctype, value)
                    if i==len(urlList):
                        raise # All servers failed
        except:
            exctype, value = sys.exc_info()[:2]
            retries += 1
            if retries > maxRetries:
                raise IOError, "MakeURLRequest: Max retries {0} exceeded attempting to request urls {1}".format(maxRetries,urlList)
            time.sleep( retryDelayInSecs )

def listdir( url ):
    data = urllib.urlopen(url).read()
    files = [os.path.normpath(urllib.unquote(x)) for x in re.findall(FILE_RE,data)]
    return [x for x in files if not x.startswith('.nfs') and x not in ('.','..',)]

def checkURL( url, robust=False, timeout=5.0 ):
    '''checks whether the given url exists on the server, without actually downloading the file'''
    p=urlparse.urlparse(url)
    h=httplib.HTTPConnection(p[1], timeout=timeout) # all socket ops henceforth will timeout in timeout secs
    try:
        h.putrequest('HEAD',p[2])
        h.endheaders()
        resp = h.getresponse()
        if resp.status==200:
            read=True
            if robust:
                read=bool(urllib.urlopen(url).read(100))
            return read or not robust
        else:
            return False
    except Exception as e:
        print 'exception in url.checkURL : {0}'.format(e)
        return False

def isValidUrl( url ):
    ''' checks whether the given string in url is a valid http url'''
    p = urlparse.urlparse(url)
    if p.scheme=='http' and p.netloc:
        return True
    else:
        return False

def urlSafeEncode(url, spaces_only=False, charset='utf-8'):
    '''
    Sanitise user-supplied URLs that contain unsafe characters like ' ', '(', ')', in addition to taking care of unicode strings
    containing non-ascii characters
    '''
    if spaces_only:
        return url.replace(' ', '%20')
    else:
        if isinstance(url, unicode):
            url = url.encode(charset,'ignore')
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(url)
        path = urllib.quote(path,'/%')
        qs = urllib.quote_plus(qs,':&=')

        return urlparse.urlunsplit((scheme,netloc,path,qs,anchor))
