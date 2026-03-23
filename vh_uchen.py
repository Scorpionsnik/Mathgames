import sys
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from try_table import *
from uuuchen1 import uuuchenik1

from vhod_uchenik import Vh_uuuuuuch

class Vhod_v_uchenika(QtWidgets.QMainWindow, Vh_uuuuuuch):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		self.label_4.hide()
		self.pushButton_2.clicked.connect(lambda: self.on_back(parent))
		self.pushButton.clicked.connect(self.prov_parol)
		self.setWindowFlags(QtCore.Qt.Window)
		self.uuuchenik_window = None

	def prov_parol(self):
		name = self.lineEdit.text()
		dannie = read_uchenik_parol(name)
		if dannie is None:
			self.label_4.show()
			self.lineEdit.clear()
			self.lineEdit_2.clear()
			print("1")
		else:
			print("3")
			if str(dannie[2]) == self.lineEdit_2.text():
				print("voshel")
				self.uuuchenik_window = uuuchenik1(dannie, parent=self)
				# self.uuuchenik_window = uuuchenik1(dannie, parent=self)
				self.uuuchenik_window.setWindowFlags(QtCore.Qt.Window)
				self.uuuchenik_window.show()
				self.hide()
			else:
				print("2")
				self.label_4.show()
				self.lineEdit.clear()
				self.lineEdit_2.clear()

	def on_back(self, parent):
		self.close()
		parent.close()
		# QtWidgets.QApplication.instance().quit()

	def close_child_window(self):
		if hasattr(self, 'a') and self.a:
			self.a.close()
			self.a = None
		self.show()

	def closeEvent(self, event):
		if self.uuuchenik_window:
			self.uuuchenik_window.close()
		self.parent_window.close()
		event.accept()
