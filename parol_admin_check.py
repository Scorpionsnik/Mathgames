import sys
import os
import shutil

from try_table import *
from admin1 import AdminWindow
from vhod_admin import Vhod_Admin

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

class Vh_Adm(QtWidgets.QMainWindow, Vhod_Admin):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setupUi(self)
		self.label_4.hide()
		self.pushButton_2.clicked.connect(lambda: self.go_back(parent))
		self.pushButton.clicked.connect(self.prov_parol)
		self.setWindowFlags(QtCore.Qt.Window)

	def prov_parol(self):
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		id1 = 1
		cursor.execute("SELECT * FROM admin WHERE id = ?", (id1,))
		admin_data = cursor.fetchone()	
		if admin_data is None:
			self.label_4.setText("Администратор не найден")
			self.label_4.show()
			conn.close()
			return
		admin_parol = int(admin_data[1])
		conn.close()
		try:
			us_par = self.lineEdit_2.text()
			if us_par:
				us_par = int(us_par)
			else:
				self.label_4.setText("Введите пароль")
				self.label_4.show()
				return
		except ValueError:
			self.label_4.setText("Пароль должен быть числом")
			self.label_4.show()
			return
		if us_par == admin_parol:
			print("voshel")
			self.a = AdminWindow(parent=self)
			self.a.setWindowFlags(QtCore.Qt.Window)
			self.a.show()
			self.hide()
		else:
			self.label_4.setText("Неверный пароль")
			self.label_4.show()

	def go_back(self, parent):
		self.close()
		parent.close()
		# QtWidgets.QApplication.instance().quit()

	def closeEvent(self, event):
		event.accept()