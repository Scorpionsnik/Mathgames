import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from hello import Hallo_class

class Hallo_class_class(QtWidgets.QMainWindow, Hallo_class):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.pushButton.clicked.connect(self.vhod)
		self.pushButton_2.clicked.connect(self.exit)
		
	def vhod(self):
		# index = self.comboBox.currentIndex()
		# self.make_ini_start_file(index)
		self.write_ini_start_file_1()
		self.close()

	def write_ini_start_file_1(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))#<-получает путь к дириктории запуска
		folder_path = os.path.join(dir_path,'Data')
		filenameout='start.ini'
		fout=open(os.path.join(os.path.join(dir_path,'Data'),filenameout),"w")
		fout.write('1')
		fout.close
		self.state = 1

	def make_ini_start_file(self, index):
		dir_path = os.path.dirname(os.path.realpath(__file__))#<-получает путь к дириктории запуска
		folder_path = os.path.join(dir_path,'Data')
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			print(f"Папка '{folder_path}' создана")
		else:
			# print(f"Папка '{folder_path}' уже существует")
			pass
		filenameout='rezh_comp.ini'
		fout=open(os.path.join(os.path.join(dir_path,'Data'),filenameout),"w")
		fout.write(str(index))
		fout.close

	def exit(self):
		QtWidgets.QApplication.instance().quit()