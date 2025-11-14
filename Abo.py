import os
import sys

from About import Ui_MainWindow_About
from zag3 import zag3
from PyQt5 import QtCore, QtGui, QtWidgets

class Abouut(QtWidgets.QMainWindow, Ui_MainWindow_About):
	def __init__(self, parent=None):
		super().__init__()
		self.setupUi(self)
		self.parent_window = parent
		self.pushButton.clicked.connect(self.admin)
		self.pushButton_2.clicked.connect(self.exit)

	def admin(self):
		print("Admin Adminovich")
		self.a = zag3(parent = self)
		self.a.show()
		self.a.setWindowFlags(QtCore.Qt.Window)
		self.hide()

	def exit(self):
		self.close()