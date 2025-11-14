import sys
import os
from typing import Tuple, List

from vichesleniya import EquationGenerator

from PyQt5 import QtCore, QtGui, QtWidgets
from resh_prim import Ui_mainwindow_1
from rere_prim import proba_prohozhdeniya
from try_table import *

class pr_na_ocenku(QtWidgets.QMainWindow, Ui_mainwindow_1):
	def __init__(self, dannie, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.parent = parent
		self.dannie = dannie
		self.showFullScreen()
		self.pushButton_2.clicked.connect(self.exit)
		self.pushButton.clicked.connect(self.prov_resh)
		self.pushButton_4.hide()
		self.label_3.hide()
		# self.pushButton_4.clicked.connect(self.start)
		self.setWindowFlags(QtCore.Qt.Window)
		self.rrr()

	def rrr(self):
		# Получаем настройки из базы данных
		max_number = self.dannie[6] if self.dannie[6] is not None else 10
		grading_criteria = self.dannie[7] if self.dannie[7] else 'standard'
		extended_mode = self.dannie[5]  # берем из базы данных

		# Получаем информацию об оценках
		examples_count, grading_array = self.get_grading_info(extended_mode, grading_criteria, max_number)
		
		print(f"Всего примеров: {examples_count}")
		print(f"Максимальное число: {max_number}")
		print(f"Критерии оценивания: {grading_criteria}")
		print(f"Для оценки 5 нужно: {grading_array[0]} правильных")
		print(f"Для оценки 4 нужно: {grading_array[1]} правильных") 
		print(f"Для оценки 3 нужно: {grading_array[2]} правильных")
		print(f"Для оценки 2 нужно: {grading_array[3]} правильных")
		
		self.examples_count = examples_count
		self.max_number = max_number
		self.correct_answers = 0
		self.sdel_primer = 0  # Начинаем с 0
		
		# Меняем подключение кнопки
		self.pushButton.clicked.disconnect()
		self.pushButton.clicked.connect(self.again)
		
		# Запускаем первый пример
		self.again()  # Теперь again() сам разберется

	def show_message(self, text, color):
		"""Универсальная функция для показа сообщений"""
		self.label_3.show()
		self.label_3.setText(text)
		self.label_3.setStyleSheet(f"""
			QLabel {{
				background-color: transparent;
				color: {color};
				font-size: 25px;
				font-weight: bold;
				border: none;
				text-align: center;
			}}
		""")

	def prov_resh(self):
		otvet = self.lineEdit.text()
		
		# Более надежная проверка на число
		try:
			otvet = int(otvet)
		except ValueError:
			self.show_message('!НЕ ЧИСЛО! Введите число', '#3498db')
			self.lineEdit.clear()
			self.lineEdit.setFocus()  # Фокус остается в поле ввода
			return None  # Специальное значение для "не число"
		
		if otvet == self.answer:
			self.show_message('!ВЕРНО!', '#2ecc71')
			self.correct_answers += 1
			return True
		else:
			self.show_message(f'!НЕВЕРНО! Правильный ответ: {self.answer}', '#e74c3c')
			return False

	def again(self):
		"""Кнопка 'Далее' - всегда переходит к следующему примеру"""
		# Если это первый пример, просто запускаем
		if self.sdel_primer == 0:
			self.start()
			self.sdel_primer = 1
			return
		
		# Проверяем текущий ответ
		result = self.prov_resh()
		
		# Если введено не число - не переходим дальше
		if result is None:
			return
		
		# Переходим к следующему примеру или завершаем
		if self.sdel_primer < self.examples_count:
			self.start()
			self.sdel_primer += 1
		else:
			self.finish_test()

	def finish_test(self):
		"""Завершение теста и выставление оценки"""
		self.pushButton.clicked.disconnect()
		extended_mode = self.dannie[5]
		grading_criteria = self.dannie[7] if self.dannie[7] else 'standard'
		max_number = self.dannie[6] if self.dannie[6] is not None else 10
		
		examples_count, grading_array = self.get_grading_info(extended_mode, grading_criteria, max_number)
		final_grade = self.calculate_grade(self.correct_answers, grading_array)
		self.label_3.setText(f"Оценка: {final_grade}")
		print(f"Оценка: {final_grade}")
		nomer = add_ocenka_auto_secure(find_student_in_classes(self.dannie[1]), self.dannie[0], final_grade)
		if nomer is not None:
			print(f"Оценка добавлена под номером {nomer}")
		else:
			print("Не удалось добавить оценку")

	def start(self):
		generator = EquationGenerator()
		self.lineEdit.clear()
		self.lineEdit.setFocus()
		# rezh_value = student_data[5]
		self.rezh = self.dannie[5]
		equation, steps, answer = generator.generate_from_extended_mode(self.rezh)
		self.answer = answer
		print(self.answer)
		self.label.setText(str(equation))

	def get_grading_info(self, extended_mode: int, grading_criteria: str, max_number: int) -> Tuple[int, List[int]]:
		"""
		Извлекает количество примеров и массив с числом правильных для каждой оценки
		из расширенного режима (64 бита) и отдельных настроек
		
		Args:
			extended_mode: 64-битное число с настройками
			grading_criteria: строка с критериями оценивания
			max_number: максимальное число для примеров
			
		Returns:
			Tuple[int, List[int]]: (количество примеров, [правильных для 5, для 4, для 3, для 2])
		"""
		# Извлекаем параметры из 64-битного числа
		examples_count = (extended_mode >> 32) & 0xFFFF
		
		# Если examples_count = 0, используем значение по умолчанию
		if examples_count == 0:
			examples_count = 10
		
		def calculate_standard_grading(total_examples):
			"""Стандартная система оценки по процентам"""
			return [
				max(1, int(total_examples * 0.8)),  # 5: 80%
				max(1, int(total_examples * 0.6)),  # 4: 60%
				max(1, int(total_examples * 0.4)),  # 3: 40%
				1								   # 2: минимум 1
			]
		
		def calculate_custom_grading(total_examples, grading_criteria):
			"""Кастомная система с индивидуальными критериями для каждой оценки"""
			# Парсим критерии из строки
			criteria_dict = self.parse_grading_criteria(grading_criteria)
			
			for_5 = criteria_dict.get('for_5', max(1, int(total_examples * 0.8)))
			for_4 = criteria_dict.get('for_4', max(1, int(total_examples * 0.6)))
			for_3 = criteria_dict.get('for_3', max(1, int(total_examples * 0.4)))
			for_2 = criteria_dict.get('for_2', 1)
			
			return [for_5, for_4, for_3, for_2]
		
		# Определяем принцип оценки
		if grading_criteria == 'standard' or not grading_criteria:
			# Стандартная система
			grading_array = calculate_standard_grading(examples_count)
		else:
			# Кастомная система
			grading_array = calculate_custom_grading(examples_count, grading_criteria)
		
		# Финальная проверка и корректировка
		grading_array = [
			min(grading_array[0], examples_count),  # для 5
			min(grading_array[1], grading_array[0] - 1) if grading_array[0] > 1 else 1,  # для 4
			min(grading_array[2], grading_array[1] - 1) if grading_array[1] > 1 else 1,  # для 3
			min(grading_array[3], grading_array[2] - 1) if grading_array[2] > 1 else 1   # для 2
		]
		
		# Гарантируем, что значения идут по убыванию
		for i in range(3):
			if grading_array[i] <= grading_array[i + 1]:
				grading_array[i + 1] = max(1, grading_array[i] - 1)
		
		return examples_count, grading_array
	
	def parse_grading_criteria(self, criteria_string):
		"""Парсит строку критериев оценивания"""
		criteria_dict = {}
		try:
			# Формат: "5:8,4:6,3:4,2:1" или подобный
			if criteria_string == 'standard':
				return criteria_dict  # Пустой словарь - будут использованы стандартные значения
				
			pairs = criteria_string.split(',')
			for pair in pairs:
				if ':' in pair:
					grade, value = pair.split(':')
					if grade.strip() in ['5', 'for_5']:
						criteria_dict['for_5'] = int(value.strip())
					elif grade.strip() in ['4', 'for_4']:
						criteria_dict['for_4'] = int(value.strip())
					elif grade.strip() in ['3', 'for_3']:
						criteria_dict['for_3'] = int(value.strip())
					elif grade.strip() in ['2', 'for_2']:
						criteria_dict['for_2'] = int(value.strip())
		except:
			pass
		return criteria_dict
	
	def calculate_grade(self, correct_answers: int, grading_array: List[int]) -> int:
		"""
		Определяет оценку based на количестве правильных ответов
		
		Args:
			correct_answers: количество правильных ответов
			grading_array: [правильных для 5, для 4, для 3, для 2]
			
		Returns:
			int: оценка (5, 4, 3, 2)
		"""
		if correct_answers >= grading_array[0]:
			return 5
		elif correct_answers >= grading_array[1]:
			return 4
		elif correct_answers >= grading_array[2]:
			return 3
		elif correct_answers >= grading_array[3]:
			return 2
		else:
			return 2  # Минимальная оценка

	def exit(self):
		if self.parent:
			self.parent.show()
		self.close()

	def closeEvent(self, event):
		if self.parent:
			self.parent.show()
		event.accept()