# server.py с расширенной проверкой
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import try_table

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def validate_message(self, data):
        """Проверка валидности сообщения"""
        errors = []
        
        # Проверка обязательных полей
        if 'text' not in data:
            errors.append("Отсутствует поле 'text'")
        
        # Проверка типа данных
        if 'text' in data and not isinstance(data['text'], str):
            errors.append("Поле 'text' должно быть строкой")
            
        # Проверка длины сообщения
        if 'text' in data and len(data['text']) > 1000:
            errors.append("Сообщение слишком длинное")
            
        # Проверка содержания
        if 'text' in data and data['text'].strip() == '':
            errors.append("Сообщение не может быть пустым")
        
        return errors
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_error(400, "Неверный JSON формат")
            return
        
        # ВАЛИДАЦИЯ СООБЩЕНИЯ
        errors = self.validate_message(data)
        
        if errors:
            # Есть ошибки валидации
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "error",
                "message": "Ошибка валидации",
                "errors": errors
            }
            print(f"❌ Ошибки валидации: {errors}")
        else:
            # Сообщение валидно
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            print(f"✅ Получено валидное сообщение: '{data['text']}'")
            
            # Разделяем строку на части
            parts = data['text'].split()
            print("Разделенные части:")
            
            # Инициализация переменных
            id_uchenika = None
            class_u = None
            ocenka = None
            nomer_ocenki = None
            
            # Обработка частей
            i = 1
            for part in parts:
                if i == 1:
                    id_uchenika = part
                elif i == 2:
                    class_u = part
                elif i == 3:
                    ocenka = part
                elif i == 4:
                    nomer_ocenki = part
                print(f"Часть {i}: {part}")
                i += 1
            
            # Добавляем оценку через импортированный модуль
            if all([id_uchenika, class_u, ocenka, nomer_ocenki]):
                try:
                    # Преобразуем типы данных
                    id_uchenika_int = int(id_uchenika)
                    ocenka_int = int(ocenka)
                    nomer_ocenki_int = int(nomer_ocenki)
                    
                    # Вызываем функцию из импортированного модуля
                    try_table.add_ocenka_requests(class_u, id_uchenika_int, ocenka_int, nomer_ocenki_int)
                    print(f"✅ Оценка добавлена через try_table.add_ocenka_requests")
                except Exception as e:
                    print(f"❌ Ошибка при добавлении оценки: {e}")
            else:
                print("❌ Не все данные получены для добавления оценки")
            
            # Создаем ответ для клиента
            response = {
                "status": "success",
                "message": f"Получено {len(parts)} частей: {parts}",
                "original_text": data['text'],
                "parts": parts
            }
            
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"message": "Привет от сервера!"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Запуск сервера на порту {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()