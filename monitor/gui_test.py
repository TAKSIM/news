# -*- coding: utf-8 -*-
from PyQt4 import QtGui as qg
import PyQt4
import sys

class Example( qg.QWidget ):
    def __init__( self ):
        super(Example,self).__init__()
        PyQt4.QtCore.QTextCodec.setCodecForTr(PyQt4.QtCore.QTextCodec.codecForName('GB18030'))
        self.init()

    def init( self ):
        qg.QToolTip.setFont(qg.QFont("SansSerif",10))
        self.setToolTip(self.tr(u'show tool tip <b>帮助</b>!'))
        b = qg.QPushButton(self.tr(u'帮助'),self)
        b.setToolTip(self.tr(u'button t<b>尼玛</b>tip'))
        b.resize(b.sizeHint())
        self.setWindowTitle('Window title')
        self.show()


def show():
    app = qg.QApplication(sys.argv)
    e = Example()

    sys.exit(app.exec_())

if __name__ == '__main__':
    show()
