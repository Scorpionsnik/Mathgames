import sys
import os

from analiticcc_uchenik import Analitic_uchen
from st import ststart
from ssend import send

from PyQt5 import QtCore, QtGui, QtWidgets
from ucenik1 import uchen1

class uuuchenik1(QtWidgets.QMainWindow, uchen1):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		self.dannie = dannie
		self.showFullScreen()
		self.pushButton_exit.clicked.connect(self.exit)
		self.pushButton_stats.clicked.connect(self.analitic_open)
		self.pushButton_practice.clicked.connect(self.st_open)
		self.pushButton_send_grades.clicked.connect(self.send)
		self.analitic_window = None
		self.st_window = None

	def st_open(self):
		a = ststart(self.dannie, parent = self)
		a.show()
		self.hide()

	def analitic_open(self):
		a = Analitic_uchen(self.dannie, parent = self)
		a.show()
		self.hide()

	def send(self):
		a = send(self.dannie, parent = self)
		a.show()
		self.hide()

	def exit(self):
		self.close()

	def close_child_window(self):
		if self.analitic_window:
			self.analitic_window.close()
			self.analitic_window = None
		if self.st_window:
			self.st_window.close()
			self.st_window = None
		self.show()

	def closeEvent(self, event):
		if self.analitic_window:
			self.analitic_window.close()
		if self.st_window:
			self.st_window.close()
		event.accept()