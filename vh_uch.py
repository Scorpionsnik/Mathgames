import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from vhod_uchitel import vhod_uch
from uch1 import uchitell1
from try_table import *

class Vhod_uchit(QtWidgets.QMainWindow, vhod_uch):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		parent.hide()
		self.label_4.hide()
		self.pushButton_2.clicked.connect(lambda: self.on_back(parent))
		self.pushButton.clicked.connect(self.prov_parol)
		
		# Правильные флаги для отдельного окна в панели задач
		self.setWindowFlags(QtCore.Qt.Window)

	def prov_parol(self):
		name = self.lineEdit.text()
		dannie = read_uchitel_parol(name)
		if dannie is None:
			self.label_4.show()
			self.lineEdit.clear()
			self.lineEdit_2.clear()
		else:
			if str(dannie[2]) == self.lineEdit_2.text():
				print("voshel")
				self.a = uchitell1(dannie, parent=self)
				# Убираем модальность и устанавливаем правильные флаги
				self.a.setWindowFlags(QtCore.Qt.Window)
				self.a.show()
				self.hide()
			else:
				self.label_4.show()
				self.lineEdit.clear()
				self.lineEdit_2.clear()

	def on_back(self, parent):
		self.close()
		parent.close()

	def close_child_window(self):
		"""Закрывает дочерние окна (например, окно учителя)"""
		if hasattr(self, 'a') and self.a:
			self.a.close()
			self.a = None

	def closeEvent(self, event):
		self.parent.close()
		event.accept()

