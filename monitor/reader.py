# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import urlutils

class SourceReader(object):
    def __init__( self, rootURL, parser='lxml', encoding='utf-8' ):
        self.rootURL = rootURL
        self.news = [] # list of news contents
        self.parser = parser
        self.encoding = encoding

    def _parse( self, pageData ):
        raise Exception('Parser not implemented.')

    def Name(self):
        return '未定义'

    def RetrieveFullContents( self ):
        for n in self.news: n.Retrieve()

    def Read( self ):
        page = None
        try:
            page = urlutils.MakeURLRequest(self.rootURL)
            data = bs(page,self.parser,from_encoding=self.encoding)
            self._parse(data)
        except Exception as e:
            return e
        finally:
            if page: page.close()

    def LatestNews( self ):
        if not self.news:
            self.Read()
        return max(self.news, key=lambda n:n.timestamp)

class News(object):
    def __init__( self, srcName, title, link, timestamp, fullContents='' ):
        self.source = srcName
        self.title = title
        self.link = link
        self.timestamp = timestamp
        self.contents = fullContents

    def Retrieve( self ):
        raise Exception('Parser not implemented.')

    def __str__( self ):
        return '['+self.source+']'+self.title

