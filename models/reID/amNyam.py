import os
import json
import requests

json_folder = "/mnt/c/pet_vid"

api_url = "https://petmonitoringsystem.ru/api/ai/pet-stat"
API_KEY = ""

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

for filename in os.listdir(json_folder):
    if filename.lower().endswith(".json"):
        file_path = os.path.join(json_folder, filename)
        print(f"Отправка {file_path}...")
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Ошибка чтения {file_path}: {e}")
            continue
        
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=10)
        except Exception as e:
            print(f"Ошибка при отправке {file_path}: {e}")
            continue
        
        if response.status_code == 200:
            print(f"Файл {filename} успешно отправлен. Удаляю его...")
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Ошибка удаления {file_path}: {e}")
        else:
            print(f"Ошибка отправки {filename}: статус {response.status_code}\n{response.text}")
