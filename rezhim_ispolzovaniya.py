import sys
import os

from vhod_multi import *

class opr_mod():
	def __init__(self):
		super().__init__()
		self.read_mode()
		try:
			if not self.state:
				QtWidgets.QApplication.instance().quit()
		except:
			pass
		if self.state == 2:
			self.run_gui()

	def run_gui(self):
		app = QtWidgets.QApplication(sys.argv)
		window = vhod_multi()
		window.show()
		app.exec_()

	def read_mode(self):
		filename='rezh_comp.ini'
		dir_path = os.path.dirname(os.path.realpath(__file__))#<-получает путь к дириктории запуска
		path = os.path.join(os.path.join(dir_path, 'Data'),filename)#<-объединятет путь к директории запуска и имя файла
		if os.path.isfile(path):#<-проверка на существование файла
			fileini=open(path,"r")#<-открытие файла на чтение

			fileini.seek(0,0)#<-перемещение указателя чтения файла на начало файла
			while True:
				stm=fileini.readlines(1)
				if not stm:
					break

				for i in stm:
					if i.find('0')!=-1:
						self.state = 0
					if i.find('1')!=-1:
						self.state = 1
					if i.find('2')!=-1:
						self.state = 2		
			fileini.close

		else:
			print('no file')