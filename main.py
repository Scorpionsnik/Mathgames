import sys
import os

from hel import *

from vhod_multi import *

from PyQt5 import QtCore, QtGui, QtWidgets ,uic 

class main():
	def __init__(self):
		super().__init__()
		# print(os.getcwd())
		# print("123")
		self.find_zagr_file()
		
		if self.state == 0:
			self.run_gui()
		else:
			self.run_main_app()
		

	def run_main_app(self):
		app = QtWidgets.QApplication(sys.argv)
		main_window = vhod_multi()
		main_window.show()
		app.exec_()

	def run_gui(self):
		app = QtWidgets.QApplication(sys.argv)
		main_window = vhod_multi()
		window = Hallo_class_class(main_window)
		window.show()
		app.exec_()  
		# self.run_main_app()      

	def find_zagr_file(self):
		filename='start.ini'
		# dir_path = ".\\"#<-получает путь к дириктории запуска
		dir_path = ".\\"
		path = os.path.join(os.path.join(dir_path, 'Data'),filename)#<-объединятет путь к директории запуска и имя файла
		print(dir_path)
		print(path)
		if os.path.isfile(path):#<-проверка на существование файла
			fileini=open(path,"r")#<-открытие файла на чтение

			fileini.seek(0,0)#<-перемещение указателя чтения файла на начало файла
			while True:
				stm=fileini.readlines(1)#<-прочитать одну строчку
				# print(stm)
				if not stm:
					break

				for i in stm:
					# print(i)
					if i.find('1')!=-1:
						self.state = 1
					if i.find('0')!=-1:
						self.state = 0		
			fileini.close

		else:
			print('no start file')
			self.make_ini_start_file()

	def make_ini_start_file(self):
		# dir_path = ".\\"#<-получает путь к дириктории запуска
		dir_path = ".\\"
		folder_path = os.path.join(dir_path, 'Data')
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			print(f"Папка '{folder_path}' создана")
		else:
			print(f"Папка '{folder_path}' уже существует")
		filenameout='start.ini'
		fout=open(os.path.join(os.path.join(dir_path, 'Data'),filenameout),"w")
		fout.write('0')
		fout.close
		self.state = 0

a = main()