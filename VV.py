import sys
import os
import shutil

from PyQt5 import QtCore, QtGui, QtWidgets
from V import Voskl
from sbros_nast import Sbros_n

class Vooskl(QtWidgets.QMainWindow, Voskl):
	def __init__(self, parent=None):
		super().__init__()
		self.setupUi(self)
		self.parent_window = parent
		self.pushButton.clicked.connect(self.restart)
		self.pushButton_2.clicked.connect(self.exit)

	def restart(self):
		self.a = Sbros_n(parent = self)
		self.a.show()
		self.hide()

	def exit(self):
		self.close()