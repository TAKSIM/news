# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import datetime
import re
from reader import SourceReader, News
import urlutils

pattern=re.compile('^\d+[u4e00-u9fa5]') # e.g. 2013年, 2月, 13日

class Reuters_FI_CN_News( News ):
    def __init__( self, source, title, link, timestamp, fullContents='' ):
        super(Reuters_FI_CN_News, self).__init__(source,title, link, timestamp, fullContents='')
        if type(self.timestamp) is str:
            self.timestamp = self._parseTimeStamp(self.timestamp)
    
    def _parseTimeStamp( self, ts ):
        '''Expect to be either "hh:mm BJT", or "yyyy年 m月 d日 星期n hh:mm BJT'''
        try:
            info = ts.split()
            if len(info) in [2,6]:
                hour, minute = info[-2].split(':')
                if len(info) == 2:
                    d = datetime.datetime.today()
                else:
                    year = pattern.match(info[0]).group(0)
                    month = pattern.match(info[1]).group(0)
                    day = pattern.match(info[2]).group(0)
                    d = datetime.date(int(year),int(month),int(day))
                return datetime.datetime(d.year,d.month,d.day,int(hour),int(minute),0)
            else:
                raise Exception('Failed to parse timestamp {0}'.format(ts))
        except Exception as e:
            print e.message

    def Retrieve( self ):
        useURL = self.link + '?sp=true' # read full article
        self.contents = []
        try:
            page = urlutils.MakeURLRequest(useURL)
            data = bs(page,"lxml",from_encoding="utf-8")
            lines = data.findAll('span', attrs={'class':'focusParagraph'})
            for l in lines:
                self.contents.append(l.find('p').text)
        except Exception as e:
            self.contents=''
            print e.message
        finally:
            page.close()

class Reuters_FI_CN( SourceReader ):
    '''Reuters fixed-income market news (Chinese)'''
    def __init__( self ):
        super(Reuters_FI_CN, self).__init__(
              rootURL = r'http://cn.reuters.com/investing/news/archive/vbc_cn_bonds')

    def Name(self):
        return u'路透-中国债市'

    def _parse( self, pageData ):
        headlines = pageData.findAll('div',attrs={'class':'headlineMed standalone'})
        self.news = []
        for headline in headlines:
            try:
                body = headline.find(name='a')
                href = body['href']
                title = body.text
                timestamp = headline.find('span',attrs={'class':'timestamp'}).text
                self.news.append(Reuters_FI_CN_News(self.Name(), title, self.rootURL+href, timestamp))
            except Exception as e:
                print e.message
                continue

if __name__ == '__main__':
    src = Reuters_FI_CN()
    src.Read()
    n = src.LatestNews()
    n.Retrieve()
    pass