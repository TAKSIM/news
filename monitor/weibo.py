# -*- coding: utf-8 -*-
from reader import SourceReader, News
from selenium import webdriver

# weibo authentication changes frequently. use web automation is much stable. 

class WeiboMonitor( SourceReader ):
    def __init__( self, uid ):
        super(WeiboMonitor, self).__init__(rootURL='http://e.weibo.com')
        self.rootURL += '/u/' + uid
        self.driver = None
    
    def _connect( self ):
        if not self.driver:
            self.driver = webdriver.Firefox()
            self.driver.get(self.rootURL)

    def _kill( self ):
        if self.driver:
            self.driver.close()

    def Read( self ):
        self._connect()
        self.driver.refresh()
        posts = self.driver.find_elements_by_xpath("//dl[@action-type='feed_list_item']")
        for post in posts:
            if post.get_attribute("isforward") == u'1':
                continue    # do not care about forwarded post
            lines = post.text.split('\n')
            # expect 3*n lines, where n is number of posts.
            # each post, first line is contents, second line is statistics, third line is time stamp
            if len(lines) % 3 == 0:
                for i in xrange(len(lines)/3):
                    title = lines[3*i]
                    timestamp = lines[3*i+2].split()[0]
                    self.news.append(WeiboPost(self.Name(), title, self.rootURL, timestamp))
            else:
                raise Exception('Weibo returned expected contents: {0}.'.format(posts))

class WeiboPost( News ):
    def __init__(self, source, title, link, timestamp):
        super(WeiboPost, self).__init__(source, title, link, timestamp)

class WeiboPBOC( WeiboMonitor ):
    def __init__( self ):
        super(WeiboPBOC, self).__init__(uid='3921015143')

    def Name(self):
        return '央行微博'

if __name__ == '__main__':
    m = WeiboPBOC()
    m.Read()
    m._kill()