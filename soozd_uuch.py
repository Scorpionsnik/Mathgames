import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from sozd_uch import Sozd_uch
from try_table import *

class Sozd_uchitel(QtWidgets.QMainWindow, Sozd_uch):
	def __init__(self, num_uch, vsego_uch, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		self.num_uch = num_uch
		self.vsego_uch = vsego_uch
		self.label_5.setText(f'''<html><head/><body><p align="right"> {self.num_uch} </p></body></html>''')
		self.label_6.setText(f'''<html><head/><body><p align="left"> {self.vsego_uch} </p></body></html>''')
		self.label_8.hide()
		self.label_9.hide()
		self.pushButton.clicked.connect(self.next)
		self.setWindowFlags(QtCore.Qt.Window)  # Делаем окно независимым

	def validate_name(self, name):
		"""
		Проверяет корректность имени/названия класса
		Возвращает (is_valid, error_message)
		"""
		if not name or not name.strip():
			return False, "Имя не может быть пустым"
		
		# Проверяем, что имя не начинается с пробела
		if name.startswith(' '):
			return False, "Имя не может начинаться с пробела"
		
		# Проверяем, что имя не заканчивается на пробел
		if name.endswith(' '):
			return False, "Имя не может заканчиваться на пробел"
		
		# Проверяем, что имя не начинается с цифры
		if name[0].isdigit():
			return False, "Имя не может начинаться с цифры"
		
		# Проверяем на наличие только допустимых символов
		if not all(c.isalnum() or c.isspace() or c in '-_.' for c in name):
			return False, "Имя содержит недопустимые символы"
		
		if len(name) > 50:
			return False, "Имя не может превышать 50 символов"
		
		return True, ""

	def next(self):
		uch_name = self.lineEdit.text().strip()
		uch_par = self.lineEdit_2.text().strip()
		self.label_8.hide()
		self.label_9.hide()
		
		if not uch_name or not uch_par:
			self.label_8.setText("Имя учителя или пароль не могут быть пустыми!")
			self.label_8.show()
			return
		
		# ПРОВЕРКА КОРРЕКТНОСТИ ИМЕНИ УЧИТЕЛЯ
		is_valid, error_message = self.validate_name(uch_name)
		if not is_valid:
			self.label_8.setText(f"Ошибка в имени: {error_message}")
			self.label_8.show()
			return
		
		sush_uch = find_by_name('uchitelya', uch_name)
		if sush_uch is not None:
			self.label_8.setText("Такой учитель уже существует")
			self.label_8.show()
			return
		
		try:
			uch_par = int(uch_par)
			add_uchitel(uch_name, uch_par)
			self.close()  # Закрываем окно после успешного добавления
		except ValueError:
			self.label_9.setText("Пароль должен быть целочисленным!")
			self.label_9.show()
		except Exception as e:
			self.label_8.setText(f"Ошибка: {e}")
			self.label_8.show()
		if self.num_uch == self.vsego_uch:
			QtWidgets.QApplication.instance().quit()

	def closeEvent(self, event):
		if self.parent_window:
			self.parent_window.show()
		event.accept()