import sys
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from uch4 import Uch4

class TeacherViewWindow(QtWidgets.QMainWindow, Uch4):
    def __init__(self, parent=None, teacher_data=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent_window = parent
        self.teacher_data = teacher_data
        self.current_class = None
        self.current_student_id = None
        self.setWindowFlags(QtCore.Qt.Window)
        self.setup_connections()
        self.load_teacher_classes()
        
    def setup_connections(self):
        self.pushButton_load.clicked.connect(self.load_class_data)
        self.pushButton_set_grade.clicked.connect(self.set_grade)
        self.pushButton_delete_grade.clicked.connect(self.delete_grade)
        self.pushButton_set_task_student.clicked.connect(self.set_task_student)
        self.pushButton_set_task_class.clicked.connect(self.set_task_class)
        self.pushButton_back.clicked.connect(self.go_back)
        self.listWidget_students.currentRowChanged.connect(self.on_student_selected)
        
        # Валидация диапазона чисел
        self.spinBox_min.valueChanged.connect(self.validate_number_range)
        self.spinBox_max.valueChanged.connect(self.validate_number_range)
        
        # Связываем чекбокс переменных со спинбоксом
        self.checkBox_variables.stateChanged.connect(self.on_variables_changed)
        
        # Редактирование таблицы
        self.tableWidget_grades.cellChanged.connect(self.on_grade_cell_changed)
        self.tableWidget_grades.cellDoubleClicked.connect(self.on_grade_cell_double_clicked)
        
        # Принцип оценки
        self.radioButton_standard.toggled.connect(self.on_grading_system_changed)
        self.radioButton_custom.toggled.connect(self.on_grading_system_changed)
        
        # Валидация: числа правильных не могут превышать число примеров
        self.spinBox_examples_count.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_5.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_4.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_3.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_2.valueChanged.connect(self.validate_grading_criteria)
        
    def validate_grading_criteria(self):
        """Проверяет что числа правильных не превышают число примеров и идут по убыванию"""
        examples_count = self.spinBox_examples_count.value()
        
        # Ограничиваем максимальные значения
        self.spinBox_for_5.setMaximum(examples_count)
        self.spinBox_for_4.setMaximum(examples_count)
        self.spinBox_for_3.setMaximum(examples_count)
        self.spinBox_for_2.setMaximum(examples_count)
        
        # Гарантируем убывающую последовательность
        for_5 = self.spinBox_for_5.value()
        for_4 = self.spinBox_for_4.value()
        for_3 = self.spinBox_for_3.value()
        for_2 = self.spinBox_for_2.value()
        
        if for_4 >= for_5:
            self.spinBox_for_4.setValue(max(1, for_5 - 1))
        if for_3 >= for_4:
            self.spinBox_for_3.setValue(max(1, for_4 - 1))
        if for_2 >= for_3:
            self.spinBox_for_2.setValue(max(1, for_3 - 1))
            
    def on_grading_system_changed(self):
        """Включает/выключает спинбоксы для кастомной оценки"""
        enabled = self.radioButton_custom.isChecked()
        self.spinBox_for_5.setEnabled(enabled)
        self.spinBox_for_4.setEnabled(enabled)
        self.spinBox_for_3.setEnabled(enabled)
        self.spinBox_for_2.setEnabled(enabled)
        
    def on_variables_changed(self, state):
        """Включает/выключает спинбокс переменных"""
        self.spinBox_variables.setEnabled(state == QtCore.Qt.Checked)
        
    def validate_number_range(self):
        """Проверяет что минимальное число не больше максимального"""
        min_val = self.spinBox_min.value()
        max_val = self.spinBox_max.value()
        
        if min_val > max_val:
            self.spinBox_max.setValue(min_val)
            
    def encode_max_number(self, max_number):
        """
        Шифрует максимальное число в формат: первая цифра + количество нулей
        Например: 100 -> 12 (1 и 2 нуля), 1000 -> 13 (1 и 3 нуля)
        """
        if max_number <= 0:
            return 10  # По умолчанию 10
            
        # Преобразуем число в строку для анализа
        num_str = str(max_number)
        
        # Проверяем, является ли число степенью 10 (1, 10, 100, 1000 и т.д.)
        if num_str[0] == '1' and all(digit == '0' for digit in num_str[1:]):
            first_digit = 1
            zeros_count = len(num_str) - 1
        else:
            # Для чисел не являющихся степенью 10, используем первую цифру и округляем
            first_digit = int(num_str[0])
            zeros_count = len(num_str) - 1
            
        # Кодируем: первая цифра * 10 + количество нулей
        encoded = first_digit * 10 + zeros_count
        return encoded
        
    def decode_max_number(self, encoded):
        """
        Декодирует максимальное число из зашифрованного формата
        Например: 12 -> 100 (1 и 2 нуля), 13 -> 1000 (1 и 3 нуля)
        """
        if encoded < 10:
            return 10  # По умолчанию 10
            
        first_digit = encoded // 10
        zeros_count = encoded % 10
        
        # Восстанавливаем число: первая цифра * 10^zeros_count
        decoded = first_digit * (10 ** zeros_count)
        
        # Ограничиваем максимальное значение для QSpinBox
        max_spinbox_value = 2147483647
        if decoded > max_spinbox_value:
            return max_spinbox_value
        
        return decoded
            
    def calculate_extended_mode(self):
        """Вычисляет расширенный режим (64 бита) с принципом оценки"""
        mode_number = 0
        
        # Битовая маска операций (первые 8 бит)
        if self.checkBox_addition.isChecked():
            mode_number |= 0b00000001
        if self.checkBox_subtraction.isChecked():
            mode_number |= 0b00000010
        if self.checkBox_multiplication.isChecked():
            mode_number |= 0b00000100
        if self.checkBox_division.isChecked():
            mode_number |= 0b00001000
        if self.checkBox_negatives.isChecked():
            mode_number |= 0b00010000
        if self.checkBox_fractions.isChecked():
            mode_number |= 0b00100000
        if self.checkBox_decimals.isChecked():
            mode_number |= 0b01000000
        if self.checkBox_variables.isChecked():
            mode_number |= 0b10000000
            
        # Добавляем диапазон чисел и число действий (следующие 24 бита)
        min_val = self.spinBox_min.value()
        max_val = self.spinBox_max.value()
        actions_count = self.spinBox_actions.value()
        
        # Шифруем максимальное число
        encoded_max = self.encode_max_number(max_val)
        
        # Старый формат (32 бита): [8 бит действий][8 бит min][8 бит зашифрованного max][8 бит режима]
        old_extended_mode = (actions_count << 24) | (min_val << 16) | (encoded_max << 8) | mode_number
        
        # Новый формат (64 бита): [16 бит: количество примеров][16 бит: зарезервировано][32 бита: старый режим]
        examples_count = self.spinBox_examples_count.value()
        
        # Принцип оценки теперь хранится отдельно в grading_criteria
        extended_mode_64 = (examples_count << 32) | old_extended_mode
        
        return extended_mode_64
        
    def load_student_settings(self, student_data):
        """Загружает настройки ученика из данных ученика"""
        if not student_data or len(student_data) < 8:
            # Устанавливаем значения по умолчанию
            self.set_default_settings()
            return
            
        # Получаем max_number и grading_criteria из базы данных
        max_number = student_data[6] if student_data[6] is not None else 10
        grading_criteria = student_data[7] if student_data[7] else 'standard'
        
        # Декодируем максимальное число если оно зашифровано
        if max_number > 100:  # Предполагаем, что числа больше 100 зашифрованы
            max_number = self.decode_max_number(max_number)
        
        # Проверяем, что число не превышает максимальное значение для QSpinBox
        max_spinbox_value = 2147483647
        if max_number > max_spinbox_value:
            max_number = max_spinbox_value
        
        # Устанавливаем максимальное число
        self.spinBox_max.setValue(max_number)
        
        # Устанавливаем принцип оценки
        if grading_criteria == 'standard':
            self.radioButton_standard.setChecked(True)
            # Устанавливаем стандартные значения
            examples_count = self.spinBox_examples_count.value()
            self.spinBox_for_5.setValue(min(8, examples_count))
            self.spinBox_for_4.setValue(min(6, examples_count))
            self.spinBox_for_3.setValue(min(4, examples_count))
            self.spinBox_for_2.setValue(1)
        else:
            self.radioButton_custom.setChecked(True)
            # Парсим кастомные критерии
            try:
                criteria_dict = self.parse_grading_criteria(grading_criteria)
                self.spinBox_for_5.setValue(criteria_dict.get('for_5', 8))
                self.spinBox_for_4.setValue(criteria_dict.get('for_4', 6))
                self.spinBox_for_3.setValue(criteria_dict.get('for_3', 4))
                self.spinBox_for_2.setValue(criteria_dict.get('for_2', 1))
            except:
                # В случае ошибки используем стандартные значения
                self.radioButton_standard.setChecked(True)
        
        # Если есть rezh значение, загружаем остальные настройки из него
        rezh_value = student_data[5]
        if rezh_value is not None:
            self.load_settings_from_rezh(rezh_value)
        
        self.on_grading_system_changed()  # Обновляем состояние спинбоксов оценки
    
    def load_settings_from_rezh(self, rezh_value):
        """Загружает настройки из значения rezh (64 бита)"""
        if rezh_value is None:
            return
            
        # Извлекаем настройки из 64-битного числа
        examples_count = (rezh_value >> 32) & 0xFFFF
        old_extended_mode = rezh_value & 0xFFFFFFFF
        
        # Извлекаем из старого формата
        actions_count = (old_extended_mode >> 24) & 0xFF
        min_val = (old_extended_mode >> 16) & 0xFF
        encoded_max = (old_extended_mode >> 8) & 0xFF  # Зашифрованное максимальное число
        mode_number = old_extended_mode & 0xFF  # первые 8 бит - режим
        
        # Декодируем максимальное число
        max_val = self.decode_max_number(encoded_max)
        
        # Проверяем, что число не превышает максимальное значение для QSpinBox
        max_spinbox_value = 2147483647
        if max_val > max_spinbox_value:
            max_val = max_spinbox_value
        
        # Устанавливаем диапазон, число действий и количество примеров
        self.spinBox_actions.setValue(actions_count if actions_count > 0 else 1)
        self.spinBox_min.setValue(min_val if min_val > 0 else 0)  # ИЗМЕНЕНО: минимальное 0
        self.spinBox_max.setValue(max_val)
        self.spinBox_examples_count.setValue(examples_count if examples_count > 0 else 10)
        
        # Устанавливаем операции
        self.checkBox_addition.setChecked(bool(mode_number & 0b00000001))
        self.checkBox_subtraction.setChecked(bool(mode_number & 0b00000010))
        self.checkBox_multiplication.setChecked(bool(mode_number & 0b00000100))
        self.checkBox_division.setChecked(bool(mode_number & 0b00001000))
        self.checkBox_negatives.setChecked(bool(mode_number & 0b00010000))
        self.checkBox_fractions.setChecked(bool(mode_number & 0b00100000))
        self.checkBox_decimals.setChecked(bool(mode_number & 0b01000000))
        self.checkBox_variables.setChecked(bool(mode_number & 0b10000000))
        
        # Включаем/выключаем спинбокс переменных
        self.spinBox_variables.setEnabled(self.checkBox_variables.isChecked())
    
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
    
    def format_grading_criteria(self):
        """Форматирует критерии оценивания в строку для базы данных"""
        if self.radioButton_standard.isChecked():
            return 'standard'
        else:
            return f"5:{self.spinBox_for_5.value()},4:{self.spinBox_for_4.value()},3:{self.spinBox_for_3.value()},2:{self.spinBox_for_2.value()}"
    
    def set_default_settings(self):
        """Устанавливает настройки по умолчанию"""
        self.spinBox_actions.setValue(1)
        self.spinBox_min.setValue(0)  # ИЗМЕНЕНО: минимальное число 0
        self.spinBox_max.setValue(10)
        self.spinBox_variables.setValue(0)
        self.spinBox_examples_count.setValue(10)  # Значение по умолчанию для примеров
        self.radioButton_standard.setChecked(True)
        self.spinBox_for_5.setValue(8)
        self.spinBox_for_4.setValue(6)
        self.spinBox_for_3.setValue(4)
        self.spinBox_for_2.setValue(1)
        self.on_grading_system_changed()  # Обновляем состояние спинбоксов оценки
        self.checkBox_addition.setChecked(True)
        self.checkBox_subtraction.setChecked(True)
        self.checkBox_multiplication.setChecked(False)
        self.checkBox_division.setChecked(False)
        self.checkBox_negatives.setChecked(False)
        self.checkBox_fractions.setChecked(False)
        self.checkBox_decimals.setChecked(False)
        self.checkBox_variables.setChecked(False)
        self.spinBox_variables.setEnabled(False)
    
    def get_number_range(self):
        """Возвращает выбранный диапазон чисел"""
        return (self.spinBox_min.value(), self.spinBox_max.value())
    
    def get_examples_count(self):
        """Возвращает количество примеров"""
        return self.spinBox_examples_count.value()
    
    def get_grading_system(self):
        """Возвращает принцип оценки"""
        if self.radioButton_standard.isChecked():
            return "standard"
        else:
            return f"custom:5-{self.spinBox_for_5.value()},4-{self.spinBox_for_4.value()},3-{self.spinBox_for_3.value()},2-{self.spinBox_for_2.value()}"
    
    def load_teacher_classes(self):
        """Загружает классы учителя из базы данных"""
        if not self.teacher_data:
            return
            
        teacher_name = self.teacher_data[1]
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM uchitelya WHERE name = ?", (teacher_name,))
        teacher_info = cursor.fetchone()
        
        self.comboBox_classes.clear()
        
        if teacher_info:
            class_columns = []
            for i in range(teacher_info[3] if teacher_info[3] else 0):
                col_name = f"class{i}"
                class_columns.append(col_name)
            
            for col in class_columns:
                if len(teacher_info) > 4 + class_columns.index(col) and teacher_info[4 + class_columns.index(col)]:
                    class_name = teacher_info[4 + class_columns.index(col)]
                    if class_name:
                        self.comboBox_classes.addItem(class_name)
        
        conn.close()
        
    def load_class_data(self):
        """Загружает данные выбранного класса"""
        if self.comboBox_classes.currentText():
            self.current_class = self.comboBox_classes.currentText()
            self.load_students_list()
            self.load_grades_table()
            
    def load_students_list(self):
        """Загружает список учеников класса"""
        if not self.current_class:
            return
            
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT id_uchenika, name FROM {self.current_class}")
        students = cursor.fetchall()
        
        self.listWidget_students.clear()
        self.students_data = {}
        
        for student_id, student_name in students:
            cursor.execute("SELECT * FROM ucheniki WHERE id = ?", (student_id,))
            student_info = cursor.fetchone()
            
            if student_info:
                display_text = f"{student_name} (ID: {student_id})"
                self.listWidget_students.addItem(display_text)
                self.students_data[student_id] = student_info
        
        conn.close()
        
    def load_grades_table(self):
        """Загружает таблицу оценок класса"""
        if not self.current_class:
            return
            
        # Отключаем сигнал чтобы избежать рекурсии при загрузке
        self.tableWidget_grades.cellChanged.disconnect()
            
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
        
        # Получаем структуру таблицы
        cursor.execute(f"PRAGMA table_info({self.current_class})")
        columns = cursor.fetchall()
        
        # Фильтруем колонки оценок и находим максимальный номер
        grade_columns = []
        max_grade_num = 0
        for col in columns:
            if col[1].startswith('ocenka'):
                grade_columns.append(col[1])
                # Извлекаем номер из имени колонки
                try:
                    grade_num = int(col[1].replace('ocenka', ''))
                    if grade_num > max_grade_num:
                        max_grade_num = grade_num
                except ValueError:
                    continue
        
        # Сортируем колонки по номеру
        grade_columns.sort(key=lambda x: int(x.replace('ocenka', '')) if x.replace('ocenka', '').isdigit() else 0)
        
        # Получаем данные студентов
        select_columns = ["id_uchenika", "name"] + grade_columns
        cursor.execute(f"SELECT {', '.join(select_columns)} FROM {self.current_class}")
        students_data = cursor.fetchall()
        
        # Настраиваем таблицу
        self.tableWidget_grades.setRowCount(len(students_data))
        self.tableWidget_grades.setColumnCount(len(grade_columns) + 2)  # +2 для ID и имени
        
        headers = ["ID", "Имя ученика"]
        for i in range(len(grade_columns)):
            headers.append(f"Оценка {i+1}")
        
        self.tableWidget_grades.setHorizontalHeaderLabels(headers)
        
        # Заполняем таблицу данными
        for row, student in enumerate(students_data):
            # ID и имя
            id_item = QtWidgets.QTableWidgetItem(str(student[0]))
            id_item.setFlags(id_item.flags() & ~QtCore.Qt.ItemIsEditable)  # Не редактируемый
            self.tableWidget_grades.setItem(row, 0, id_item)
            
            name_item = QtWidgets.QTableWidgetItem(student[1])
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)  # Не редактируемый
            self.tableWidget_grades.setItem(row, 1, name_item)
            
            # Оценки
            for col in range(2, len(grade_columns) + 2):
                grade_value = student[col] if student[col] is not None else ""
                grade_item = QtWidgets.QTableWidgetItem(str(grade_value))
                self.tableWidget_grades.setItem(row, col, grade_item)
        
        self.tableWidget_grades.resizeColumnsToContents()
        conn.close()
        
        # Включаем сигнал обратно
        self.tableWidget_grades.cellChanged.connect(self.on_grade_cell_changed)
        
    def on_student_selected(self, row):
        """Обработчик выбора ученика из списка"""
        if row >= 0 and hasattr(self, 'students_data'):
            student_item = self.listWidget_students.item(row)
            if student_item:
                text = student_item.text()
                student_id = int(text.split('(ID: ')[1].split(')')[0])
                self.current_student_id = student_id
                
                student_data = self.students_data.get(student_id)
                if student_data and len(student_data) >= 8:  # Проверяем что есть все поля
                    self.load_student_settings(student_data)
                    
    def ensure_grade_column_exists(self, class_name, grade_num):
        """Создает колонку для оценки если её нет"""
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
        
        # Получаем существующие колонки
        cursor.execute(f"PRAGMA table_info({class_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        column_name = f"ocenka{grade_num}"
        
        if column_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE {class_name} ADD COLUMN {column_name} INTEGER")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise e
        
        conn.close()
        
    def set_grade(self):
        """Устанавливает оценку выбранному ученику"""
        if not self.current_student_id or not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика и класс")
            return
            
        grade_num = self.spinBox_grade_num.value()
        grade_value = self.spinBox_grade_value.value()
        
        try:
            # Убеждаемся что колонка существует
            self.ensure_grade_column_exists(self.current_class, grade_num)
            
            # Обновляем оценку в базе
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = ? WHERE id_uchenika = ?", 
                          (grade_value, self.current_student_id))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", f"Оценка {grade_value} установлена ученику")
            self.load_grades_table()  # Обновляем таблицу
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить оценку: {str(e)}")
            
    def delete_grade(self):
        """Удаляет оценку выбранному ученику"""
        if not self.current_student_id or not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика и класс")
            return
            
        grade_num = self.spinBox_grade_num.value()
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            # Устанавливаем NULL вместо оценки
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = NULL WHERE id_uchenika = ?", 
                          (self.current_student_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", f"Оценка №{grade_num} удалена")
            self.load_grades_table()  # Обновляем таблицу
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить оценку: {str(e)}")
            
    def on_grade_cell_changed(self, row, column):
        """Обработчик изменения ячейки таблицы оценок"""
        if column < 2:  # Пропускаем колонки ID и имени
            return
            
        try:
            # Получаем ID ученика из первой колонки
            student_id_item = self.tableWidget_grades.item(row, 0)
            if not student_id_item:
                return
                
            student_id = int(student_id_item.text())
            
            # Определяем номер оценки из номера колонки
            grade_num = column - 1  # -2 для ID и имени, +1 т.к. оценки с 1
            
            # Получаем значение из ячейки
            grade_item = self.tableWidget_grades.item(row, column)
            if not grade_item:
                return
                
            grade_text = grade_item.text().strip()
            
            if grade_text == "":
                # Удаляем оценку если поле пустое
                grade_value = None
            else:
                try:
                    grade_value = int(grade_text)
                    if grade_value < 1 or grade_value > 5:
                        QMessageBox.warning(self, "Ошибка", "Оценка должна быть от 1 до 5")
                        self.load_grades_table()  # Восстанавливаем предыдущее значение
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Введите число от 1 до 5")
                    self.load_grades_table()  # Восстанавливаем предыдущее значение
                    return
            
            # Убеждаемся что колонка существует
            self.ensure_grade_column_exists(self.current_class, grade_num)
            
            # Обновляем в базе данных
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = ? WHERE id_uchenika = ?", 
                          (grade_value, student_id))
            conn.commit()
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить оценку: {str(e)}")
            self.load_grades_table()  # Восстанавливаем таблицу при ошибке
            
    def on_grade_cell_double_clicked(self, row, column):
        """Обработчик двойного клика по ячейке оценки"""
        if column >= 2:  # Только для колонок с оценками
            self.tableWidget_grades.editItem(self.tableWidget_grades.item(row, column))
        
    def set_task_student(self):
        """Выдает задание выбранному ученику"""
        if not self.current_student_id:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика")
            return
            
        extended_mode = self.calculate_extended_mode()
        number_range = self.get_number_range()
        actions_count = self.spinBox_actions.value()
        variables_count = self.spinBox_variables.value() if self.checkBox_variables.isChecked() else 0
        examples_count = self.get_examples_count()
        grading_system = self.get_grading_system()
        max_number = self.spinBox_max.value()
        grading_criteria = self.format_grading_criteria()
        
        # Шифруем максимальное число перед сохранением
        encoded_max = self.encode_max_number(max_number)
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            # Сохраняем расширенный режим (64 бита) в поле rezh и зашифрованное максимальное число
            # и отдельно сохраняем критерии оценивания в grading_criteria
            cursor.execute("UPDATE ucheniki SET rezh = ?, max_number = ?, grading_criteria = ? WHERE id = ?", 
                          (extended_mode, encoded_max, grading_criteria, self.current_student_id))
            conn.commit()
            conn.close()
            
            message = (f"Задание выдано ученику\n"
                      f"Диапазон: {number_range[0]}-{number_range[1]}\n"
                      f"Число действий: {actions_count}\n"
                      f"Количество примеров: {examples_count}\n"
                      f"Принцип оценки: {grading_system}\n"
                      f"Максимальное число: {max_number}")
            if variables_count > 0:
                message += f"\nЧисло переменных: {variables_count}"
                
            QMessageBox.information(self, "Успех", message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выдать задание: {str(e)}")
            
    def set_task_class(self):
        """Выдает задание всему классу"""
        if not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите класс")
            return
            
        extended_mode = self.calculate_extended_mode()
        number_range = self.get_number_range()
        actions_count = self.spinBox_actions.value()
        variables_count = self.spinBox_variables.value() if self.checkBox_variables.isChecked() else 0
        examples_count = self.get_examples_count()
        grading_system = self.get_grading_system()
        max_number = self.spinBox_max.value()
        grading_criteria = self.format_grading_criteria()
        
        # Шифруем максимальное число перед сохранением
        encoded_max = self.encode_max_number(max_number)
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT id_uchenika FROM {self.current_class}")
            student_ids = [row[0] for row in cursor.fetchall()]
            
            for student_id in student_ids:
                # Сохраняем расширенный режим (64 бита) в поле rezh и зашифрованное максимальное число
                # и отдельно сохраняем критерии оценивания в grading_criteria
                cursor.execute("UPDATE ucheniki SET rezh = ?, max_number = ?, grading_criteria = ? WHERE id = ?", 
                              (extended_mode, encoded_max, grading_criteria, student_id))
            
            conn.commit()
            conn.close()
            
            message = (f"Задание выдано {len(student_ids)} ученикам\n"
                      f"Диапазон: {number_range[0]}-{number_range[1]}\n"
                      f"Число действий: {actions_count}\n"
                      f"Количество примеров: {examples_count}\n"
                      f"Принцип оценки: {grading_system}\n"
                      f"Максимальное число: {max_number}")
            if variables_count > 0:
                message += f"\nЧисло переменных: {variables_count}"
                
            QMessageBox.information(self, "Успех", message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выдать задание: {str(e)}")
        
    def go_back(self):
        """Возврат к предыдущему окну"""
        if self.parent_window:
            self.parent_window.show()
        self.close()