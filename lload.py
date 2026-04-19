# main_window.py
from flask import Flask, request, jsonify
import json
import os
import threading
from datetime import datetime
import socket
import sys
import ast
import re
from PyQt5 import QtCore, QtGui, QtWidgets

from load import Ui_Load

from try_table import update_student_grades_from_position

def parse_grades_string(grades_input):
    """
    Преобразует строковое представление списка оценок в настоящий список.
    
    Аргументы:
        grades_input: строка с оценками в различных форматах
    
    Возвращает:
        list: список оценок (числа и None)
    """
    
    def clean_and_validate(item):
        """Очищает и валидирует отдельный элемент"""
        if item is None:
            return None
        
        # Если это строка
        if isinstance(item, str):
            item = item.strip()
            
            # Пустая строка или 'None' -> None
            if item == '' or item.lower() == 'none' or item.lower() == 'null':
                return None
            
            # Пробуем преобразовать в число
            try:
                # Заменяем запятую на точку для float
                item = item.replace(',', '.')
                if '.' in item:
                    grade = float(item)
                else:
                    grade = int(item)
                
                # Проверяем диапазон (1-5 для оценок)
                if 1 <= grade <= 5:
                    return int(grade)  # Возвращаем как int для единообразия
                else:
                    return None
            except (ValueError, AttributeError):
                # Не число -> None
                return None
        
        # Если уже число
        elif isinstance(item, (int, float)):
            if 1 <= item <= 5:
                return int(item)
            else:
                return None
        
        # Всё остальное -> None
        return None
    
    # Если уже список - просто очищаем
    if isinstance(grades_input, list):
        return [clean_and_validate(item) for item in grades_input]
    
    # Если не строка - пробуем преобразовать
    if not isinstance(grades_input, str):
        try:
            grades_input = str(grades_input)
        except:
            print(f"❌ Не удалось преобразовать {type(grades_input)} в строку")
            return []
    
    # Очищаем строку от лишних пробелов
    grades_input = grades_input.strip()
    
    # Способ 1: Пробуем распарсить как JSON
    try:
        parsed = json.loads(grades_input)
        if isinstance(parsed, list):
            print(f"✅ Распаршено через JSON: {len(parsed)} элементов")
            return [clean_and_validate(item) for item in parsed]
    except json.JSONDecodeError:
        pass
    
    # Способ 2: Пробуем через ast.literal_eval (безопасное вычисление)
    try:
        parsed = ast.literal_eval(grades_input)
        if isinstance(parsed, list):
            print(f"✅ Распаршено через ast.literal_eval: {len(parsed)} элементов")
            return [clean_and_validate(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    
    # Способ 3: Парсим вручную (для кривых форматов)
    # Убираем квадратные скобки если есть
    if grades_input.startswith('[') and grades_input.endswith(']'):
        grades_input = grades_input[1:-1]
    
    # Убираем круглые скобки если есть
    if grades_input.startswith('(') and grades_input.endswith(')'):
        grades_input = grades_input[1:-1]
    
    # Разбиваем по запятым
    parts = []
    current_part = ""
    in_quotes = False
    quote_char = None
    bracket_depth = 0
    
    for char in grades_input:
        if char in ['"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
        elif char == ',' and not in_quotes and bracket_depth == 0:
            parts.append(current_part.strip())
            current_part = ""
            continue
        
        current_part += char
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    # Очищаем каждую часть
    result = []
    for part in parts:
        # Убираем кавычки
        if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
            part = part[1:-1]
        
        # Очищаем и валидируем
        cleaned = clean_and_validate(part)
        result.append(cleaned)
    
    if result:
        print(f"✅ Распаршено вручную: {len(result)} элементов")
    
    return result

class FlaskSignals(QtCore.QObject):
    update_label = QtCore.pyqtSignal(str)

class lload(QtWidgets.QMainWindow, Ui_Load):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.signals = FlaskSignals()
        self.signals.update_label.connect(self.label_5.setText)
        self.pushButton_2.clicked.connect(self.exit)
        self.label_5.setText(self.get_local_ip())
        self.setWindowTitle("Приём оценок")
        self.show()
        self.parent=parent
        self.app = app
        self.app.add_url_rule(
            '/endpoint', 
            view_func=self.handle_data, # Указываем на метод
            methods=['POST']
        )

    def get_local_ip(self):
        """Получить свой локальный IP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def handle_data(self):
        """
        Обработчик POST запросов - сохраняет данные и возвращает ответ
        """
        try:
            # Получаем данные из запроса
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'Нет данных для сохранения',
                    'code': 'NO_DATA'
                }), 400
            
            # Добавляем метаданные
            data['received_at'] = datetime.now().isoformat()
            data['ip_address'] = request.remote_addr
            print(data)
            rres = update_student_grades_from_position(data['name'], parse_grades_string(data['grades']))
            if rres == True:
                # self.label_6.setText(f"""<html><head/><body><p align="center">✅ Успешно обновлены оценки {data['name']}</p></body></html>""")
                return jsonify({
                    'status': 'success',
                    'message': 'Данные успешно сохранены',
                    'code': 'DATA_SAVED',
                    'data': {
                        'id': data.get('user_id', 'unknown'),
                        'saved_at': data['received_at']
                    }
                }), 200

                

            else:
                # self.label_6.setText(f"""<html><head/><body><p align="center">❌ Ошибка Детали: неудалось записать</p></body></html>""")
                return jsonify({
                    'status': 'error',
                    'message': 'Данные не сохранены',
                    'code': 'DATA_NOT_SAVED'
                }), 400
                

        except json.JSONDecodeError:
            # self.label_6.setText(f"""<html><head/><body><p align="center">❌ Ошибка Детали: неверный json</p></body></html>""")
            return jsonify({
                'status': 'error',
                'message': 'Неверный формат JSON',
                'code': 'INVALID_JSON'
            }), 400
            
            
        except Exception as e:
            # self.label_6.setText(f"""<html><head/><body><p align="center">❌ Ошибка Детали: {str(e)}</p></body></html>""")
            return jsonify({
                'status': 'error',
                'message': f'Внутренняя ошибка сервера: {str(e)}',
                'code': 'SERVER_ERROR'
            }), 500
            

        
            
    
    def exit(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.parent:
            self.parent.show()
        event.accept()

def run_flask(app, host):
    # debug=False обязателен при работе с потоками!
    app.run(host=host, port=8052, debug=False, threaded=True)

if __name__ == "__main__":
    app_flask = Flask(__name__)
    
    qt_app = QtWidgets.QApplication(sys.argv)
    
    # Создаем окно
    window = lload(app_flask)
    
    # Узнаем IP
    ip = window.get_local_ip()
    print(f"Сервер запускается на http://{ip}:8052")

    # ЗАПУСК FLASK В ПОТОКЕ
    flask_thread = threading.Thread(target=run_flask, args=(app_flask, ip), daemon=True)
    flask_thread.start()

    # Запуск интерфейса
    sys.exit(qt_app.exec_())