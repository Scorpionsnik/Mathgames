import sys
import os

from vichesleniya import EquationGenerator

from PyQt5 import QtCore, QtGui, QtWidgets
from resh_prim import Ui_mainwindow_1
from try_table import *

class proba_prohozhdeniya(QtWidgets.QMainWindow, Ui_mainwindow_1):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		self.dannie = dannie
		self.showFullScreen()
		self.label_4.hide()
		self.label_3.hide()
		self.label_3.setAlignment(QtCore.Qt.AlignCenter)
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton.clicked.connect(self.prov_resh)
		self.pushButton_4.clicked.connect(self.start)
		self.start()

	def start(self):
		self.lineEdit.setFocus()
		generator = EquationGenerator()
		self.lineEdit.clear()
		# rezh_value = student_data[5]
		self.rezh = self.dannie[5]
		equation, steps, answer = generator.generate_from_extended_mode(self.rezh)
		self.answer = answer
		print(self.answer)
		self.label.setText(str(equation))

	def prov_resh(self):
		otvet = self.lineEdit.text()
		try:
			otvet = int(otvet)
		except:
			self.label_3.show()
			self.lineEdit.setFocus()
			self.lineEdit.clear()
			self.label_3.setText('!НЕ ЧИСЛО!')
			self.label_3.setStyleSheet("""
				QLabel {
					background-color: transparent;
					color: #3498db;
					font-size: 25px;
					font-weight: bold;
					border: none;
					text-align: center;
				}
			""")
			return
		if otvet == self.answer:
			self.lineEdit.setFocus()
			self.label_3.show()
			self.label_3.setText('!ВЕРНО!')
			self.label_3.setStyleSheet("""QLabel {
				background-color: transparent;
				color: #2ecc71;
				font-size: 25px;
				font-weight: bold;
				border: none;
			}""")
			self.start()
		else:
			self.lineEdit.setFocus()
			self.label_3.show()
			self.label_3.setStyleSheet("""QLabel {
				background-color: transparent;
				color: #e74c3c;
				font-size: 25px;
				font-weight: bold;
				border: none;
			}""")
			self.label_3.setText(f'!НЕВЕРНО! Правильный ответ: {self.answer}')
		self.start()


	def exit(self):
		if self.parent:
			self.parent.show()
		self.close()

	def closeEvent(self, event):
		if self.parent:
			self.parent.show()
		event.accept()