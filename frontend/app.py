from flask import Flask, render_template, request, url_for

app = Flask(
    __name__,
    template_folder="templates",  # путь к папке с HTML
    static_folder="static"        # путь к папке со статикой (CSS/JS)
)

# Главная страница
@app.route("/")
def main_page():
    return render_template("main_page.html")


# Аутентификация для работников
@app.route("/auth_for_workers")
def auth_for_workers():
    return render_template("auth_for_workers.html")


# Статистика камеры для работников
@app.route("/camera_stat_workers")
def camera_stat_workers():
    return render_template("camera_stat_workers.html")


# Камеры работников
@app.route("/cameras_workers")
def cameras_workers():
    return render_template("cameras_workers.html")


# Статистика питомцев для пользователей с информацией из stat_and_video_clients
@app.route("/pets_stat_users")
def pets_stat_users():
    # Получаем параметр animal_id из GET-запроса (например, /pets_stat_users?animal_id=1)
    animal_id = request.args.get("animal_id", type=int)

    # Словарь с данными о животных
    shelters_animals = {
        1: {"id": 1, "name": "Барсик", "description": "Кот, 2 года"},
        2: {"id": 2, "name": "Мурзик", "description": "Кот, 1 год"},
        3: {"id": 3, "name": "Рыжик", "description": "Кот, 3 года"},
        4: {"id": 4, "name": "Снежок", "description": "Кот, 5 лет"},
        5: {"id": 5, "name": "Грей", "description": "Кот, 4 года"},
        6: {"id": 6, "name": "Шарик", "description": "Пёс, 4 года"},
        7: {"id": 7, "name": "Мурка", "description": "Кошка, 1 год"},
        8: {"id": 8, "name": "Снежка", "description": "Кошка, 2 года"},
        9: {"id": 9, "name": "Луна", "description": "Кошка, 3 года"},
        10: {"id": 10, "name": "Карамелька", "description": "Кошка, 1.5 года"},
        11: {"id": 11, "name": "Соня", "description": "Кошка, 4 года"},
        12: {"id": 12, "name": "Буся", "description": "Кошка, 6 лет"},
        13: {"id": 13, "name": "Рекс", "description": "Собака, 6 лет"},
        14: {"id": 14, "name": "Джек", "description": "Собака, 3 года"},
        15: {"id": 15, "name": "Тигра", "description": "Кот, 2 года"},
        16: {"id": 16, "name": "Лео", "description": "Кот, 1 год"},
        17: {"id": 17, "name": "Симба", "description": "Кот, 3 года"},
        18: {"id": 18, "name": "Барон", "description": "Кот, 4 года"},
        19: {"id": 19, "name": "Честер", "description": "Кот, 5 лет"},
        20: {"id": 20, "name": "Гарри", "description": "Кот, 2.5 года"},
        21: {"id": 21, "name": "Ричард", "description": "Кот, 6 лет"},
        22: {"id": 22, "name": "Феликс", "description": "Кот, 3.5 года"},
        23: {"id": 23, "name": "Байрон", "description": "Кот, 2 года"},
        24: {"id": 24, "name": "Оскар", "description": "Кот, 7 лет"},
        25: {"id": 25, "name": "Белка", "description": "Собака, 2 года"},
        26: {"id": 26, "name": "Стрелка", "description": "Собака, 3 года"},
        27: {"id": 27, "name": "Лайка", "description": "Собака, 4 года"},
        28: {"id": 28, "name": "Тузик", "description": "Собака, 5 лет"},
        29: {"id": 29, "name": "Гром", "description": "Собака, 3 года"},
        30: {"id": 30, "name": "Васька", "description": "Кот, 1 год"},
        31: {"id": 31, "name": "Пушок", "description": "Кот, 2 года"},
        32: {"id": 32, "name": "Черныш", "description": "Кот, 3 года"},
        33: {"id": 33, "name": "Рыжуля", "description": "Кот, 4 года"},
        34: {"id": 34, "name": "Дружок", "description": "Пёс, 5 лет"},
        35: {"id": 35, "name": "Бим", "description": "Пёс, 2 года"},
        36: {"id": 36, "name": "Зефир", "description": "Кошка, 1 год"},
        37: {"id": 37, "name": "Маркиз", "description": "Кошка, 2 года"},
        38: {"id": 38, "name": "Соня", "description": "Кошка, 3 года"},
        39: {"id": 39, "name": "Буся", "description": "Кошка, 4 года"},
        40: {"id": 40, "name": "Глория", "description": "Кошка, 5 лет"},
        41: {"id": 41, "name": "Тиффани", "description": "Кошка, 6 лет"},
        42: {"id": 42, "name": "Лейла", "description": "Кошка, 7 лет"},
        43: {"id": 43, "name": "Рокки", "description": "Собака, 6 лет"},
        44: {"id": 44, "name": "Дейзи", "description": "Собака, 3 года"},
        45: {"id": 45, "name": "Макс", "description": "Собака, 4 года"},
        46: {"id": 46, "name": "Сэм", "description": "Собака, 5 лет"},
        47: {"id": 47, "name": "Бадди", "description": "Собака, 6 лет"},
        48: {"id": 48, "name": "Ральф", "description": "Собака, 7 лет"},
        49: {"id": 49, "name": "Чарли", "description": "Собака, 8 лет"},
        50: {"id": 50, "name": "Оскар", "description": "Собака, 2 года"},
        51: {"id": 51, "name": "Лаки", "description": "Собака, 3.5 года"},
        52: {"id": 52, "name": "Шон", "description": "Собака, 9 лет"},
        53: {"id": 53, "name": "Гарфилд", "description": "Кот, 2 года"},
        54: {"id": 54, "name": "Том", "description": "Кот, 1 год"},
        55: {"id": 55, "name": "Белла", "description": "Собака, 2 года"},
        56: {"id": 56, "name": "Луна", "description": "Собака, 3 года"},
        57: {"id": 57, "name": "Чарли", "description": "Собака, 4 года"},
        58: {"id": 58, "name": "Тедди", "description": "Собака, 5 лет"},
        59: {"id": 59, "name": "Кай", "description": "Собака, 6 лет"},
        60: {"id": 60, "name": "Райли", "description": "Собака, 7 лет"}
    }

    # Если animal_id не передан или его нет в словаре, возвращаем ошибку
    if animal_id is None or animal_id not in shelters_animals:
        return "Животное не найдено", 404

    animal_name = shelters_animals[animal_id]["name"]
    # Преобразуем описание в список, чтобы цикл в шаблоне отработал корректно
    stats = [shelters_animals[animal_id]["description"]]
    # URL фотографии; если фото нет, используем изображение по умолчанию
    if "Кот" in shelters_animals[animal_id]["description"] or "Кошка" in shelters_animals[animal_id]["description"]:
        animal_photo_url = url_for('static', filename='cat.jpg')
    else:
        animal_photo_url = url_for('static', filename='dog.jpg')

    return render_template(
        "pets_stat_users.html",
        animal_name=animal_name,
        stats=stats,
        animal_photo_url=animal_photo_url
    )




# Статистика питомцев для работников
@app.route("/pets_stat_workers")
def pets_stat_workers():
    return render_template("pets_stat_workers.html")


# Питомцы работников
@app.route("/pets_workers")
def pets_workers():
    return render_template("pets_workers.html")


# Поиск клиентов – заглушка для API-запросов
@app.route("/search_for_clients", methods=["GET"])
def search_for_clients():
    # Параметр запроса из формы
    query = request.args.get("query", "")

    # Заглушка: список приютов
    shelters = [
        {
            "id": 1,
            "name": "Приют 1",
            "address": "Покровская, 1",
            "link": "https://www.mos.ru/city/projects/pets/priyut/"
        },
        {
            "id": 2,
            "name": "Приют 2",
            "address": "Троицкая, 5",
            "link": "https://vao-priut.org/"
        },
        {
            "id": 3,
            "name": "Приют 3",
            "address": "Новослободская, 3",
            "link": "https://priut-kozhuhovo.com/"
        },
        {
            "id": 4,
            "name": "Приют 4",
            "address": "Тереньевская, 14",
            "link": "https://yandex.ru/maps/213/moscow/category/animal_shelter/16058225738/"
        },
        {
            "id": 5,
            "name": "Приют 5",
            "address": "Ленинский пр-т, 10",
            "link": "https://kotodommurlyka.ru/"
        },
        {
            "id": 6,
            "name": "Приют 6",
            "address": "ул. Пушкина, 25",
            "link": "https://murkosha.ru/?utm_source=google&utm_medium=maps&utm_campaign=company_card&utm_content=site"
        },
        {
            "id": 7,
            "name": "Приют 7",
            "address": "пр. Мира, 15",
            "link": "http://vao-priut.org/links/munitsipalnyi-priyut-dlya-bezdomnykh-zhivotnykh-khimki"
        },
        {
            "id": 8,
            "name": "Приют 8",
            "address": "ул. Гагарина, 7",
            "link": "https://izpriuta.ru/"
        },
        {
            "id": 9,
            "name": "Приют 9",
            "address": "ул. Солнечная, 42",
            "link": "https://suncats.ru/"
        },
        {
            "id": 10,
            "name": "Приют 10",
            "address": "пр. Космонавтов, 8",
            "link": "https://spacepaws.org/"
        },
        {
            "id": 11,
            "name": "Приют 11",
            "address": "ул. Лесная, 15А",
            "link": "https://forestfriends.ru/"
        },
        {
            "id": 12,
            "name": "Приют 12",
            "address": "пер. Цветочный, 3",
            "link": "https://flowerpets.com/"
        }
    ]
    return render_template(
        "search_for_clients.html",
        query=query,
        shelters=shelters
    )


# Статистика и видео клиентов
@app.route("/stat_and_video_clients")
def stat_and_video_clients():
    # Получаем id приюта, переданный через GET-параметр
    shelter_id = request.args.get("shelter_id")

    # Преобразуем shelter_id в целое число (если нужно) и добавляем проверку
    try:
        shelter_id = int(shelter_id)
    except (TypeError, ValueError):
        shelter_id = None

    # Заглушка: список животных, можно фильтровать по shelter_id при необходимости
    shelters_animals = shelters_animals = {
    1: [
        {"id": 1, "name": "Барсик", "description": "Кот, 2 года"},
        {"id": 2, "name": "Мурзик", "description": "Кот, 1 год"},
        {"id": 3, "name": "Рыжик", "description": "Кот, 3 года"},
        {"id": 4, "name": "Снежок", "description": "Кот, 5 лет"},
        {"id": 5, "name": "Грей", "description": "Кот, 4 года"}
    ],
    2: [
        {"id": 6, "name": "Шарик", "description": "Пёс, 4 года"}
    ],
    3: [
        {"id": 7, "name": "Мурка", "description": "Кошка, 1 год"},
        {"id": 8, "name": "Снежка", "description": "Кошка, 2 года"},
        {"id": 9, "name": "Луна", "description": "Кошка, 3 года"},
        {"id": 10, "name": "Карамелька", "description": "Кошка, 1.5 года"},
        {"id": 11, "name": "Соня", "description": "Кошка, 4 года"},
        {"id": 12, "name": "Буся", "description": "Кошка, 6 лет"}
    ],
    4: [
        {"id": 13, "name": "Рекс", "description": "Собака, 6 лет"},
        {"id": 14, "name": "Джек", "description": "Собака, 3 года"}
    ],
    5: [
        {"id": 15, "name": "Тигра", "description": "Кот, 2 года"},
        {"id": 16, "name": "Лео", "description": "Кот, 1 год"},
        {"id": 17, "name": "Симба", "description": "Кот, 3 года"},
        {"id": 18, "name": "Барон", "description": "Кот, 4 года"},
        {"id": 19, "name": "Честер", "description": "Кот, 5 лет"},
        {"id": 20, "name": "Гарри", "description": "Кот, 2.5 года"},
        {"id": 21, "name": "Ричард", "description": "Кот, 6 лет"},
        {"id": 22, "name": "Феликс", "description": "Кот, 3.5 года"},
        {"id": 23, "name": "Байрон", "description": "Кот, 2 года"},
        {"id": 24, "name": "Оскар", "description": "Кот, 7 лет"}
    ],
    6: [
        {"id": 25, "name": "Белка", "description": "Собака, 2 года"},
        {"id": 26, "name": "Стрелка", "description": "Собака, 3 года"},
        {"id": 27, "name": "Лайка", "description": "Собака, 4 года"},
        {"id": 28, "name": "Тузик", "description": "Собака, 5 лет"},
        {"id": 29, "name": "Гром", "description": "Собака, 3 года"}
    ],
    7: [
        {"id": 30, "name": "Васька", "description": "Кот, 1 год"},
        {"id": 31, "name": "Пушок", "description": "Кот, 2 года"},
        {"id": 32, "name": "Черныш", "description": "Кот, 3 года"},
        {"id": 33, "name": "Рыжуля", "description": "Кот, 4 года"}
    ],
    8: [
        {"id": 34, "name": "Дружок", "description": "Пёс, 5 лет"},
        {"id": 35, "name": "Бим", "description": "Пёс, 2 года"}
    ],
    9: [
        {"id": 36, "name": "Зефир", "description": "Кошка, 1 год"},
        {"id": 37, "name": "Маркиз", "description": "Кошка, 2 года"},
        {"id": 38, "name": "Соня", "description": "Кошка, 3 года"},
        {"id": 39, "name": "Буся", "description": "Кошка, 4 года"},
        {"id": 40, "name": "Глория", "description": "Кошка, 5 лет"},
        {"id": 41, "name": "Тиффани", "description": "Кошка, 6 лет"},
        {"id": 42, "name": "Лейла", "description": "Кошка, 7 лет"}
    ],
    10: [
        {"id": 43, "name": "Рокки", "description": "Собака, 6 лет"},
        {"id": 44, "name": "Дейзи", "description": "Собака, 3 года"},
        {"id": 45, "name": "Макс", "description": "Собака, 4 года"},
        {"id": 46, "name": "Сэм", "description": "Собака, 5 лет"},
        {"id": 47, "name": "Бадди", "description": "Собака, 6 лет"},
        {"id": 48, "name": "Ральф", "description": "Собака, 7 лет"},
        {"id": 49, "name": "Чарли", "description": "Собака, 8 лет"},
        {"id": 50, "name": "Оскар", "description": "Собака, 2 года"},
        {"id": 51, "name": "Лаки", "description": "Собака, 3.5 года"},
        {"id": 52, "name": "Шон", "description": "Собака, 9 лет"}
    ],
    11: [
        {"id": 53, "name": "Гарфилд", "description": "Кот, 2 года"},
        {"id": 54, "name": "Том", "description": "Кот, 1 год"}
    ],
    12: [
        {"id": 55, "name": "Белла", "description": "Собака, 2 года"},
        {"id": 56, "name": "Луна", "description": "Собака, 3 года"},
        {"id": 57, "name": "Чарли", "description": "Собака, 4 года"},
        {"id": 58, "name": "Тедди", "description": "Собака, 5 лет"},
        {"id": 59, "name": "Кай", "description": "Собака, 6 лет"},
        {"id": 60, "name": "Райли", "description": "Собака, 7 лет"}
    ]
}


    # Здесь можно добавить логику для получения данных по shelter_id из базы или API

    return render_template("stat_and_video_clients.html", animals=shelters_animals[shelter_id], shelter_id=shelter_id)


# Статистика и видео работников
@app.route("/stat_and_video_workers")
def stat_and_video_workers():
    return render_template("stat_and_video_workers.html")


if __name__ == "__main__":
    app.run(debug=True)
