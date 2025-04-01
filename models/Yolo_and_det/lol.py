import cv2
import os
from ultralytics import YOLO

# COCO id для собаки (в стандартном наборе классов COCO собака имеет id=16)
DOG_CLASS_ID = 16

# Папка для сохранения вырезанных изображений
base_output_dir = "dogs_crops"
os.makedirs(base_output_dir, exist_ok=True)

def main():
    # Загрузка модели YOLO (убедитесь, что используете версию с поддержкой трекинга, например, YOLOv8)
    model = YOLO("yolov8m.pt")  # замените на корректный путь к весам модели

    # Запуск трекинга на видео (или установите source=0 для камеры)
    results = model.track(source="IMG_2295.MOV", show=True, stream=True, conf=0.5)
    
    # Используем enumerate для получения номера кадра
    for frame_num, result in enumerate(results):
        frame = result.orig_img  # исходный кадр

        # Обработка всех обнаруженных объектов на кадре
        for box in result.boxes:
            # Если объект принадлежит классу собаки
            if int(box.cls[0]) == DOG_CLASS_ID:
                # Получаем координаты bounding box (x1, y1, x2, y2)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Вырезаем область, содержащую собаку
                dog_crop = frame[y1:y2, x1:x2]

                # Получаем id отслеживания (если доступен, иначе по умолчанию 0)
                dog_id = int(box.id) if box.id is not None else 0

                # Создаем папку для данной собаки, если её ещё нет
                dog_folder = os.path.join(base_output_dir, f"dog_{dog_id}")
                os.makedirs(dog_folder, exist_ok=True)

                # Формируем имя файла и сохраняем вырезанный bounding box
                output_path = os.path.join(dog_folder, f"crop_{frame_num}.jpg")
                cv2.imwrite(output_path, dog_crop)
                print(f"Сохранён вырезанный bounding box собаки с id {dog_id} из кадра {frame_num} в {output_path}")

if __name__ == "__main__":
    main()
