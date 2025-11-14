import sys
import os
import random
from resh_prim import Ui_mainwindow_1
from PyQt5 import QtCore, QtGui, QtWidgets ,uic 

class primer(QtWidgets.QMainWindow, Ui_mainwindow_1):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton_3.clicked.connect(self.exit)
		self.pushButton_4.clicked.connect(self.sled_prim)
		self.pushButton.clicked.connect(self.prov_otv)
		self.pushButton_3.setVisible(False)

	def sled_prim(self):
		self.schit_pr()

	def opr(self, rezh, slozh, chisl_pr):
		self.sl = slozh
		self.rezh = rezh
		self.chisl_pr = chisl_pr + 1
		self.maxi = self.opr_sl(slozh)
		self.mini = 0
		if(rezh == 0):
			self.zn = '+'
		elif(rezh ==1):
			self.zn = '-'
		elif(rezh ==2):
			self.zn = '*'
		elif(rezh ==3):
			self.zn = ':'
		self.konec = 0
		self.schit_pr()
		self.lineEdit.setPlaceholderText("Введите ответ")
		self.lineEdit.setFocus()

	def schit_pr(self):
		self.lineEdit.clear()
		if(self.konec < self.chisl_pr):
			self.pushButton.show()
			self.pushButton_4.show()
			self.pushButton_3.setVisible(False)
			self.konec = self.konec + 1
			self.schit_prim()
		else:
			self.pushButton.hide()
			self.pushButton_4.hide()
			self.pushButton_3.setVisible(True)

	def schit_prim(self):
		if(self.zn == '+'):
			chisl1 = random.randint(self.mini, self.maxi)
			chisl2 = random.randint(self.mini, self.maxi)
			self.otv = chisl1 + chisl2
			text_pr = str(str(chisl1)+str(self.zn)+str(chisl2))
		elif(self.zn == '-'):
			chisl1 = random.randint(1, self.maxi)
			chisl2 = random.randint(self.mini, chisl1)
			self.otv = chisl1 - chisl2
			text_pr = str(str(chisl1)+str(self.zn)+str(chisl2))
		elif(self.zn == '*'):
			chisl1 = random.randint(self.mini, self.maxi)
			chisl2 = random.randint(self.mini, self.maxi)
			self.otv = chisl1 * chisl2
			text_pr = str(str(chisl1)+str(self.zn)+str(chisl2))
		elif(self.zn == ':'):
			chisl1 = random.randint(1, self.maxi)
			chisl2 = chisl1 * random.randint(1, self.maxi)
			self.otv = chisl2 // chisl1
			text_pr = str(str(chisl2)+str(self.zn)+str(chisl1))
		self.label.setText(text_pr)

	def opr_sl(self, sl):
		if(sl == 0):
			return 10
		elif(sl == 1):
			return 50
		elif(sl == 2):
			return 500

	def prov_otv(self):
		otv_us = self.lineEdit.text()
		self.lineEdit.setFocus()
		try:
			otv_us = int(otv_us)
			if(otv_us == self.otv):
				self.lineEdit.clear()
				self.lineEdit.setPlaceholderText("Правильно!")
				self.schit_pr()
				self.lineEdit.setFocus()
			else:
				self.lineEdit.clear()
				self.lineEdit.setPlaceholderText("Неправильно!")
				self.lineEdit.setFocus()
		except:
			self.lineEdit.clear()
			print("ne chislo")
			self.lineEdit.setFocus()
			self.lineEdit.clear()
			self.lineEdit.setPlaceholderText("Не число!")
			

	def exit(self):
		self.close()