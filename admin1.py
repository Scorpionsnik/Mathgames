import sys
import os
import sqlite3
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets

from admin_panel import admin_panel

class AdminWindow(QtWidgets.QMainWindow, admin_panel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent_window = parent
		
		self.pushButton_sozd_uchitel.clicked.connect(self.sozdanie_uchitelya)
		self.pushButton_udalit_uchitel.clicked.connect(self.udalenie_uchitelya)
		self.pushButton_sozd_uchenik.clicked.connect(self.sozdanie_uchenika)
		self.pushButton_udalit_uchenik.clicked.connect(self.udalenie_uchenika)
		self.pushButton_prosmotr.clicked.connect(self.prosmotr_vseh)
		self.pushButton_backup.clicked.connect(self.sozdanie_backup)
		self.pushButton_backup_custom.clicked.connect(self.sozdanie_backup_custom)
		self.pushButton_exit.clicked.connect(self.exit)
		
		self.load_all_classes()
		
		self.setWindowFlags(QtCore.Qt.Window)
		
	def load_all_classes(self):
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()
			cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
			tables = cursor.fetchall()
			classes = []
			for table in tables:
				table_name = table[0]
				if (table_name not in ['uchitelya', 'ucheniki', 'sqlite_sequence', 'admin'] and 
					not table_name.startswith('sqlite_')):
					classes.append(table_name)
			
			conn.close()
			self.comboBox_class.clear()
			if classes:
				self.comboBox_class.addItems(classes)
			else:
				self.comboBox_class.addItem("Нет доступных классов")
				
		except Exception as e:
			print(f"Ошибка при загрузке классов: {e}")
			self.comboBox_class.addItem("Ошибка загрузки")
		
	def validate_name(self, name):
		if not name or not name.strip():
			return False, "Имя не может быть пустым"
		
		if name.startswith(' '):
			return False, "Имя не может начинаться с пробелом"

		if name.endswith(' '):
			return False, "Имя не может заканчиваться на пробел"

		if name[0].isdigit():
			return False, "Имя не может начинаться с цифры"

		if not all(c.isalnum() or c.isspace() or c in '-_.' for c in name):
			return False, "Имя содержит недопустимые символы"
		
		if len(name) > 50:
			return False, "Имя не может превышать 50 символов"
		
		return True, ""

	def validate_class_name(self, class_name):

		is_valid, error_message = self.validate_name(class_name)
		
		if not is_valid:
			return False, error_message
		
		if len(class_name) > 50:
			return False, "Название класса не может превышать 50 символов"
		
		return True, ""
		
	def sozdanie_uchitelya(self):
		name = self.lineEdit_uchitel.text().strip()
		parol_text = self.lineEdit_parol_uchitel.text().strip()
		
		if not name or not parol_text:
			self.pokazat_status("Введите имя и пароль учителя", "red")
			return
		is_valid, error_message = self.validate_name(name)
		if not is_valid:
			self.pokazat_status(f"Ошибка в имени: {error_message}", "red")
			return
			
		try:
			parol = int(parol_text)
		except ValueError:
			self.pokazat_status("Пароль должен быть целым числом", "red")
			return

		if self.find_by_name('uchitelya', name):
			self.pokazat_status("Учитель с таким именем уже существует", "red")
			return

		if not self.check_table_exists('uchitelya'):
			self.make_table_uchitelya()
			
		self.add_uchitel(name, parol)
		self.pokazat_status(f"Учитель {name} успешно создан", "green")
		self.ochistit_polya_uchitel()
		
	def udalenie_uchitelya(self):
		name = self.lineEdit_udalenie.text().strip()
		
		if not name:
			self.pokazat_status("Введите имя учителя для удаления", "red")
			return

		if not self.find_by_name('uchitelya', name):
			self.pokazat_status("Учитель с таким именем не найден", "red")
			return

		self.delete_by_name('uchitelya', name)
		self.pokazat_status(f"Учитель {name} успешно удален", "green")
		self.lineEdit_udalenie.clear()
		
	def sozdanie_uchenika(self):
		name = self.lineEdit_uchenik.text().strip()
		parol_text = self.lineEdit_parol_uchenik.text().strip()
		class_name = self.comboBox_class.currentText()
		
		if not name or not parol_text:
			self.pokazat_status("Введите имя и пароль ученика", "red")
			return
			
		if class_name in ["Нет доступных классов", "Ошибка загрузки"]:
			self.pokazat_status("Нет доступных классов для добавления", "red")
			return

		is_valid, error_message = self.validate_name(name)
		if not is_valid:
			self.pokazat_status(f"Ошибка в имени: {error_message}", "red")
			return
			
		try:
			parol = int(parol_text)
		except ValueError:
			self.pokazat_status("Пароль должен быть целым числом", "red")
			return

		if self.find_by_name('ucheniki', name):
			self.pokazat_status("Ученик с таким именем уже существует", "red")
			return

		if not self.check_table_exists('ucheniki'):
			self.make_table_uchenik()
		student_id = self.add_uchenik(name, parol, 1)
		
		if student_id:
			self.add_student_to_class(class_name, student_id, name)
			self.pokazat_status(f"Ученик {name} успешно создан и добавлен в класс {class_name}", "green")
			self.ochistit_polya_uchenik()
			self.load_all_classes()
		else:
			self.pokazat_status("Ошибка при создании ученика", "red")
		
	def add_student_to_class(self, class_name, student_id, student_name):
		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()

			cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (class_name,))
			if not cursor.fetchone():
				cursor.execute(f'''CREATE TABLE IF NOT EXISTS {class_name} (
					id_uchenika INTEGER PRIMARY KEY,
					name TEXT,
					ocenka1 INTEGER,
					ocenka2 INTEGER,
					ocenka3 INTEGER
				)''')

			cursor.execute(f"INSERT INTO {class_name} (id_uchenika, name) VALUES (?, ?)", 
						  (student_id, student_name))
			
			conn.commit()
			conn.close()
			return True
			
		except Exception as e:
			print(f"Ошибка при добавлении в класс: {e}")
			return False
		
	def udalenie_uchenika(self):
		name = self.lineEdit_udalenie_uchenik.text().strip()
		
		if not name:
			self.pokazat_status("Введите имя ученика для удаления", "red")
			return

		student_data = self.find_by_name('ucheniki', name)
		if not student_data:
			self.pokazat_status("Ученик с таким именем не найден", "red")
			return
			
		student_id = student_data[0]

		self.remove_student_from_all_classes(student_id)

		self.delete_by_name('ucheniki', name)
		self.pokazat_status(f"Ученик {name} успешно удален", "green")
		self.lineEdit_udalenie_uchenik.clear()
		
	def remove_student_from_all_classes(self, student_id):

		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()

			cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
			tables = cursor.fetchall()
			
			for table in tables:
				table_name = table[0]
				if (table_name not in ['uchitelya', 'ucheniki', 'sqlite_sequence'] and 
					not table_name.startswith('sqlite_')):

					cursor.execute(f"DELETE FROM {table_name} WHERE id_uchenika = ?", (student_id,))
			
			conn.commit()
			conn.close()
			
		except Exception as e:
			print(f"Ошибка при удалении из классов: {e}")
		
	def prosmotr_vseh(self):

		try:
			conn = sqlite3.connect('Data/vse.db')
			cursor = conn.cursor()

			cursor.execute("SELECT id, name, parol FROM uchitelya")
			uchitelya = cursor.fetchall()

			cursor.execute("SELECT id, name, parol FROM ucheniki")
			ucheniki = cursor.fetchall()
			
			conn.close()

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

			dialog = QtWidgets.QMessageBox(self)
			dialog.setWindowTitle("Все пользователи")
			dialog.setText(message)
			dialog.exec_()
			
		except Exception as e:
			self.pokazat_status(f"Ошибка при получении данных: {e}", "red")
			
	def sozdanie_backup(self):
		try:
			current_dir =".\\"
			source_path = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')
			backup_path = os.path.join(os.path.join(current_dir, 'SourceBackup'), 'vse.db')

			os.makedirs(os.path.dirname(backup_path), exist_ok=True)

			shutil.copy2(source_path, backup_path)
			self.pokazat_status(f"Резервная копия базы данных создана: {backup_path}", "green")
			
		except Exception as e:
			self.pokazat_status(f"Ошибка при создании резервной копии: {e}", "red")
			
	def sozdanie_backup_custom(self):
		try:
			folder_path = QtWidgets.QFileDialog.getExistingDirectory(
				self, 
				"Выберите папку для сохранения резервной копии",
				os.path.expanduser("~"),
				QtWidgets.QFileDialog.ShowDirsOnly
			)
			
			if not folder_path:
				self.pokazat_status("Операция отменена", "orange")
				return
				
			current_dir = ".\\"
			source_path = os.path.join(os.path.join(current_dir, 'Data'), 'vse.db')

			if not os.path.exists(source_path):
				self.pokazat_status("Исходный файл базы данных не найден", "red")
				return

			from datetime import datetime
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			backup_filename = f"vse_backup_{timestamp}.db"
			backup_path = os.path.join(folder_path, backup_filename)

			shutil.copy2(source_path, backup_path)

			if os.path.exists(backup_path):
				self.pokazat_status(f"База данных успешно скопирована в: {backup_path}", "green")

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
		if self.parent_window:
			self.parent_window.show()
		self.close()
		
	def pokazat_status(self, message, color):
		self.label_status.setText(message)
		self.label_status.setStyleSheet(f"color: {color};")
		
	def ochistit_polya_uchitel(self):
		self.lineEdit_uchitel.clear()
		self.lineEdit_parol_uchitel.clear()
		
	def ochistit_polya_uchenik(self):
		self.lineEdit_uchenik.clear()
		self.lineEdit_parol_uchenik.clear()
	
	def check_table_exists(self, table_name):
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
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO uchitelya (name, parol) VALUES (?, ?)", (name1, parol1))
		conn.commit()
		conn.close()
		
	def add_uchenik(self, name1, parol1, rezh1):

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
		conn = sqlite3.connect('Data/vse.db')
		cursor = conn.cursor()
		cursor.execute(f"DELETE FROM {table_name} WHERE name = ?", (name_value,))
		conn.commit()
		conn.close()
		
	def closeEvent(self, event):
		if self.parent_window:
			self.parent_window.show()
		event.accept()