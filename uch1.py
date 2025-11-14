import sys
import os

from try_table import *
from PyQt5 import QtCore, QtGui, QtWidgets
from uchitel1 import uchit1
from uch_prosmotr import TeacherViewWindow
from sozd_uch_uch2 import sozd_new_class

class uchitell1(QtWidgets.QMainWindow, uchit1):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		self.dannie = dannie
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton_3.clicked.connect(self.sozd)
		self.pushButton.clicked.connect(self.prosm)
		self.setWindowFlags(QtCore.Qt.Window)  # Делаем окно независимым

	def prosm(self):
		self.dannie = read_uchitel_parol(self.dannie[1])
		a = TeacherViewWindow(parent = self, teacher_data = self.dannie)
		a.setWindowFlags(QtCore.Qt.Window)  # Делаем дочернее окно независимым
		a.show()

	def sozd(self):
		self.dannie = read_uchitel_parol(self.dannie[1])
		a = sozd_new_class(self.dannie, parent=self)
		a.setWindowFlags(QtCore.Qt.Window)  # Делаем дочернее окно независимым
		a.show()
		# Не скрываем текущее окно

	def exit(self):
		if self.parent:
			self.parent.show()
		self.close()

	def closeEvent(self, event):
		if self.parent:
			self.parent.show()
		event.accept()