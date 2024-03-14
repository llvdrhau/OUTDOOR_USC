# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QCommandLinkButton,
    QGridLayout, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_OUTDOOR(object):
    def setupUi(self, OUTDOOR):
        if not OUTDOOR.objectName():
            OUTDOOR.setObjectName(u"OUTDOOR")
        OUTDOOR.resize(799, 592)
        self.actionOUTDOOR_Hello = QAction(OUTDOOR)
        self.actionOUTDOOR_Hello.setObjectName(u"actionOUTDOOR_Hello")
        self.actionOpen_project = QAction(OUTDOOR)
        self.actionOpen_project.setObjectName(u"actionOpen_project")
        self.actionSave_project = QAction(OUTDOOR)
        self.actionSave_project.setObjectName(u"actionSave_project")
        self.actionClose_project = QAction(OUTDOOR)
        self.actionClose_project.setObjectName(u"actionClose_project")
        self.actionQuit = QAction(OUTDOOR)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionPreferences = QAction(OUTDOOR)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.centralwidget = QWidget(OUTDOOR)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_setup = QWidget()
        self.tab_setup.setObjectName(u"tab_setup")
        self.verticalLayout_3 = QVBoxLayout(self.tab_setup)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.commandLinkButton = QCommandLinkButton(self.tab_setup)
        self.commandLinkButton.setObjectName(u"commandLinkButton")

        self.verticalLayout_3.addWidget(self.commandLinkButton)

        self.checkBox = QCheckBox(self.tab_setup)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout_3.addWidget(self.checkBox)

        self.tabWidget.addTab(self.tab_setup, "")
        self.tab_lca = QWidget()
        self.tab_lca.setObjectName(u"tab_lca")
        self.gridLayout_3 = QGridLayout(self.tab_lca)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tabWidget_lca = QTabWidget(self.tab_lca)
        self.tabWidget_lca.setObjectName(u"tabWidget_lca")
        self.tab_lcaprocess = QWidget()
        self.tab_lcaprocess.setObjectName(u"tab_lcaprocess")
        self.gridLayout_4 = QGridLayout(self.tab_lcaprocess)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.gridLayout.setVerticalSpacing(5)
        self.label_process = QLabel(self.tab_lcaprocess)
        self.label_process.setObjectName(u"label_process")

        self.gridLayout.addWidget(self.label_process, 0, 0, 1, 1)

        self.label_search = QLabel(self.tab_lcaprocess)
        self.label_search.setObjectName(u"label_search")

        self.gridLayout.addWidget(self.label_search, 1, 0, 1, 1)

        self.processCB = QComboBox(self.tab_lcaprocess)
        self.processCB.setObjectName(u"processCB")

        self.gridLayout.addWidget(self.processCB, 0, 1, 1, 1)

        self.lineEdit_processSearch = QLineEdit(self.tab_lcaprocess)
        self.lineEdit_processSearch.setObjectName(u"lineEdit_processSearch")
        self.lineEdit_processSearch.setClearButtonEnabled(False)
        self.lineEdit_processSearch.returnPressed.connect(OUTDOOR.search_Process)

        self.gridLayout.addWidget(self.lineEdit_processSearch, 1, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.searchResultList = QListWidget(self.tab_lcaprocess)
        self.searchResultList.setObjectName(u"searchResultList")

        self.horizontalLayout.addWidget(self.searchResultList)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton = QPushButton(self.tab_lcaprocess)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_2.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.tab_lcaprocess)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_2.addWidget(self.pushButton_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.processList = QListView(self.tab_lcaprocess)
        self.processList.setObjectName(u"processList")

        self.horizontalLayout.addWidget(self.processList)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.tabWidget_lca.addTab(self.tab_lcaprocess, "")
        self.tab_lcaexchanges = QWidget()
        self.tab_lcaexchanges.setObjectName(u"tab_lcaexchanges")
        self.gridLayout_6 = QGridLayout(self.tab_lcaexchanges)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.radioButton_2 = QRadioButton(self.tab_lcaexchanges)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.gridLayout_6.addWidget(self.radioButton_2, 0, 0, 1, 1)

        self.radioButton_3 = QRadioButton(self.tab_lcaexchanges)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.gridLayout_6.addWidget(self.radioButton_3, 0, 1, 1, 1)

        self.radioButton = QRadioButton(self.tab_lcaexchanges)
        self.radioButton.setObjectName(u"radioButton")

        self.gridLayout_6.addWidget(self.radioButton, 1, 1, 1, 1)

        self.tabWidget_lca.addTab(self.tab_lcaexchanges, "")

        self.gridLayout_3.addWidget(self.tabWidget_lca, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_lca, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.gridLayout_5.addLayout(self.verticalLayout, 0, 0, 1, 1)

        OUTDOOR.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(OUTDOOR)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 799, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        OUTDOOR.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(OUTDOOR)
        self.statusbar.setObjectName(u"statusbar")
        OUTDOOR.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuFile.addAction(self.actionOpen_project)
        self.menuFile.addAction(self.actionSave_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose_project)
        self.menuFile.addAction(self.actionQuit)

        self.retranslateUi(OUTDOOR)

        self.tabWidget.setCurrentIndex(1)
        self.tabWidget_lca.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(OUTDOOR)
    # setupUi

    def retranslateUi(self, OUTDOOR):
        OUTDOOR.setWindowTitle(QCoreApplication.translate("OUTDOOR", u"OUTDOOR", None))
        self.actionOUTDOOR_Hello.setText(QCoreApplication.translate("OUTDOOR", u"OUTDOOR Hello", None))
        self.actionOpen_project.setText(QCoreApplication.translate("OUTDOOR", u"Open project", None))
        self.actionSave_project.setText(QCoreApplication.translate("OUTDOOR", u"Save project", None))
        self.actionClose_project.setText(QCoreApplication.translate("OUTDOOR", u"Close project", None))
        self.actionQuit.setText(QCoreApplication.translate("OUTDOOR", u"Quit", None))
        self.actionPreferences.setText(QCoreApplication.translate("OUTDOOR", u"Preferences", None))
        self.commandLinkButton.setText(QCoreApplication.translate("OUTDOOR", u"CommandLinkButton", None))
        self.checkBox.setText(QCoreApplication.translate("OUTDOOR", u"CheckBox", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_setup), QCoreApplication.translate("OUTDOOR", u"Setup", None))
        self.label_process.setText(QCoreApplication.translate("OUTDOOR", u"Process", None))
        self.label_search.setText(QCoreApplication.translate("OUTDOOR", u"Search", None))
        self.lineEdit_processSearch.setPlaceholderText(QCoreApplication.translate("OUTDOOR", u"Enter a process name here", None))
        self.pushButton.setText(QCoreApplication.translate("OUTDOOR", u"Add", None))
        self.pushButton_2.setText(QCoreApplication.translate("OUTDOOR", u"Remove", None))
        self.tabWidget_lca.setTabText(self.tabWidget_lca.indexOf(self.tab_lcaprocess), QCoreApplication.translate("OUTDOOR", u"Processes", None))
        self.radioButton_2.setText(QCoreApplication.translate("OUTDOOR", u"RadioButton", None))
        self.radioButton_3.setText(QCoreApplication.translate("OUTDOOR", u"RadioButton", None))
        self.radioButton.setText(QCoreApplication.translate("OUTDOOR", u"RadioButton", None))
        self.tabWidget_lca.setTabText(self.tabWidget_lca.indexOf(self.tab_lcaexchanges), QCoreApplication.translate("OUTDOOR", u"Exchanges", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_lca), QCoreApplication.translate("OUTDOOR", u"LCA", None))
        self.menuFile.setTitle(QCoreApplication.translate("OUTDOOR", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("OUTDOOR", u"Edit", None))
    # retranslateUi

