import sys
import os

from Abo import Abouut
from VV import Vooskl
from vib_r import viberr_rezhh
from zag import zag
from zag2 import zag2

from PyQt5 import QtCore, QtGui, QtWidgets
from vhod_v_user import Ui_MainWindow_vhod_2

class vhod_multi(QtWidgets.QMainWindow, Ui_MainWindow_vhod_2):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		
		self.current_child_window = None
		
		self.pushButton.clicked.connect(lambda: self.open_child_window(zag2))
		self.pushButton_2.clicked.connect(lambda: self.open_child_window(zag))
		self.pushButton_3.clicked.connect(lambda: self.open_child_window(viberr_rezhh))
		self.pushButton_4.clicked.connect(lambda: self.open_child_window(Abouut))
		self.pushButton_5.clicked.connect(lambda: self.open_child_window(Vooskl))
		
		self.setWindowTitle("MathGames - Вход")
	
	def open_child_window(self, window_class):
		if self.current_child_window:
			self.current_child_window.close()
		
		# Создаем независимое окно
		self.current_child_window = window_class(parent=None)
		self.current_child_window.setWindowFlags(QtCore.Qt.Window)
		
		self.current_child_window.show()
		# Главное окно остается открытым
	
	def close_child_window(self):
		if self.current_child_window:
			self.current_child_window.close()
			self.current_child_window = None
	
	def closeEvent(self, event):
		if self.current_child_window:
			self.current_child_window.close()
		event.accept()