import sys
import os
import sqlite3
import shutil  # ДОБАВЛЕНО: импорт shutil

from try_table import *
from PyQt5 import QtCore, QtGui, QtWidgets
from uchitel2_sozd import Uch_sozd_2
from try_table import *

class sozd_new_class(QtWidgets.QMainWindow, Uch_sozd_2):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		self.dannie = dannie
		self.updatde_classes()
		self.comboBox.setCurrentIndex(0)
		self.classes = get_all_classes()
		self.pushButton.clicked.connect(self.prov_sozd)
		self.pushButton_2.clicked.connect(self.exit)
		self.label_6.hide()
		self.label_7.hide()

	def updatde_classes(self):
		ch = len(self.dannie)
		ch = ch - 4
		current_selection = self.comboBox.currentText()
		self.comboBox.clear()
		if ch == 0:
			self.comboBox.addItem("None")
		else:
			# ИСПРАВЛЕНО: правильный диапазон для классов
			for i in range(4, len(self.dannie)):
				if self.dannie[i] is not None:  # Проверяем что значение не None
					self.comboBox.addItem(str(self.dannie[i]))

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

	def validate_class_name(self, class_name):
		"""
		Проверяет корректность названия класса
		Возвращает (is_valid, error_message)
		"""
		# Используем ту же логику, что и для имени
		is_valid, error_message = self.validate_name(class_name)
		
		if not is_valid:
			return False, error_message
		
		# Дополнительные проверки для названия класса
		if len(class_name) < 2:
			return False, "Название класса должно содержать минимум 2 символа"
		
		if len(class_name) > 50:
			return False, "Название класса не может превышать 50 символов"
		
		return True, ""

	def prov_sozd(self):
		if self.radioButton_2.isChecked():
			class_name = self.lineEdit_2.text().strip()
			
			# Правильная проверка на пустоту
			if not class_name:
				self.label_7.show()
				self.label_7.setText("Введите название класса")
				return
				
			# ПРОВЕРКА КОРРЕКТНОСТИ ИМЕНИ КЛАССА
			is_valid, error_message = self.validate_class_name(class_name)
			if not is_valid:
				self.label_7.show()
				self.label_7.setText(error_message)
				return
				
			if check_table_exists(class_name):
				self.label_7.show()
				self.label_7.setText("Такой класс уже существует")
			else:
				current_count = self.dannie[3] if self.dannie[3] is not None else 0
				new_count = current_count + 1
				
				# ВСЕГДА создаем таблицу класса
				make_table_class(class_name)
				update_uchitel_class_count(self.dannie[1], new_count)
				
				conn = sqlite3.connect('Data/vse.db')
				cursor = conn.cursor()
				
				if new_count == 1:
					# Исправлено: используем self.dannie[1] вместо uchitel
					cursor.execute("UPDATE uchitelya SET class0 = ? WHERE name = ?", 
								(class_name, self.dannie[1]))
				else:
					cursor.execute("PRAGMA table_info(uchitelya)")
					columns = cursor.fetchall()
					class_columns = [col[1] for col in columns if col[1].startswith('class')]
					num_class_columns = len(class_columns)
					new_class_column = f"class{num_class_columns}"
					
					cursor.execute(f"ALTER TABLE uchitelya ADD COLUMN {new_class_column} TEXT")
					cursor.execute(f"UPDATE uchitelya SET {new_class_column} = ? WHERE name = ?", 
								(class_name, self.dannie[1]))
				
				conn.commit()
				conn.close()
				self.backup_database()
				self.label_7.show()
				self.label_7.setText("Класс успешно создан")
				self.label_7.setStyleSheet("color: green")
				self.dannie = read_uchitel_parol(self.dannie[1])
				self.updatde_classes()
		
		elif self.radioButton.isChecked():
			name_uch = self.lineEdit.text().strip()
			if not name_uch:
				self.label_7.show()
				self.label_7.setText("Введите Nik ученика")
				return
			
			# ПРОВЕРКА КОРРЕКТНОСТИ ИМЕНИ УЧЕНИКА
			is_valid, error_message = self.validate_name(name_uch)
			if not is_valid:
				self.label_7.show()
				self.label_7.setText(error_message)
				return
				
			if find_by_name('ucheniki', name_uch):
				self.label_7.show()
				self.label_7.setText("Такой ученик уже существует")
				return
			par_uch =  self.lineEdit_3.text().strip()
			if not par_uch:
				self.label_7.show()
				self.label_7.setText("Введите пароль ученика")
				return
			try:
				par_uch = int(par_uch)
			except:
				self.label_7.show()
				self.label_7.setText("Пароль должен быть целочисленным")
				return
			clas_s = self.comboBox.currentText()
			add_uchenik(name_uch, par_uch, str(1))
			if clas_s == 'None':
				pass
			else:
				user = find_by_name('ucheniki', name_uch)
				conn = sqlite3.connect('Data/vse.db')
				cursor = conn.cursor() 
				
				# ИСПРАВЛЕННАЯ РАСПАКОВКА - 8 полей
				user_id, user_name, user_parol, user_nikname, user_ocenka, user_rezh, user_max_number, user_grading_criteria = user
				
				cursor.execute(f"INSERT INTO {clas_s} (id_v_classe, id_uchenika, name, ocenka0) VALUES (NULL, ?, ?, ?)", 
							(user_id, user_name, user_ocenka))
				print("uchenik dobavlen")
				conn.commit()
				conn.close()
				self.backup_database()
		else:
			self.label_7.show()
			self.label_7.setText("Выберите объект, который будете создавать")
		self.dannie = read_uchitel_parol(self.dannie[1])

	def backup_database(self):
		"""Создает резервную копию базы данных"""
		try:
			current_dir = os.path.dirname(os.path.realpath(__file__))
			source_path = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')
			backup_path = os.path.join(os.path.join(current_dir, 'SourceBackup'), 'vse.db')
			
			# Создаем папку если нет
			os.makedirs(os.path.dirname(backup_path), exist_ok=True)
			
			# Копируем файл
			shutil.copy2(source_path, backup_path)
			print("Резервная копия базы данных создана")
			
		except Exception as e:
			print(f"Ошибка при создании резервной копии: {e}")

	def exit(self):
		if self.parent_window:
			self.parent_window.show()
		self.close()

	def closeEvent(self, event):
		if self.parent_window:
			self.parent_window.show()
		event.accept()