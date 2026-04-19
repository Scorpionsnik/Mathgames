# main_window.py
import requests
import json
from typing import Optional, Dict, Any
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from send import Ui_Send

from try_table import get_student_all_grades

class send(QtWidgets.QMainWindow, Ui_Send):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # Настройка соединений
        self.pushButton_3.clicked.connect(self.send_data)
        self.pushButton_2.clicked.connect(self.exit)
        
        # Дополнительные настройки (по желанию)
        self.setWindowTitle("Отправка оценок")
        self.show()
        self.data=data
        self.parent=parent
    
    def send_data_to_server(self, ip: str, data: Dict[str, Any], port: int = 80) -> Dict[str, Any]:
        """
        Отправляет данные на сервер по IP и обрабатывает ответ
        
        Args:
            ip: IP-адрес сервера
            data: Данные для отправки
            port: Порт сервера (по умолчанию 80)
        
        Returns:
            Словарь с результатом операции
        """
        
        url = f"http://{ip}:{port}/endpoint"  # замени на свой endpoint
        
        try:
            # Отправляем POST запрос с данными в JSON формате
            response = requests.post(
                url,
                json=data,
                timeout=10,  # таймаут в секундах
                headers={'Content-Type': 'application/json'}
            )
            
            # Проверяем статус ответа
            response.raise_for_status()  # Вызовет исключение если статус не 2xx
            
            # Если успешно - возвращаем подтверждение
            return {
                'success': True,
                'message': 'Данные успешно сохранены',
                'status_code': response.status_code,
                'server_response': response.json() if response.text else None
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Ошибка подключения к серверу',
                'details': f'Не удалось подключиться к {url}'
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Таймаут соединения',
                'details': 'Сервер не ответил за отведенное время'
            }
            
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP ошибка: {response.status_code}',
                'details': str(e),
                'server_response': response.text if response.text else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': 'Ошибка при выполнении запроса',
                'details': str(e)
            }

    def send_data(self):
        ip = self.lineEdit.text()
        if ip is not None:
            for i in ip:
                try:
                    int(i)
                except:
                    if i != '.':
                        self.label_6.setText("ip должен содержать только цифры и точки")
                        return
        self.process_data(ip)
    
    def process_data(self, ip):
        self.label_6.setText(f"""<html><head/><body><p align="center">{str(ip)}</p></body></html>""")
        data_to_send = {
            "name": str(self.data[1]),
            "grades": str(get_student_all_grades(self.data[1]))
        }
        res=self.send_data_to_server(ip, data_to_send, port=8052)
        if res['success']:
            self.label_6.setText(f"""<html><head/><body><p align="center">✅ Успешно</p></body></html>""")
            print(f"✅ Успешно: {res['message']}")
            if res['server_response']:
                print(f"Ответ сервера: {res['server_response']}")
        else:
            self.label_6.setText(f"""<html><head/><body><p align="center">❌ Ошибка Детали: {res['details']}</p></body></html>""")
            print(f"❌ Ошибка: {res['error']}")
            print(f"Детали: {res['details']}")


        
            
    
    def exit(self):
        if self.parent:
            self.parent.show()
        self.close()

    def closeEvent(self, event):
        if self.parent:
            self.parent.show()
        event.accept()
