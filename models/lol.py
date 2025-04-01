import requests
import time
import re
import mimetypes
import os
import cv2
import random
from ultralytics import YOLO

API_KEY = ""
URL = "https://petmonitoringsystem.ru/api/ai/next-video"

def get_filename_from_cd(cd_header):
    """
    Извлекает имя файла из заголовка Content-Disposition, если оно задано.
    Пример формата: 'attachment; filename="video.mp4"'
    """
    if not cd_header:
        return None
    fname_match = re.findall(r'filename="([^"]+)"', cd_header)
    if fname_match:
        return fname_match[0]
    return None

def fetch_video():
    """
    Отправляет GET-запрос для получения следующего необработанного видео.
    Если видео получено успешно, сохраняет его с оригинальным именем или формирует имя файла.
    Возвращает имя сохранённого файла, либо None в случае ошибки.
    """
    headers = {"X-API-KEY": API_KEY}
    try:
        response = requests.get(URL, headers=headers)
    except requests.RequestException as error:
        print("Ошибка при выполнении запроса:", error)
        return None

    if response.status_code == 200:
        cd_header = response.headers.get('Content-Disposition')
        filename = get_filename_from_cd(cd_header)
        if not filename:
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            extension = mimetypes.guess_extension(content_type)
            if extension is None:
                extension = '.bin'
            video_id = response.headers.get("X-Video-Id", "unknown")
            filename = f"video_{video_id}{extension}"

        try:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Видео успешно сохранено в файл: {filename}")
        except IOError as io_err:
            print("Ошибка при сохранении файла:", io_err)
            return None
        return filename

    elif response.status_code == 401:
        error_message = response.json().get("message", "Ошибка авторизации")
        print("Ошибка авторизации:", error_message)
    elif response.status_code == 404:
        error_message = response.json().get("message", "Видео не найдено")
        print("Видео не найдено:", error_message)
    elif response.status_code == 500:
        error_message = response.json().get("message", "Внутренняя ошибка сервера")
        print("Внутренняя ошибка сервера:", error_message)
    else:
        print("Неожиданный статус ответа:", response.status_code)
    return None

def convert_to_mp4_opencv(input_filename):
    """
    Открывает видеофайл с помощью OpenCV и сохраняет его в формате MP4.
    Используется VideoCapture для чтения и VideoWriter для записи.
    Возвращает имя нового файла или None в случае ошибки.
    """
    basename, _ = os.path.splitext(input_filename)
    output_filename = f"{basename}_converted.mp4"

    cap = cv2.VideoCapture(input_filename)
    if not cap.isOpened():
        print("Ошибка: не удается открыть видеофайл", input_filename)
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    
    cap.release()
    out.release()
    print("Видео успешно конвертировано в MP4:", output_filename)
    return output_filename

DOG_CLASS_ID = 16

base_output_dir = "C:/pet_vid"
os.makedirs(base_output_dir, exist_ok=True)

active_tracks = {}

def extract_random_frames():
    """
    Функция проходит по всем видеофайлам в папке base_output_dir,
    для каждого видео создает отдельную подпапку и сохраняет в неё 3 случайных кадра.
    Если кадров меньше 3, то сохраняются все.
    """
    for file in os.listdir(base_output_dir):
        if file.endswith('.mp4'):
            video_path = os.path.join(base_output_dir, file)
            frames_folder = os.path.join(base_output_dir, file.replace('.mp4', '_frames'))
            os.makedirs(frames_folder, exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                continue
            num_frames_to_extract = 3 if total_frames >= 3 else total_frames
            frame_indices = sorted(random.sample(range(total_frames), num_frames_to_extract))
            current_frame = 0
            extracted_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if current_frame in frame_indices:
                    # Формируем имя для изображения, добавляем номер кадра в имя файла
                    image_filename = f"{file.replace('.mp4','')}_frame{current_frame}.jpg"
                    image_path = os.path.join(frames_folder, image_filename)
                    cv2.imwrite(image_path, frame)
                    extracted_count += 1
                current_frame += 1
            cap.release()
            print(f"Извлечено {extracted_count} рандомных кадров из видео {file} и сохранено в папке {frames_folder}")

def process_video(video_source):
    """
    Обрабатывает видео с помощью модели YOLO для трекинга собак:
      - Для каждого обнаруженного объекта (с DOG_CLASS_ID) создается сегмент видео,
        в котором вырезается bounding box объекта.
      - Если сегмент короче 1 секунды, он удаляется.
      - Затем из каждого сегмента извлекаются 3 случайных кадра.
    """
    video_id_match = re.search(r'video_(\d+)', video_source)
    if video_id_match:
        video_id = video_id_match.group(1)
    else:
        video_id = "unknown"
    
    cap = cv2.VideoCapture(video_source)
    fps_value = cap.get(cv2.CAP_PROP_FPS)
    if fps_value <= 0:
        fps_value = 30
    cap.release()
    
    MIN_FRAMES = int(fps_value)
    
    model = YOLO("yolo11m.pt")
    
    results = model.track(source=video_source, show=True, stream=True, conf=0.4, tracker="bytetrack.yaml")
    
    for frame_num, result in enumerate(results):
        frame = result.orig_img
        current_frame_ids = set()

        for box in result.boxes:
            if int(box.cls[0]) == DOG_CLASS_ID:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                dog_crop = frame[y1:y2, x1:x2]
                if dog_crop.size == 0:
                    continue
                
                dog_id = int(box.id) if box.id is not None else 0
                current_frame_ids.add(dog_id)
                
                if dog_id not in active_tracks:
                    start_frame = frame_num
                    h_crop, w_crop = dog_crop.shape[:2]
                    crop_size = (w_crop, h_crop)
                    video_filename = f"video{video_id}_dog_{dog_id}_first_frame_{start_frame}.mp4"
                    video_path = os.path.join(base_output_dir, video_filename)
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    writer = cv2.VideoWriter(video_path, fourcc, fps_value, crop_size)
                    
                    active_tracks[dog_id] = {
                        'writer': writer,
                        'start_frame': start_frame,
                        'last_seen': frame_num,
                        'crop_size': crop_size,
                        'frame_count': 0,
                        'video_path': video_path
                    }
                else:
                    active_tracks[dog_id]['last_seen'] = frame_num
                    crop_size = active_tracks[dog_id]['crop_size']
                    if (dog_crop.shape[1], dog_crop.shape[0]) != crop_size:
                        dog_crop = cv2.resize(dog_crop, crop_size)
                
                active_tracks[dog_id]['writer'].write(dog_crop)
                active_tracks[dog_id]['frame_count'] += 1

        remove_ids = []
        for track_id, info in active_tracks.items():
            if track_id not in current_frame_ids:
                if frame_num - info['last_seen'] >= 16:
                    info['writer'].release()
                    if info['frame_count'] < MIN_FRAMES:
                        try:
                            os.remove(info['video_path'])
                            print(f"Сегмент для dog_{track_id} (начало с кадра {info['start_frame']}) короче 1 секунды и удалён")
                        except Exception as e:
                            print(f"Не удалось удалить файл {info['video_path']}: {e}")
                    else:
                        print(f"Сегмент для dog_{track_id} (начало с кадра {info['start_frame']}) завершён, длительность: {info['frame_count']/fps_value:.2f} сек")
                    remove_ids.append(track_id)
        for track_id in remove_ids:
            del active_tracks[track_id]

    for track_id, info in active_tracks.items():
        info['writer'].release()
        if info['frame_count'] < MIN_FRAMES:
            try:
                os.remove(info['video_path'])
                print(f"Финальный сегмент для dog_{track_id} (начало с кадра {info['start_frame']}) короче 1 секунды и удалён")
            except Exception as e:
                print(f"Не удалось удалить файл {info['video_path']}: {e}")
        else:
            print(f"Финальный сегмент для dog_{track_id} (начало с кадра {info['start_frame']}) завершён, длительность: {info['frame_count']/fps_value:.2f} сек")

    extract_random_frames()

def main():
    """
    Основная логика:
      1. Получаем видео через API.
      2. Конвертируем его в формат MP4.
      3. Обрабатываем видео для выделения сегментов с собаками.
    """
    while True:
        print("Пытаемся получить следующее видео через API...")
        saved_filename = fetch_video()
        if saved_filename:
            print("Видео получено:", saved_filename)
            final_filename = convert_to_mp4_opencv(saved_filename)
            if final_filename:
                print("Конечный (конвертированный) файл:", final_filename)
                process_video(final_filename)
            break
        else:
            print("Видео не получено. Повторная попытка через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    main()
