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
        
        self.spinBox_min.valueChanged.connect(self.validate_number_range)
        self.spinBox_max.valueChanged.connect(self.validate_number_range)
        
        self.checkBox_variables.stateChanged.connect(self.on_variables_changed)
        
        self.tableWidget_grades.cellChanged.connect(self.on_grade_cell_changed)
        self.tableWidget_grades.cellDoubleClicked.connect(self.on_grade_cell_double_clicked)
        
        self.radioButton_standard.toggled.connect(self.on_grading_system_changed)
        self.radioButton_custom.toggled.connect(self.on_grading_system_changed)
        
        self.spinBox_examples_count.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_5.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_4.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_3.valueChanged.connect(self.validate_grading_criteria)
        self.spinBox_for_2.valueChanged.connect(self.validate_grading_criteria)
        
        self.checkBox_addition.toggled.connect(self.validate_at_least_one_operation)
        self.checkBox_subtraction.toggled.connect(self.validate_at_least_one_operation)
        self.checkBox_multiplication.toggled.connect(self.validate_at_least_one_operation)
        self.checkBox_division.toggled.connect(self.validate_at_least_one_operation)
        
    def validate_at_least_one_operation(self):
        operations_checked = [
            self.checkBox_addition.isChecked(),
            self.checkBox_subtraction.isChecked(),
            self.checkBox_multiplication.isChecked(),
            self.checkBox_division.isChecked()
        ]

    def validate_grading_criteria(self):
        examples_count = self.spinBox_examples_count.value()
        
        self.spinBox_for_5.setMaximum(examples_count)
        self.spinBox_for_4.setMaximum(examples_count)
        self.spinBox_for_3.setMaximum(examples_count)
        self.spinBox_for_2.setMaximum(examples_count)
        
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
        enabled = self.radioButton_custom.isChecked()
        self.spinBox_for_5.setEnabled(enabled)
        self.spinBox_for_4.setEnabled(enabled)
        self.spinBox_for_3.setEnabled(enabled)
        self.spinBox_for_2.setEnabled(enabled)
        
    def on_variables_changed(self, state):
        self.spinBox_variables.setEnabled(state == QtCore.Qt.Checked)
        
    def validate_number_range(self):
        min_val = self.spinBox_min.value()
        max_val = self.spinBox_max.value()
        
        if min_val > max_val:
            self.spinBox_max.setValue(min_val)
            
    def encode_max_number(self, max_number):

        if max_number <= 0:
            return 10
            
        num_str = str(max_number)
        
        if num_str[0] == '1' and all(digit == '0' for digit in num_str[1:]):
            first_digit = 1
            zeros_count = len(num_str) - 1
        else:
            first_digit = int(num_str[0])
            zeros_count = len(num_str) - 1
            
        encoded = first_digit * 10 + zeros_count
        return encoded
        
    def decode_max_number(self, encoded):

        if encoded < 10:
            return 10
            
        first_digit = encoded // 10
        zeros_count = encoded % 10
        
        decoded = first_digit * (10 ** zeros_count)
        
        max_spinbox_value = 2147483647
        if decoded > max_spinbox_value:
            return max_spinbox_value
        
        return decoded
            
    def calculate_extended_mode(self):
        mode_number = 0
        
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
            
        min_val = self.spinBox_min.value()
        max_val = self.spinBox_max.value()
        actions_count = self.spinBox_actions.value()
        
        encoded_max = self.encode_max_number(max_val)
        
        old_extended_mode = (actions_count << 24) | (min_val << 16) | (encoded_max << 8) | mode_number
        
        examples_count = self.spinBox_examples_count.value()
        extended_mode_64 = (examples_count << 32) | old_extended_mode
        
        return extended_mode_64
        
    def load_student_settings(self, student_data):
        if not student_data or len(student_data) < 8:
            self.set_default_settings()
            return
            
        max_number = student_data[6] if student_data[6] is not None else 10
        grading_criteria = student_data[7] if student_data[7] else 'standard'
        
        if max_number > 100: 
            max_number = self.decode_max_number(max_number)
        
        max_spinbox_value = 2147483647
        if max_number > max_spinbox_value:
            max_number = max_spinbox_value
        
        self.spinBox_max.setValue(max_number)
        
        if grading_criteria == 'standard':
            self.radioButton_standard.setChecked(True)
            examples_count = self.spinBox_examples_count.value()
            self.spinBox_for_5.setValue(min(8, examples_count))
            self.spinBox_for_4.setValue(min(6, examples_count))
            self.spinBox_for_3.setValue(min(4, examples_count))
            self.spinBox_for_2.setValue(1)
        else:
            self.radioButton_custom.setChecked(True)
            try:
                criteria_dict = self.parse_grading_criteria(grading_criteria)
                self.spinBox_for_5.setValue(criteria_dict.get('for_5', 8))
                self.spinBox_for_4.setValue(criteria_dict.get('for_4', 6))
                self.spinBox_for_3.setValue(criteria_dict.get('for_3', 4))
                self.spinBox_for_2.setValue(criteria_dict.get('for_2', 1))
            except:
                self.radioButton_standard.setChecked(True)
        
        rezh_value = student_data[5]
        if rezh_value is not None:
            self.load_settings_from_rezh(rezh_value)
        
        self.on_grading_system_changed() 
    
    def load_settings_from_rezh(self, rezh_value):
        if rezh_value is None:
            return
            
        examples_count = (rezh_value >> 32) & 0xFFFF
        old_extended_mode = rezh_value & 0xFFFFFFFF
        
        actions_count = (old_extended_mode >> 24) & 0xFF
        min_val = (old_extended_mode >> 16) & 0xFF
        encoded_max = (old_extended_mode >> 8) & 0xFF 
        mode_number = old_extended_mode & 0xFF
        

        max_val = self.decode_max_number(encoded_max)
        

        max_spinbox_value = 2147483647
        if max_val > max_spinbox_value:
            max_val = max_spinbox_value

        self.spinBox_actions.setValue(actions_count if actions_count > 0 else 1)
        self.spinBox_min.setValue(min_val if min_val > 0 else 0) 
        self.spinBox_max.setValue(max_val)
        self.spinBox_examples_count.setValue(examples_count if examples_count > 0 else 10)
        
        self.checkBox_addition.setChecked(bool(mode_number & 0b00000001))
        self.checkBox_subtraction.setChecked(bool(mode_number & 0b00000010))
        self.checkBox_multiplication.setChecked(bool(mode_number & 0b00000100))
        self.checkBox_division.setChecked(bool(mode_number & 0b00001000))
        self.checkBox_negatives.setChecked(bool(mode_number & 0b00010000))
        self.checkBox_fractions.setChecked(bool(mode_number & 0b00100000))
        self.checkBox_decimals.setChecked(bool(mode_number & 0b01000000))
        self.checkBox_variables.setChecked(bool(mode_number & 0b10000000))
        
        self.spinBox_variables.setEnabled(self.checkBox_variables.isChecked())
    
    def parse_grading_criteria(self, criteria_string):
        criteria_dict = {}
        try:
            if criteria_string == 'standard':
                return criteria_dict 
                
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
        if self.radioButton_standard.isChecked():
            return 'standard'
        else:
            return f"5:{self.spinBox_for_5.value()},4:{self.spinBox_for_4.value()},3:{self.spinBox_for_3.value()},2:{self.spinBox_for_2.value()}"
    
    def set_default_settings(self):
        self.spinBox_actions.setValue(1)
        self.spinBox_min.setValue(0) 
        self.spinBox_max.setValue(10)
        self.spinBox_variables.setValue(0)
        self.spinBox_examples_count.setValue(10)
        self.radioButton_standard.setChecked(True)
        self.spinBox_for_5.setValue(8)
        self.spinBox_for_4.setValue(6)
        self.spinBox_for_3.setValue(4)
        self.spinBox_for_2.setValue(1)
        self.on_grading_system_changed()
        
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
        return (self.spinBox_min.value(), self.spinBox_max.value())
    
    def get_examples_count(self):
        return self.spinBox_examples_count.value()
    
    def get_grading_system(self):
        if self.radioButton_standard.isChecked():
            return "standard"
        else:
            return f"custom:5-{self.spinBox_for_5.value()},4-{self.spinBox_for_4.value()},3-{self.spinBox_for_3.value()},2-{self.spinBox_for_2.value()}"
    
    def load_teacher_classes(self):
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
        if self.comboBox_classes.currentText():
            self.current_class = self.comboBox_classes.currentText()
            self.load_students_list()
            self.load_grades_table()
            
    def load_students_list(self):
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
        if not self.current_class:
            return
            
        self.tableWidget_grades.cellChanged.disconnect()
            
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({self.current_class})")
        columns = cursor.fetchall()
        
        grade_columns = []
        max_grade_num = 0
        for col in columns:
            if col[1].startswith('ocenka'):
                grade_columns.append(col[1])
                try:
                    grade_num = int(col[1].replace('ocenka', ''))
                    if grade_num > max_grade_num:
                        max_grade_num = grade_num
                except ValueError:
                    continue
        
        grade_columns.sort(key=lambda x: int(x.replace('ocenka', '')) if x.replace('ocenka', '').isdigit() else 0)
        
        cursor.execute(f"SELECT id_uchenika, name FROM {self.current_class}")
        students = cursor.fetchall()
        
        visible_columns_count = max(10, len(grade_columns) + 5)  
        
        self.tableWidget_grades.setRowCount(len(students))
        self.tableWidget_grades.setColumnCount(visible_columns_count)
        
        headers = ["ID", "Имя ученика"]
        for i in range(1, visible_columns_count - 1):
            headers.append(f"Оценка {i}")
        
        self.tableWidget_grades.setHorizontalHeaderLabels(headers)

        for row, student in enumerate(students):
            student_id = student[0]
            student_name = student[1]

            cursor.execute(f"SELECT {', '.join(grade_columns)} FROM {self.current_class} WHERE id_uchenika = ?", (student_id,))
            grades = cursor.fetchone()

            id_item = QtWidgets.QTableWidgetItem(str(student_id))
            id_item.setFlags(id_item.flags() & ~QtCore.Qt.ItemIsEditable) 
            self.tableWidget_grades.setItem(row, 0, id_item)

            name_item = QtWidgets.QTableWidgetItem(student_name)
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable) 
            self.tableWidget_grades.setItem(row, 1, name_item)

            if grades:
                for col_idx, grade_value in enumerate(grades):
                    table_col = col_idx + 2 
                    
                    if table_col < visible_columns_count:
                        grade_text = str(grade_value) if grade_value is not None else ""
                        grade_item = QtWidgets.QTableWidgetItem(grade_text)
                        self.tableWidget_grades.setItem(row, table_col, grade_item)
            
            for col in range(2, visible_columns_count):
                if not self.tableWidget_grades.item(row, col):
                    empty_item = QtWidgets.QTableWidgetItem("")
                    self.tableWidget_grades.setItem(row, col, empty_item)
        
        self.tableWidget_grades.resizeColumnsToContents()
        conn.close()
        
        self.tableWidget_grades.cellChanged.connect(self.on_grade_cell_changed)
        
    def on_student_selected(self, row):
        if row >= 0 and hasattr(self, 'students_data'):
            student_item = self.listWidget_students.item(row)
            if student_item:
                text = student_item.text()
                student_id = int(text.split('(ID: ')[1].split(')')[0])
                self.current_student_id = student_id
                
                student_data = self.students_data.get(student_id)
                if student_data and len(student_data) >= 8:
                    self.load_student_settings(student_data)
                    
    def ensure_grade_column_exists(self, class_name, grade_num):
        conn = sqlite3.connect('Data/vse.db')
        cursor = conn.cursor()
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
        if not self.current_student_id or not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика и класс")
            return
            
        grade_num = self.spinBox_grade_num.value() + 1 
        grade_value = self.spinBox_grade_value.value()
        
        try:
            self.ensure_grade_column_exists(self.current_class, grade_num)
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = ? WHERE id_uchenika = ?", 
                          (grade_value, self.current_student_id))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", f"Оценка {grade_value} установлена ученику в колонку {grade_num - 1}")
            self.load_grades_table() 
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить оценку: {str(e)}")
            
    def delete_grade(self):
        if not self.current_student_id or not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика и класс")
            return
            
        grade_num = self.spinBox_grade_num.value()
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = NULL WHERE id_uchenika = ?", 
                          (self.current_student_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", f"Оценка №{grade_num} удалена")
            self.load_grades_table()  # Обновляем таблицу
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить оценку: {str(e)}")
            
    def on_grade_cell_changed(self, row, column):
        if column < 2:
            return
            
        try:
            student_id_item = self.tableWidget_grades.item(row, 0)
            if not student_id_item:
                return
                
            student_id = int(student_id_item.text())

            grade_num = column - 1

            grade_item = self.tableWidget_grades.item(row, column)
            if not grade_item:
                return
                
            grade_text = grade_item.text().strip()
            
            if grade_text == "":
                grade_value = None
            else:
                try:
                    grade_value = int(grade_text)
                    if grade_value < 1 or grade_value > 5:
                        QMessageBox.warning(self, "Ошибка", "Оценка должна быть от 1 до 5")
                        self.load_grades_table()
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Введите число от 1 до 5")
                    self.load_grades_table() 
                    return
            
            self.ensure_grade_column_exists(self.current_class, grade_num)
            
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"UPDATE {self.current_class} SET ocenka{grade_num} = ? WHERE id_uchenika = ?", 
                          (grade_value, student_id))
            conn.commit()
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить оценку: {str(e)}")
            self.load_grades_table()
            
    def on_grade_cell_double_clicked(self, row, column):
        if column >= 2:
            self.tableWidget_grades.editItem(self.tableWidget_grades.item(row, column))
        
    def set_task_student(self):
        if not self.current_student_id:
            QMessageBox.warning(self, "Ошибка", "Выберите ученика")
            return
        operations_checked = [
            self.checkBox_addition.isChecked(),
            self.checkBox_subtraction.isChecked(),
            self.checkBox_multiplication.isChecked(),
            self.checkBox_division.isChecked()
        ]
        if not any(operations_checked):
            self.checkBox_addition.setChecked(True)
            QMessageBox.warning(self, "Предупреждение", "Должно быть выбрано хотя бы одно действие! Сложение включено автоматически.")
            return

        extended_mode = self.calculate_extended_mode()
        number_range = self.get_number_range()
        actions_count = self.spinBox_actions.value()
        variables_count = self.spinBox_variables.value() if self.checkBox_variables.isChecked() else 0
        examples_count = self.get_examples_count()
        grading_system = self.get_grading_system()
        max_number = self.spinBox_max.value()
        grading_criteria = self.format_grading_criteria()
        
        encoded_max = self.encode_max_number(max_number)
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
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

        if not self.current_class:
            QMessageBox.warning(self, "Ошибка", "Выберите класс")
            return
        operations_checked = [
            self.checkBox_addition.isChecked(),
            self.checkBox_subtraction.isChecked(),
            self.checkBox_multiplication.isChecked(),
            self.checkBox_division.isChecked()
        ]
        if not any(operations_checked):
            self.checkBox_addition.setChecked(True)
            QMessageBox.warning(self, "Предупреждение", "Должно быть выбрано хотя бы одно действие! Сложение включено автоматически.")
            return

        extended_mode = self.calculate_extended_mode()
        number_range = self.get_number_range()
        actions_count = self.spinBox_actions.value()
        variables_count = self.spinBox_variables.value() if self.checkBox_variables.isChecked() else 0
        examples_count = self.get_examples_count()
        grading_system = self.get_grading_system()
        max_number = self.spinBox_max.value()
        grading_criteria = self.format_grading_criteria()
        
        encoded_max = self.encode_max_number(max_number)
        
        try:
            conn = sqlite3.connect('Data/vse.db')
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT id_uchenika FROM {self.current_class}")
            student_ids = [row[0] for row in cursor.fetchall()]
            
            for student_id in student_ids:
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
        if self.parent_window:
            self.parent_window.show()
        self.close()