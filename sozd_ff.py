import sys
import os
import shutil

from PyQt5 import QtCore, QtGui, QtWidgets

from sozd_file import Sozd_f
from soozd_uuch import Sozd_uchitel

from try_table import *

class Sozd_new_class(QtWidgets.QMainWindow, Sozd_f):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		self.label.hide()
		self.label_2.hide()
		self.pushButton.clicked.connect(self.next)
		self.pushButton_2.clicked.connect(self.exit)
		self.setWindowFlags(QtCore.Qt.Window)

	def next(self):
		admin_par = self.lineEdit_3.text()
		if admin_par:
			try:
				admin_par = int(admin_par)
				chisl_uch = self.spinBox_2.value()
				print(f"!!!!!!!!!!!!!!!!!!! parol admina = {admin_par} , chislo uchiteley = {chisl_uch}")
				sozd_admin_table(admin_par)
				make_table_uchenik()
				make_table_uchitelya()

				for i in range(1, chisl_uch + 1):
					teacher_window = Sozd_uchitel(chisl_uch + 1 - i, chisl_uch, parent=self)
					teacher_window.show()

				self.make_ini_zagr_f_ok()
				current_dir = os.path.dirname(os.path.realpath(__file__))
				path_start_file = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')
				new_path_file = os.path.join(os.path.join(current_dir,'SourceBackup'), 'vse.db')
				os.makedirs(os.path.dirname(new_path_file), exist_ok=True)
				shutil.copy2(path_start_file, new_path_file)
				# self.close()
				# QtWidgets.QApplication.instance().quit()

			except ValueError:
				self.label_2.show()
				self.label.hide()

		else:
			self.label.show()
			self.label_2.hide()

	def exit(self):
		if self.parent_window:
			self.parent_window.show()
		self.close()

	def closeEvent(self, event):
		if self.parent_window:
			self.parent_window.show()
		event.accept()

	def make_ini_zagr_f_ok(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		folder_path = os.path.join(dir_path, 'Data')

		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			print(f"Папка '{folder_path}' создана")

		filenameout = 'sozd_zag.ini'
		filepath = os.path.join(folder_path, filenameout)
		
		with open(filepath, "w") as fout:
			fout.write(str(1))