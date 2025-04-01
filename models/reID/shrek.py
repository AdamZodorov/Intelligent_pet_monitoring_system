# shrek.py
import os
import re
import zipfile
import shutil
import subprocess
from collections import Counter
import json
import requests

API_KEY = ""

def get_filename_from_cd(cd_header):
    if not cd_header:
        return None
    fname_match = re.findall(r'filename="([^"]+)"', cd_header)
    if fname_match:
        return fname_match[0]
    return None

def fetch_pets_photos_archive(video_id):
    """Запрашивает архив с фото по video_id через API."""
    url = f"https://petmonitoringsystem.ru/api/ai/pets-photos/{video_id}"
    headers = {"X-API-KEY": API_KEY}
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        print("Ошибка запроса:", e)
        return None
    if response.status_code == 200:
        cd_header = response.headers.get("Content-Disposition")
        print("Content-Disposition:", cd_header)
        filename = get_filename_from_cd(cd_header)
        if not filename:
            filename = f"pets_photos_{video_id}.zip"
        try:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Архив сохранён: {filename}")
        except Exception as e:
            print("Ошибка сохранения архива:", e)
            return None
        return filename
    elif response.status_code == 404:
        try:
            error_message = response.json().get("error", "Не найдено")
        except:
            error_message = "Не найдено"
        print("Ошибка:", error_message)
    else:
        print("Неожиданный статус:", response.status_code)
    return None

def extract_archive(zip_filename, extraction_path):
    """Распаковывает архив во временную директорию."""
    if not os.path.exists(extraction_path):
        os.makedirs(extraction_path, exist_ok=True)
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extraction_path)
    print(f"Распакован архив {zip_filename} в {extraction_path}")
    return extraction_path

def remove_folder_if_exists(path):
    """Удаляет папку, если существует."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Папка {path} удалена")
        except Exception as e:
            print(f"Ошибка удаления {path}: {e}")

def is_dog_in_dataset(dog_id, dataset_dirs):
    """
    Проверяет, присутствуют ли в датасете файлы, начинающиеся с '100{dog_id}_'.
    """
    prefix = f"100{dog_id}_"
    for d in dataset_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(".jpg") and f.startswith(prefix):
                    return True
    return False

def distribute_photos(extracted_dir, train_dir, query_dir, gallery_dir):
    """
    Перебирает папки внутри extracted_dir, каждая папка - dog_id.
    Файлы "1.jpg", "2.jpg", ... распределяются в train/query/gallery.
    """
    new_data_added = False
    dataset_dirs = [train_dir, query_dir, gallery_dir]
    for d in dataset_dirs:
        os.makedirs(d, exist_ok=True)

    for dog_id in os.listdir(extracted_dir):
        dog_path = os.path.join(extracted_dir, dog_id)
        if os.path.isdir(dog_path):
            if is_dog_in_dataset(dog_id, dataset_dirs):
                print(f"Собака {dog_id} уже есть в датасете. Пропуск.")
                continue
            print(f"Добавляем фото собаки {dog_id} в датасет...")
            for fname in os.listdir(dog_path):
                m = re.match(r'^(\d+)\.jpg$', fname, re.IGNORECASE)
                if not m:
                    continue
                n = int(m.group(1))
                if n in (1,2,3,4):
                    target_dir = train_dir
                elif n == 5:
                    target_dir = query_dir
                elif n in (6,7,8):
                    target_dir = gallery_dir
                else:
                    print(f"Пропуск файла {fname} - номер {n} вне диапазона [1..8]")
                    continue
                new_name = f"100{dog_id}_c1s{n}_{n}.jpg"
                src = os.path.join(dog_path, fname)
                dst = os.path.join(target_dir, new_name)
                try:
                    os.rename(src, dst)
                    print(f"Перемещён {src} -> {dst}")
                    new_data_added = True
                except Exception as e:
                    print(f"Ошибка перемещения {src}: {e}")
    return new_data_added

def run_training():
    """Запускает обучение ReID после добавления новых собак."""
    print("Запускаем обучение...")
    cmd = 'python train_clipreid.py --config_file="configs/MPDD/vit_clipreid.yml"'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Ошибка обучения:", e)

def get_unique_video_ids(directory):
    """
    Ищем файлы .mp4, содержащие в названии 'video_?(\d+)'.
    """
    video_ids = set()
    for file in os.listdir(directory):
        if file.endswith('.mp4'):
            m = re.search(r'video_?(\d+)', file)
            if m:
                video_ids.add(m.group(1))
    return list(video_ids)

def run_inference_on_image(img_path, config_file, weight_file, dataset_root, device):
    """
    Запускает inference_custom.py через subprocess и парсит результат.
    Ожидаем строку: "Predicted dog id: XXX, similarity: YYY"
    """
    cmd = [
        "python", "inference_custom.py",
        "--config_file", config_file,
        "--weight_file", weight_file,
        "--input_image", img_path,
        "--dataset_root", dataset_root,
        "--device", device
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = res.stdout.strip()
        m = re.search(r"Predicted dog id:\s*(\S+),", out)
        if m:
            return m.group(1)
        else:
            print(f"Не удалось распарсить вывод:\n{out}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Ошибка инференса для {img_path}:\n{e}\nStderr:\n{e.stderr}")
        return None

def process_inference_folder(folder_path, config_file, weight_file, dataset_root, device):
    """
    Для папки (например, /mnt/c/pet_vid/video6_dog_1_first_frame_2_frames)
    перебирает все .jpg файлы, запускает инференс и делает голосование (majority vote).
    Возвращает итоговый наиболее часто предсказанный dog id (или None, если нет предсказаний).
    """
    preds = []
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(".jpg"):
            img_path = os.path.join(folder_path, fname)
            pid = run_inference_on_image(img_path, config_file, weight_file, dataset_root, device)
            if pid:
                preds.append(pid)
    if preds:
        cnt = Counter(preds)
        most_common, _ = cnt.most_common(1)[0]
        print(f"Голосование в {folder_path}: {dict(cnt)} -> итог id: {most_common}")
        return most_common
    else:
        print(f"В папке {folder_path} нет предсказаний.")
        return None

def update_existing_json_from_folder(folder_name, recognized_id):
    """
    Определяет соответствующий JSON по названию папки.
    Например, если папка называется "video6_dog_12_first_frame_277_frames",
    то соответствующий JSON-файл ожидается как "video6_dog_12_first_frame_277.json" в папке /mnt/c/pet_vid.
    
    После извлечения JSON обновляется поле "petId" значением recognized_id.
    Перед записью из recognized_id вычитается 1000 и передаётся как число.
    
    Если JSON не найден, обновление не производится.
    """
    if folder_name.endswith("_frames"):
        base = folder_name[:-7]
    else:
        base = folder_name
    json_filename = base + ".json"
    json_path = os.path.join("/mnt/c/pet_vid", json_filename)
    if not os.path.exists(json_path):
        print(f"JSON-файл {json_path} не найден. Обновление пропущено.")
        return
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения {json_path}: {e}")
        return
    try:
        pet_id_num = int(str(recognized_id)[3:])
    except Exception as e:
        print(f"Ошибка преобразования recognized_id {recognized_id}: {e}")
        return
    data["petId"] = pet_id_num
    try:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON {json_path} обновлён: petId = {pet_id_num}")
    except Exception as e:
        print(f"Ошибка записи в {json_path}: {e}")

if __name__ == "__main__":
    videos_dir   = "/mnt/c/pet_vid"
    logs_dir     = "/mnt/c/reID/logs"
    temp_extract = "/mnt/c/reID/temp_extracted"

    train_dir   = "/mnt/c/reID/data/MPDD/train"
    query_dir   = "/mnt/c/reID/data/MPDD/query"
    gallery_dir = "/mnt/c/reID/data/MPDD/gallery"

    config_file  = "configs/MPDD/vit_clipreid.yml"
    weight_file  = "./logs/mpdd/ViT-B-16_30.pth"
    dataset_root = "/mnt/c/reID/data"
    device       = "cuda"

    vids = get_unique_video_ids(videos_dir)
    if not vids:
        print("Нет видео в", videos_dir)
    else:
        print("Найдены video_id:", vids)
        new_data_added = False

        for vid in vids:
            print("Обработка video_id:", vid)
            zipfile_name = fetch_pets_photos_archive(vid)
            if zipfile_name:
                remove_folder_if_exists(temp_extract)
                os.makedirs(temp_extract, exist_ok=True)

                extract_archive(zipfile_name, temp_extract)
                added = distribute_photos(temp_extract, train_dir, query_dir, gallery_dir)
                if added:
                    new_data_added = True

                remove_folder_if_exists(temp_extract)
                try:
                    os.remove(zipfile_name)
                    print("Удалён архив:", zipfile_name)
                except Exception as e:
                    print("Ошибка удаления архива:", e)

        if new_data_added:
            if os.path.exists(logs_dir):
                remove_folder_if_exists(logs_dir)
            run_training()
        else:
            print("Новых собак не добавлено, обучение пропущено.")

        for item in os.listdir(videos_dir):
            folder_path = os.path.join(videos_dir, item)
            if os.path.isdir(folder_path) and re.search(r'video\d+_dog_', item, re.IGNORECASE):
                print(f"Запуск инференса на {folder_path} (модель уже обучена).")
                recognized_id = process_inference_folder(folder_path, config_file, weight_file, dataset_root, device)
                if recognized_id:
                    update_existing_json_from_folder(item, recognized_id)
                remove_folder_if_exists(folder_path)
