# This file is part of Amphetype.

# Amphetype is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Amphetype is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Amphetype.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement, division

import sys

# Get command-line --database argument before importing
# modules which count on database support
from Config import Settings

import optparse
opts = optparse.OptionParser()
opts.add_option("-d", "--database", metavar="FILE", help="use database FILE")
v = opts.parse_args()[0]

if v.database is not None:
    Settings.set('db_name', v.database)

from Data import DB
from Quizzer import Quizzer
from StatWidgets import StringStats
from TextManager import TextManager
from Performance import PerformanceHistory
from Config import PreferenceWidget
from Lesson import LessonGenerator
from Widgets.Database import DatabaseWidget

from PyQt4.QtCore import *
from PyQt4.QtGui import *

QApplication.setStyle('cleanlooks')

class TyperWindow(QMainWindow):
    def __init__(self, *args):
        super(TyperWindow, self).__init__(*args)

        self.setWindowTitle("Amphetype")
        self.setPalette(QPalette(QColor(130,130,135), #color of typing text
                                 QColor(50,50,50),    #background color
                                 Qt.lightGray,
                                 Qt.darkGray,
                                 Qt.gray,
                                 QColor(0,0,0), #color of label text
                                 Qt.white,
                                 Qt.darkGray,
                                 Qt.black)) 
        tabs = QTabWidget()

        quiz = Quizzer()

        tabs.addTab(quiz, "Typer")

        tm = TextManager()
        self.connect(quiz, SIGNAL("wantText"), tm.nextText)
        self.connect(tm, SIGNAL("setText"), quiz.setText)
        self.connect(tm, SIGNAL("gotoText"), lambda: tabs.setCurrentIndex(0))
        self.connect(quiz, SIGNAL("newReview"), tm.newReview)
        self.connect(quiz, SIGNAL("lastText"), tm.lastText)

        tabs.addTab(tm, "Sources")

        ph = PerformanceHistory()
        self.connect(tm, SIGNAL("refreshSources"), ph.refreshSources)
        self.connect(quiz, SIGNAL("statsChanged"), ph.updateData)
        self.connect(ph, SIGNAL("setText"), quiz.setText)
        self.connect(ph, SIGNAL("gotoText"), lambda: tabs.setCurrentIndex(0))
        tabs.addTab(ph, "Performance")

        st = StringStats()
        self.connect(st, SIGNAL("lessonStrings"), lambda x: tabs.setCurrentIndex(4))
        tabs.addTab(st, "Analysis")

        lg = LessonGenerator()
        self.connect(st, SIGNAL("lessonStrings"), lg.addStrings)
        self.connect(lg, SIGNAL("newLessons"), lambda: tabs.setCurrentIndex(1))
        self.connect(lg, SIGNAL("newLessons"), tm.addTexts)
        self.connect(quiz, SIGNAL("wantReview"), lg.wantReview)
        self.connect(lg, SIGNAL("newReview"), tm.newReview)
        tabs.addTab(lg, "Lesson Generator")

        pw = PreferenceWidget()
        pw_scroll = QScrollArea()
        pw_scroll.setWidget(pw)
        tabs.addTab(pw_scroll, "Preferences")

        dw = DatabaseWidget()
        tabs.addTab(dw, "Database")

        ab = AboutWidget()
        tabs.addTab(ab, "About/Help")

        self.setCentralWidget(tabs)

        tm.nextText()

    def sizeHint(self):
        return QSize(650, 400)

class AboutWidget(QTextBrowser):
    def __init__(self, *args):
        html = "about.html file missing!"
        try:
            html = open("about.html", "r").read()
        except:
            pass
        super(AboutWidget, self).__init__(*args)
        self.setHtml(html)
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)

app = QApplication(sys.argv)

w = TyperWindow()
w.show()

app.exec_()

print "exit"
DB.commit()
