import sys
import os
import shutil

from try_table import *
# from zag4 import zag4
from PyQt5 import QtCore, QtGui, QtWidgets
from vhod_admin import Vhod_Admin

class Sbros_n(QtWidgets.QMainWindow, Vhod_Admin):
	def __init__(self, parent=None):
		super().__init__()
		self.setupUi(self)
		self.label_4.hide()
		self.pushButton.setText("Сброс")
		self.parent_window = parent
		self.pushButton.clicked.connect(self.prov)
		self.pushButton_2.clicked.connect(lambda: self.exit(parent))
		# a = zag4(parent = self)
		# a.show()
		# self.hide()

	def prov(self):
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
			self.rest()
		else:
			self.label_4.setText("Неверный пароль")
			self.label_4.show()

	def rest(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		folder_path = os.path.join(dir_path, 'Data')
		folder_path_1 = os.path.join(dir_path, 'SourceBackup')
		if os.path.exists(folder_path) and os.path.isdir(folder_path):
			try:
				shutil.rmtree(folder_path)
				shutil.rmtree(folder_path_1)
				print(f"Папка и всё её содержимое удалены")
				# return True
				QtWidgets.QApplication.instance().quit()
			except Exception as e:
				print(f"Ошибка при удалении папки '': {e}")
				return False
		else:
			print(f"Папка '' не существует")
			return False

	def exit(self, parent):
		self.close()
		parent.show()