import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from start import start_win
from rereresh_pr import pr_na_ocenku
from rere_prim import proba_prohozhdeniya
from try_table import *

class ststart(QtWidgets.QMainWindow, start_win):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		self.dannie = dannie
		self.showFullScreen()
		self.pushButton.clicked.connect(self.exit)
		self.pushButton_3.clicked.connect(self.start_no)
		self.pushButton_2.clicked.connect(self.start_oc)
		self.setWindowFlags(QtCore.Qt.Window)
		self.stile_knopki()

	def start_oc(self):
		aa = pr_na_ocenku(self.dannie, parent = self)
		aa.show()
		self.hide()

	def stile_knopki(self):
		"""Применяет стили кнопок как в ucenik1.py"""
		
		# Зеленый стиль для кнопки "Попробовать примеры" (как "Начать занятия")
		practice_style = """
			QPushButton {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #11998e, stop: 1 #38ef7d);
				color: white;
				border: none;
				border-radius: 20px;
				padding: 25px 40px;
				font-size: 28px;
				font-weight: bold;
				font-family: 'Segoe UI', Arial, sans-serif;
				min-width: 300px;
				min-height: 90px;
			}
			QPushButton:hover {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #0f8a7f, stop: 1 #32d46b);
			}
			QPushButton:pressed {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #0d7b70, stop: 1 #2cc159);
				padding: 26px 41px 24px 39px;
			}
		"""
		
		# Красный стиль для кнопки "Назад" (как "Выход")
		exit_style = """
			QPushButton {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #ff9a9e, stop: 1 #fad0c4);
				color: #333;
				border: none;
				border-radius: 20px;
				padding: 25px 40px;
				font-size: 28px;
				font-weight: bold;
				font-family: 'Segoe UI', Arial, sans-serif;
				min-width: 300px;
				min-height: 90px;
			}
			QPushButton:hover {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #ff8a8e, stop: 1 #f8c0b4);
			}
			QPushButton:pressed {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #ff7a7e, stop: 1 #f6b0a4);
				padding: 26px 41px 24px 39px;
			}
		"""
		
		# Основной стиль для кнопки "Начать прохождение"
		main_style = """
			QPushButton {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #667eea, stop: 1 #764ba2);
				color: white;
				border: none;
				border-radius: 20px;
				padding: 25px 40px;
				font-size: 28px;
				font-weight: bold;
				font-family: 'Segoe UI', Arial, sans-serif;
				min-width: 300px;
				min-height: 90px;
			}
			QPushButton:hover {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #5a6fd8, stop: 1 #6a4190);
			}
			QPushButton:pressed {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
									stop: 0 #4c5bc4, stop: 1 #5c377e);
				padding: 26px 41px 24px 39px;
			}
		"""
		
		# Применяем стили к конкретным кнопкам
		self.pushButton_2.setStyleSheet(main_style)	  # "Начать прохождение"
		self.pushButton_3.setStyleSheet(practice_style)  # "Попробовать примеры" 
		self.pushButton.setStyleSheet(exit_style)  

	def start_no(self):
		print("start none")
		a = proba_prohozhdeniya(self.dannie, parent=self)
		a.show()
		self.hide()

	def exit(self):
		if self.parent:
			self.parent.show()
		self.close()

	def closeEvent(self, event):
		if self.parent:
			self.parent.show()
		event.accept()