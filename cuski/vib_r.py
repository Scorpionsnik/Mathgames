import sys
import os

from primer import primer

from PyQt5 import QtCore, QtGui, QtWidgets
# from resh_prim import Ui_mainwindow_1
from viber_rezh import Ui_MainWindow

class viberr_rezhh(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton.clicked.connect(self.prov_rezh)
		self.window1 = primer()
		self.window1.hide()

	def prov_rezh(self):
		index0 = self.comboBox.currentIndex()
		index1 = self.comboBox_3.currentIndex()
		index2 = self.comboBox_2.currentIndex()
		self.window1.show()
		self.window1.opr(index0, index1, index2)

	def exit(self):
		self.close()