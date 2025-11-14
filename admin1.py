import sys
import os
import sqlite3
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets

# Импортируем сгенерированный UI файл
from admin_panel import admin_panel

class AdminWindow(QtWidgets.QMainWindow, admin_panel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		
		# Подключаем кнопки
		self.pushButton_sozd_uchitel.clicked.connect(self.sozdanie_uchitelya)
		self.pushButton_udalit_uchitel.clicked.connect(self.udalenie_uchitelya)
		self.pushButton_sozd_uchenik.clicked.connect(self.sozdanie_uchenika)
		self.pushButton_udalit_uchenik.clicked.connect(self.udalenie_uchenika)
		self.pushButton_prosmotr.clicked.connect(self.prosmotr_vseh)
		self.pushButton_backup.clicked.connect(self.sozdanie_backup)
		self.pushButton_backup_custom.clicked.connect(self.sozdanie_backup_custom)
		self.pushButton_exit.clicked.connect(self.exit)
		
		# Загружаем список классов при инициализации
		self.load_all_classes()
		
		# Устанавливаем флаги для независимого окна
		self.setWindowFlags(QtCore.Qt.Window)
		
	def load_all_classes(self):
		"""Загружает все существующие классы из базы данных"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			
			# Получаем все таблицы (классы) из базы данных
			cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
			tables = cursor.fetchall()
			
			# Фильтруем только таблицы классов (исключаем системные таблицы)
			classes = []
			for table in tables:
				table_name = table[0]
				if (table_name not in ['uchitelya', 'ucheniki', 'sqlite_sequence'] and 
					not table_name.startswith('sqlite_')):
					classes.append(table_name)
			
			conn.close()
			
			# Заполняем ComboBox
			self.comboBox_class.clear()
			if classes:
				self.comboBox_class.addItems(classes)
			else:
				self.comboBox_class.addItem("Нет доступных классов")
				
		except Exception as e:
			print(f"Ошибка при загрузке классов: {e}")
			self.comboBox_class.addItem("Ошибка загрузки")
		
	def validate_name(self, name):
		"""
		Проверяет корректность имени/названия класса
		Возвращает (is_valid, error_message)
		"""
		if not name or not name.strip():
			return False, "Имя не может быть пустым"
		
		# Проверяем, что имя не начинается с пробела
		if name.startswith(' '):
			return False, "Имя не может начинаться с пробелом"
		
		# Проверяем, что имя не заканчивается на пробел
		if name.endswith(' '):
			return False, "Имя не может заканчиваться на пробел"
		
		# Проверяем, что имя не начинается с цифры
		if name[0].isdigit():
			return False, "Имя не может начинаться с цифры"
		
		# Проверяем на наличие только допустимых символов
		if not all(c.isalnum() or c.isspace() or c in '-_.' for c in name):
			return False, "Имя содержит недопустимые символы"
		
		# Проверяем длину имени
		if len(name) < 2:
			return False, "Имя должно содержать минимум 2 символа"
		
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
		
	def sozdanie_uchitelya(self):
		"""Создание нового учителя"""
		name = self.lineEdit_uchitel.text().strip()
		parol_text = self.lineEdit_parol_uchitel.text().strip()
		
		if not name or not parol_text:
			self.pokazat_status("Введите имя и пароль учителя", "red")
			return
		
		# ПРОВЕРКА КОРРЕКТНОСТИ ИМЕНИ УЧИТЕЛЯ
		is_valid, error_message = self.validate_name(name)
		if not is_valid:
			self.pokazat_status(f"Ошибка в имени: {error_message}", "red")
			return
			
		try:
			parol = int(parol_text)
		except ValueError:
			self.pokazat_status("Пароль должен быть целым числом", "red")
			return
			
		# Проверяем существование учителя
		if self.find_by_name('uchitelya', name):
			self.pokazat_status("Учитель с таким именем уже существует", "red")
			return
			
		# Создаем таблицу учителей если нет
		if not self.check_table_exists('uchitelya'):
			self.make_table_uchitelya()
			
		# Добавляем учителя
		self.add_uchitel(name, parol)
		self.pokazat_status(f"Учитель {name} успешно создан", "green")
		self.ochistit_polya_uchitel()
		
	def udalenie_uchitelya(self):
		"""Удаление учителя"""
		name = self.lineEdit_udalenie.text().strip()
		
		if not name:
			self.pokazat_status("Введите имя учителя для удаления", "red")
			return
			
		# Проверяем существование учителя
		if not self.find_by_name('uchitelya', name):
			self.pokazat_status("Учитель с таким именем не найден", "red")
			return
			
		# Удаляем учителя
		self.delete_by_name('uchitelya', name)
		self.pokazat_status(f"Учитель {name} успешно удален", "green")
		self.lineEdit_udalenie.clear()
		
	def sozdanie_uchenika(self):
		"""Создание нового ученика"""
		name = self.lineEdit_uchenik.text().strip()
		parol_text = self.lineEdit_parol_uchenik.text().strip()
		class_name = self.comboBox_class.currentText()
		
		if not name or not parol_text:
			self.pokazat_status("Введите имя и пароль ученика", "red")
			return
			
		if class_name in ["Нет доступных классов", "Ошибка загрузки"]:
			self.pokazat_status("Нет доступных классов для добавления", "red")
			return
		
		# ПРОВЕРКА КОРРЕКТНОСТИ ИМЕНИ УЧЕНИКА
		is_valid, error_message = self.validate_name(name)
		if not is_valid:
			self.pokazat_status(f"Ошибка в имени: {error_message}", "red")
			return
			
		try:
			parol = int(parol_text)
		except ValueError:
			self.pokazat_status("Пароль должен быть целым числом", "red")
			return
			
		# Проверяем существование ученика
		if self.find_by_name('ucheniki', name):
			self.pokazat_status("Ученик с таким именем уже существует", "red")
			return
			
		# Создаем таблицу учеников если нет
		if not self.check_table_exists('ucheniki'):
			self.make_table_uchenik()
			
		# Добавляем ученика в основную таблицу
		student_id = self.add_uchenik(name, parol, 1)
		
		# Добавляем ученика в выбранный класс
		if student_id:
			self.add_student_to_class(class_name, student_id, name)
			self.pokazat_status(f"Ученик {name} успешно создан и добавлен в класс {class_name}", "green")
			self.ochistit_polya_uchenik()
			# Обновляем список классов (на случай если создался новый класс)
			self.load_all_classes()
		else:
			self.pokazat_status("Ошибка при создании ученика", "red")
		
	def add_student_to_class(self, class_name, student_id, student_name):
		"""Добавляет ученика в таблицу класса"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			
			# Проверяем существование таблицы класса
			cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (class_name,))
			if not cursor.fetchone():
				# Создаем таблицу класса если её нет
				cursor.execute(f'''CREATE TABLE IF NOT EXISTS {class_name} (
					id_uchenika INTEGER PRIMARY KEY,
					name TEXT,
					ocenka1 INTEGER,
					ocenka2 INTEGER,
					ocenka3 INTEGER
				)''')
			
			# Добавляем ученика в класс
			cursor.execute(f"INSERT INTO {class_name} (id_uchenika, name) VALUES (?, ?)", 
						  (student_id, student_name))
			
			conn.commit()
			conn.close()
			return True
			
		except Exception as e:
			print(f"Ошибка при добавлении в класс: {e}")
			return False
		
	def udalenie_uchenika(self):
		"""Удаление ученика"""
		name = self.lineEdit_udalenie_uchenik.text().strip()
		
		if not name:
			self.pokazat_status("Введите имя ученика для удаления", "red")
			return
			
		# Проверяем существование ученика
		student_data = self.find_by_name('ucheniki', name)
		if not student_data:
			self.pokazat_status("Ученик с таким именем не найден", "red")
			return
			
		student_id = student_data[0]
		
		# Удаляем ученика из всех классов
		self.remove_student_from_all_classes(student_id)
		
		# Удаляем ученика из основной таблицы
		self.delete_by_name('ucheniki', name)
		self.pokazat_status(f"Ученик {name} успешно удален", "green")
		self.lineEdit_udalenie_uchenik.clear()
		
	def remove_student_from_all_classes(self, student_id):
		"""Удаляет ученика из всех классов"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			
			# Получаем все таблицы классов
			cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
			tables = cursor.fetchall()
			
			for table in tables:
				table_name = table[0]
				if (table_name not in ['uchitelya', 'ucheniki', 'sqlite_sequence'] and 
					not table_name.startswith('sqlite_')):
					# Удаляем ученика из класса
					cursor.execute(f"DELETE FROM {table_name} WHERE id_uchenika = ?", (student_id,))
			
			conn.commit()
			conn.close()
			
		except Exception as e:
			print(f"Ошибка при удалении из классов: {e}")
		
	def prosmotr_vseh(self):
		"""Просмотр всех пользователей"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			
			# Получаем всех учителей
			cursor.execute("SELECT id, name, parol FROM uchitelya")
			uchitelya = cursor.fetchall()
			
			# Получаем всех учеников
			cursor.execute("SELECT id, name, parol FROM ucheniki")
			ucheniki = cursor.fetchall()
			
			conn.close()
			
			# Формируем сообщение
			message = "=== УЧИТЕЛЯ ===\n"
			if uchitelya:
				for uchitel in uchitelya:
					message += f"ID: {uchitel[0]}, Имя: {uchitel[1]}, Пароль: {uchitel[2]}\n"
			else:
				message += "Учителей нет\n"
				
			message += "\n=== УЧЕНИКИ ===\n"
			if ucheniki:
				for uchenik in ucheniki:
					message += f"ID: {uchenik[0]}, Имя: {uchenik[1]}, Пароль: {uchenik[2]}\n"
			else:
				message += "Учеников нет\n"
				
			# Показываем в диалоговом окне
			dialog = QtWidgets.QMessageBox(self)
			dialog.setWindowTitle("Все пользователи")
			dialog.setText(message)
			dialog.exec_()
			
		except Exception as e:
			self.pokazat_status(f"Ошибка при получении данных: {e}", "red")
			
	def sozdanie_backup(self):
		"""Создание резервной копии базы данных в автоматическую папку"""
		try:
			current_dir = os.path.dirname(os.path.realpath(__file__))
			source_path = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')
			backup_path = os.path.join(os.path.join(current_dir, 'SourceBackup'), 'vse.db')
			
			# Создаем папку если нет
			os.makedirs(os.path.dirname(backup_path), exist_ok=True)
			
			# Копируем файл
			shutil.copy2(source_path, backup_path)
			self.pokazat_status(f"Резервная копия базы данных создана: {backup_path}", "green")
			
		except Exception as e:
			self.pokazat_status(f"Ошибка при создании резервной копии: {e}", "red")
			
	def sozdanie_backup_custom(self):
		"""Создание резервной копии базы данных в выбранное место"""
		try:
			# Открываем диалог выбора папки
			folder_path = QtWidgets.QFileDialog.getExistingDirectory(
				self, 
				"Выберите папку для сохранения резервной копии",
				os.path.expanduser("~"),
				QtWidgets.QFileDialog.ShowDirsOnly
			)
			
			if not folder_path:
				self.pokazat_status("Операция отменена", "orange")
				return
				
			current_dir = os.path.dirname(os.path.realpath(__file__))
			source_path = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')
			
			# Проверяем существование исходного файла
			if not os.path.exists(source_path):
				self.pokazat_status("Исходный файл базы данных не найден", "red")
				return
			
			# Создаем имя файла с timestamp
			from datetime import datetime
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			backup_filename = f"vse_backup_{timestamp}.db"
			backup_path = os.path.join(folder_path, backup_filename)
			
			# Копируем файл
			shutil.copy2(source_path, backup_path)
			
			# Проверяем успешность копирования
			if os.path.exists(backup_path):
				self.pokazat_status(f"База данных успешно скопирована в: {backup_path}", "green")
				
				# Показываем дополнительное сообщение об успехе
				msg = QtWidgets.QMessageBox()
				msg.setIcon(QtWidgets.QMessageBox.Information)
				msg.setWindowTitle("Копирование завершено")
				msg.setText(f"База данных успешно скопирована:\n{backup_path}")
				msg.exec_()
			else:
				self.pokazat_status("Ошибка: файл не был создан", "red")
				
		except Exception as e:
			self.pokazat_status(f"Ошибка при копировании базы данных: {e}", "red")
			
	def exit(self):
		"""Выход из приложения"""
		if self.parent_window:
			self.parent_window.show()
		self.close()
		
	def pokazat_status(self, message, color):
		"""Показать статусное сообщение"""
		self.label_status.setText(message)
		self.label_status.setStyleSheet(f"color: {color};")
		
	def ochistit_polya_uchitel(self):
		"""Очистить поля учителя"""
		self.lineEdit_uchitel.clear()
		self.lineEdit_parol_uchitel.clear()
		
	def ochistit_polya_uchenik(self):
		"""Очистить поля ученика"""
		self.lineEdit_uchenik.clear()
		self.lineEdit_parol_uchenik.clear()
		
	# Методы работы с базой данных (взяты из try_table.py)
	
	def check_table_exists(self, table_name):
		"""Проверяет существование таблицы"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
			result = cursor.fetchone()
			conn.close()
			return result is not None
		except:
			return False
			
	def make_table_uchitelya(self):
		"""Создает таблицу учителей"""
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS uchitelya (
			id INTEGER PRIMARY KEY,
			name TEXT,
			parol INTEGER,
			chislo_classov INTEGER,
			class0 TEXT)''')
		conn.commit()
		conn.close()
		
	def make_table_uchenik(self):
		"""Создает таблицу учеников"""
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS ucheniki (
			id INTEGER PRIMARY KEY,
			name TEXT,
			parol INTEGER,
			nikname TEXT,
			posl_oc INTEGER,
			rezh INTEGER,
			max_number INTEGER DEFAULT 10,
			grading_criteria TEXT DEFAULT 'standard')''')
		conn.commit()
		conn.close()
		
	def find_by_name(self, tabl_name, name):
		"""Находит пользователя по имени"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			cursor.execute(f"SELECT * FROM {tabl_name} WHERE name = ?", (name,))
			user = cursor.fetchone()
			conn.close()
			return user
		except:
			return None
			
	def add_uchitel(self, name1, parol1):
		"""Добавляет учителя"""
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO uchitelya (name, parol) VALUES (?, ?)", (name1, parol1))
		conn.commit()
		conn.close()
		
	def add_uchenik(self, name1, parol1, rezh1):
		"""Добавляет ученика и возвращает его ID"""
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO ucheniki (name, parol, rezh) VALUES (?, ?, ?)", (name1, parol1, rezh1))
			student_id = cursor.lastrowid
			conn.commit()
			conn.close()
			return student_id
		except Exception as e:
			print(f"Ошибка при добавлении ученика: {e}")
			return None
		
	def delete_by_name(self, table_name, name_value):
		"""Удаляет пользователя по имени"""
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute(f"DELETE FROM {table_name} WHERE name = ?", (name_value,))
		conn.commit()
		conn.close()
		
	def closeEvent(self, event):
		"""Обработчик закрытия окна"""
		if self.parent_window:
			self.parent_window.show()
		event.accept()