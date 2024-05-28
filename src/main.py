# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_v1.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1218, 810)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(20, 20, 1121, 731))
        self.skiu1 = QWidget()
        self.skiu1.setObjectName(u"skiu1")
        self.connect_btn = QPushButton(self.skiu1)
        self.connect_btn.setObjectName(u"connect_btn")
        self.connect_btn.setGeometry(QRect(10, 140, 121, 23))
        self.close_btn = QPushButton(self.skiu1)
        self.close_btn.setObjectName(u"close_btn")
        self.close_btn.setGeometry(QRect(10, 180, 121, 23))
        self.send_btn = QPushButton(self.skiu1)
        self.send_btn.setObjectName(u"send_btn")
        self.send_btn.setGeometry(QRect(630, 160, 121, 23))
        self.btn1 = QPushButton(self.skiu1)
        self.btn1.setObjectName(u"btn1")
        self.btn1.setGeometry(QRect(20, 490, 75, 23))
        self.btn2 = QPushButton(self.skiu1)
        self.btn2.setObjectName(u"btn2")
        self.btn2.setGeometry(QRect(20, 530, 75, 23))
        self.btn3 = QPushButton(self.skiu1)
        self.btn3.setObjectName(u"btn3")
        self.btn3.setGeometry(QRect(20, 570, 75, 23))
        self.btn4 = QPushButton(self.skiu1)
        self.btn4.setObjectName(u"btn4")
        self.btn4.setGeometry(QRect(20, 610, 75, 23))
        self.sn_lineEdit = QLineEdit(self.skiu1)
        self.sn_lineEdit.setObjectName(u"sn_lineEdit")
        self.sn_lineEdit.setGeometry(QRect(90, 90, 101, 20))
        self.lineEdit_2 = QLineEdit(self.skiu1)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(640, 30, 113, 20))
        self.label = QLabel(self.skiu1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 90, 31, 21))
        self.label_2 = QLabel(self.skiu1)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(560, 30, 47, 21))
        self.out_list = QListWidget(self.skiu1)
        self.out_list.setObjectName(u"out_list")
        self.out_list.setGeometry(QRect(360, 210, 391, 481))
        self.state_lbl = QLabel(self.skiu1)
        self.state_lbl.setObjectName(u"state_lbl")
        self.state_lbl.setGeometry(QRect(170, 150, 41, 41))
        self.state_lbl.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(255, 170, 0);\n"
"}")
        self.r1_deley_lineEdit = QLineEdit(self.skiu1)
        self.r1_deley_lineEdit.setObjectName(u"r1_deley_lineEdit")
        self.r1_deley_lineEdit.setGeometry(QRect(130, 490, 51, 20))
        self.r1_time_lineEdit = QLineEdit(self.skiu1)
        self.r1_time_lineEdit.setObjectName(u"r1_time_lineEdit")
        self.r1_time_lineEdit.setGeometry(QRect(220, 490, 51, 20))
        self.label_3 = QLabel(self.skiu1)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(230, 460, 47, 13))
        self.label_4 = QLabel(self.skiu1)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(140, 460, 41, 16))
        self.input_lineEdit = QLineEdit(self.skiu1)
        self.input_lineEdit.setObjectName(u"input_lineEdit")
        self.input_lineEdit.setGeometry(QRect(360, 130, 391, 20))
        self.label_5 = QLabel(self.skiu1)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 20, 71, 21))
        self.label_6 = QLabel(self.skiu1)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 50, 47, 21))
        self.port_comboBox = QComboBox(self.skiu1)
        self.port_comboBox.setObjectName(u"port_comboBox")
        self.port_comboBox.setGeometry(QRect(90, 20, 291, 22))
        self.speed_comboBox = QComboBox(self.skiu1)
        self.speed_comboBox.setObjectName(u"speed_comboBox")
        self.speed_comboBox.setGeometry(QRect(90, 50, 141, 22))
        self.tabWidget.addTab(self.skiu1, "")
        self.skiu2 = QWidget()
        self.skiu2.setObjectName(u"skiu2")
        self.tabWidget.addTab(self.skiu2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1218, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.connect_btn.setText(QCoreApplication.translate("MainWindow", u"Start / Connect", None))
        self.close_btn.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u0441\u044f", None))
        self.send_btn.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c", None))
        self.btn1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.btn2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.btn3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.btn4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"s/n", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.state_lbl.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0440. \u0441\u0440.", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0434.", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"COM PORT", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.skiu1), QCoreApplication.translate("MainWindow", u"\u0421\u041a\u0418\u0423 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.skiu2), QCoreApplication.translate("MainWindow", u"\u0421\u041a\u0418\u04232", None))
    # retranslateUi

