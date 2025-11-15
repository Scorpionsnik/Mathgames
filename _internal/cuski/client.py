# client.py
import requests
import json
import sys

# Укажите правильный IP сервера
SERVER_IP = "192.168.50.109"  # ваш IP сервера
SERVER_URL = f"http://{SERVER_IP}:8000/"

# GET-запрос
try:
    response_get = requests.get(SERVER_URL) 
    response_get.raise_for_status()
    print("GET-ответ:", response_get.json())
except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении GET-запроса: {e}")

# POST-запрос
try:
    uchenik = int(input("vvedi id uchenika: "))
except:
    print("ne chislo")
    sys.exit()
class_uchenika = input("vvedi class uchenika: ")
try:
    ocenka = int(input("vvedi ocenku:"))
    if ((ocenka < 6) and (ocenka > 1)):
        pass
    else:
        print("nevozmozhnaya ocenka")
        sys.exit()
        # message_to_send = {"text": "neverniy variant"}
except:
    print("nevernaya ocenka")
    sys.exit()
    # message_to_send = {"text": "neverniy variant"}
try:
    nomer_ocenki = int(input("vvedi nomer ocenki: "))
except:
    print("ne chislo")
    sys.exit()
    # message_to_send = {"text": "neverniy variant"}
mess = str(uchenik + class_uchenika + str(ocenka) + str(nomer_ocenki))
message_to_send = {"text": mess}
try:
    # ИСПРАВЬТЕ ЭТУ СТРОКУ - используйте SERVER_URL вместо localhost!
    response_post = requests.post(SERVER_URL, json=message_to_send)
    response_post.raise_for_status()
    response_data = response_post.json()  # ← сначала получаем данные
    print(response_data.get('message', 'Нет сообщения'))  # ← теперь работает
except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении POST-запроса: {e}")
