# vib_r.py
import sys
import os

from primer import primer
from vichesleniya import EquationGenerator

from PyQt5 import QtCore, QtGui, QtWidgets
from viber_rezh import Ui_MainWindow

class viberr_rezhh(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent_window = parent
        self.pushButton_2.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.prov_rezh)
        self.showFullScreen()

    def prov_rezh(self):
        index1 = self.comboBox_3.currentIndex()
        index3 = self.comboBox_4.currentIndex()
        params = {'actions_count': (index3 + 1)}
        
        if((self.checkBox_5.checkState() == QtCore.Qt.Unchecked) and 
           (self.checkBox_6.checkState() == QtCore.Qt.Unchecked) and 
           (self.checkBox_7.checkState() == QtCore.Qt.Unchecked) and 
           (self.checkBox_8.checkState() == QtCore.Qt.Unchecked)):
            self.label_3.setText("Нельзя продолжать не выбрав действия!")
            return
            
        if index1 == 0:
            params['min_val'] = 1
            params['max_val'] = 10
        elif index1 == 1:
            params['min_val'] = 1
            params['max_val'] = 100
        elif index1 == 2:
            params['min_val'] = 0
            params['max_val'] = 1000
            
        oper = {}
        if self.checkBox_5.isChecked():
            oper['addition'] = True
        else:
            oper['addition'] = False
        if self.checkBox_6.isChecked():
            oper['subtraction'] = True
        else:
            oper['subtraction'] = False
        if self.checkBox_7.isChecked():
            oper['multiplication'] = True
        else:
            oper['multiplication'] = False
        if self.checkBox_8.isChecked():
            oper['division'] = True
        else:
            oper['division'] = False
        if self.checkBox.isChecked():
            oper['variables'] = True
        else:
            oper['variables'] = False
        if self.checkBox_2.isChecked():
            oper['negatives'] = True
        else:
            oper['negatives'] = False
        if self.checkBox_3.isChecked():
            oper['fractions'] = True
        else:
            oper['fractions'] = False
        if self.checkBox_4.isChecked():
            oper['decimals'] = True
        else:
            oper['decimals'] = False
            
        params['operations'] = oper
        
        # Создаем расширенный режим (64 бита) с учетом новых настроек
        extended_mode = self.create_extended_config(params)
        
        # Тестируем генерацию уравнения (опционально)
        # self.test_equation_generation(extended_mode)
        
        self.window1 = primer(extended_mode, parent=self)
        self.window1.show()
        self.hide()

    def create_extended_config(self, params):
        """
        Создает расширенный конфиг (64 бита) для vichesleniya из массива параметров
        """
        # Битовая маска операций (первые 8 бит)
        mode_number = 0
        
        if params.get('operations', {}).get('addition', False):
            mode_number |= 0b00000001
        if params.get('operations', {}).get('subtraction', False):
            mode_number |= 0b00000010
        if params.get('operations', {}).get('multiplication', False):
            mode_number |= 0b00000100
        if params.get('operations', {}).get('division', False):
            mode_number |= 0b00001000
        if params.get('operations', {}).get('negatives', False):
            mode_number |= 0b00010000
        if params.get('operations', {}).get('fractions', False):
            mode_number |= 0b00100000
        if params.get('operations', {}).get('decimals', False):
            mode_number |= 0b01000000
        if params.get('operations', {}).get('variables', False):
            mode_number |= 0b10000000
            
        # Получаем значения с проверками
        actions_count = max(1, min(255, params.get('actions_count', 1)))
        min_val = max(0, min(255, params.get('min_val', 1)))  # Мин. может быть 0
        max_val = max(1, min(255, params.get('max_val', 10)))
        
        # Кодируем максимальное число
        encoded_max = self.encode_max_number(max_val)
        
        # Старый формат (32 бита): [8 бит действий][8 бит min][8 бит max][8 бит режима]
        old_extended_mode = (actions_count << 24) | (min_val << 16) | (encoded_max << 8) | mode_number
        
        # Новый формат (64 бита): [16 бит: принцип оценки][16 бит: количество примеров][32 бита: старый режим]
        # Для тренировочного режима используем специальные значения
        grading_system = 0  # 0 = стандартная система оценки (не используется в тренировке)
        examples_count = 0  # 0 = бесконечное количество примеров (только тренировка)
        
        extended_mode_64 = (grading_system << 48) | (examples_count << 32) | old_extended_mode
        
        return extended_mode_64

    def encode_max_number(self, max_number):
        """
        Кодирует максимальное число в специальный формат
        Например: 100 -> 12 (1 и 2 нуля), 1000 -> 13 (1 и 3 нуля)
        """
        if max_number < 10:
            return 10  # По умолчанию 10
            
        num_str = str(max_number)
        if num_str[0] == '1' and all(digit == '0' for digit in num_str[1:]):
            first_digit = 1
            zeros_count = len(num_str) - 1
        else:
            first_digit = int(num_str[0])
            zeros_count = len(num_str) - 1
        
        return first_digit * 10 + zeros_count

    # def test_equation_generation(self, extended_mode):

    #     try:
    #         generator = EquationGenerator()
            
    #         # Декодируем настройки для проверки
    #         config = generator.decode_extended_mode(extended_mode)
    #         print("=== ТЕСТ ГЕНЕРАЦИИ УРАВНЕНИЯ ===")
    #         print(f"Конфигурация: {config}")
            
    #         # Генерируем пример уравнения
    #         equation, steps, answer = generator.generate_from_extended_mode(extended_mode)
            
    #         print(f"Уравнение: {equation}")
    #         print(f"Ответ: {answer}")
    #         print(f"Шаги решения:\n{steps}")
    #         print("=" * 50)
            
    #     except Exception as e:
    #         print(f"Ошибка при тестировании генерации: {e}")

    def exit(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def get_current_params(self):
        index1 = self.comboBox_3.currentIndex()
        index3 = self.comboBox_4.currentIndex()
        params = {'actions_count': (index3 + 1)}
        
        if index1 == 0:
            params['min_val'] = 1
            params['max_val'] = 10
        elif index1 == 1:
            params['min_val'] = 1
            params['max_val'] = 100
        elif index1 == 2:
            params['min_val'] = 0
            params['max_val'] = 1000
            
        oper = {}
        oper['addition'] = self.checkBox_5.isChecked()
        oper['subtraction'] = self.checkBox_6.isChecked()
        oper['multiplication'] = self.checkBox_7.isChecked()
        oper['division'] = self.checkBox_8.isChecked()
        oper['variables'] = self.checkBox.isChecked()
        oper['negatives'] = self.checkBox_2.isChecked()
        oper['fractions'] = self.checkBox_3.isChecked()
        oper['decimals'] = self.checkBox_4.isChecked()
        
        params['operations'] = oper
        return params