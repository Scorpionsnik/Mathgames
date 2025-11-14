import sys
import os
import shutil

from no_zag import no_zaag
from try_table import *
from vh_uch import Vhod_uchit
from sozd_ff import Sozd_new_class

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

class zag(QtWidgets.QMainWindow, no_zaag):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.setup_connections()
		self.parent_window = parent
		self.state = None
		self.teacher_login_window = None
		self.sozd_file_window = None
		self.read_mode()

		if self.state == 1:
			self.open_teacher_login()
		else:
			self.setup_connections()
			self.show()

	def setup_connections(self):
		self.pushButton_3.clicked.connect(self.get_file_bd)
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton.clicked.connect(self.new_file)
		# if hasattr(self, 'pushButton_2'):
		# 	# Без disconnect() при первом подключении
		# 	self.pushButton_2.clicked.connect(self.go_back)

	def exit(self):
		QtWidgets.QApplication.instance().quit()

	def new_file(self):
		self.sozd_file_window = Sozd_new_class(parent=self)
		self.sozd_file_window.show()
		self.hide()

	def open_teacher_login(self):
		if not self.teacher_login_window:
			self.teacher_login_window = Vhod_uchit(parent=self)
			self.teacher_login_window.show()
			self.hide()  # Используем hide() вместо close()

	def go_back(self):
		if self.parent_window:
			self.parent_window.close_child_window()
		else:
			self.close()

	def get_file_bd(self):
		path = self.get_file_path()
		if not path:
			return
	
		current_dir = os.path.dirname(os.path.realpath(__file__))
		destination_dir = os.path.join(current_dir, 'Data')
		source_backup_dir = os.path.join(current_dir, 'SourceBackup')
		
		os.makedirs(destination_dir, exist_ok=True)
		os.makedirs(source_backup_dir, exist_ok=True)
		
		new_name = 'vse.db'
		destination_path = os.path.join(destination_dir, new_name)
		source_backup_path = os.path.join(source_backup_dir, new_name)
		
		shutil.copy2(path, destination_path)
		shutil.copy2(path, source_backup_path)
		
		tables_to_check = ['admin', 'uchitelya', 'ucheniki']
		all_tables_exist = True
		
		for table in tables_to_check:
			exists = check_table_exists(table)
			if not exists:
				all_tables_exist = False
		
		if not all_tables_exist:
			self.label.setText("В данной заготовке нету всех необходимых для работы таблиц!")
			self.label_6.setText("Обратитесь к админу для \nсоздания этих таблиц или \nсоздайте новую таблицу\n		 --->")
			return
		
		self.make_ini_zagr_f_ok(destination_path)
		self.open_teacher_login()

	def get_file_path(self):
		file_path, _ = QFileDialog.getOpenFileName(
			self, 
			"Выберите файл с заготовкой",
			"",
			"Базы данных (*.db)"
		)
		if file_path:
			print(f"Выбран файл: {file_path}")
			return file_path
		return None

	def read_mode(self):
		filename = 'sozd_zag.ini'
		dir_path = os.path.dirname(os.path.realpath(__file__))
		path = os.path.join(os.path.join(dir_path, 'Data'), filename)
		
		if os.path.isfile(path):
			with open(path, "r") as fileini:
				content = fileini.read().strip()
				if content == '0':
					self.state = 0
				else:
					self.state = 1
		else:
			print('no file')
			self.make_ini_zagr_f()

	def make_ini_zagr_f(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		folder_path = os.path.join(dir_path, 'Data')
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			print(f"Папка '{folder_path}' создана")
		
		filenameout = 'sozd_zag.ini'
		filepath = os.path.join(folder_path, filenameout)
		with open(filepath, "w") as fout:
			fout.write(str(0))
		self.state = 0

	def close_child_window(self):
		"""Закрывает дочерние окна и показывает текущее"""
		if self.teacher_login_window:
			self.teacher_login_window.close()
			self.teacher_login_window = None
		
		if self.sozd_file_window:
			self.sozd_file_window.close()
			self.sozd_file_window = None
		
		self.show()

	def make_ini_zagr_f_ok(self, path):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		folder_path = os.path.join(dir_path, 'Data')
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			print(f"Папка '{folder_path}' создана")
		
		filenameout = 'sozd_zag.ini'
		filepath = os.path.join(folder_path, filenameout)
		with open(filepath, "w") as fout:
			fout.write(str(1))
		self.state = 1

	def closeEvent(self, event):
		if self.teacher_login_window:
			self.teacher_login_window.close()
		if self.sozd_file_window:
			self.sozd_file_window.close()
		event.accept()