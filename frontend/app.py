from flask import Response, Flask, render_template, request, url_for, redirect, session
from functools import wraps
import requests
from dotenv import load_dotenv
import os
import json
import logging
import sys



app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)


load_dotenv()
app.secret_key = os.environ['FLASK_SECRET_KEY']
base_url = "http://localhost:8080"

API_EXAMPLES = {
    "shelters": [
        {
            "id": 1,
            "name": "Приют 'Лапки'",
            "description": "Приют для кошек и собак в центре города",
            "website": "https://lapki-shelter.ru"
        },
        {
            "id": 2,
            "name": "Дом для хвостов",
            "description": "Специализированный приют для собак",
            "website": "https://hvosty.org"
        }
    ],
    "shelter_pets": [
        {
            "id": 1,
            "name": "Барсик",
            "species": "Кот",
            "age": 2,
            "weight": 4.2,
            "height": 25.0,
            "breed": "Дворовый",
            "description": "Игривый и ласковый кот"
        },
        {
            "id": 2,
            "name": "Шарик",
            "species": "Собака",
            "age": 4,
            "weight": 12.5,
            "height": 45.0,
            "breed": "Дворняжка",
            "description": "Дружелюбный и активный пёс"
        }
    ],
    "pet_detail1": {
        "id": 1,
        "name": "Барсик",
        "age": 2,
        "weight": 4.2,
        "height": 25.0,
        "breed": "Дворовый",
        "species": "Кот",
        "description": "Игривый и ласковый кот"
    },
    "pet_detail2": {
        "id": 2,
        "name": "Шарик",
        "species": "Собака",
        "age": 4,
        "weight": 12.5,
        "height": 45.0,
        "breed": "Дворняжка",
        "description": "Дружелюбный и активный пёс"
    },
    "auth_response": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "shelterId": 1
    }
}



def pluralize_years(age):
    if age % 10 == 1 and age % 100 != 11:
        return "год"
    elif age % 10 in [2, 3, 4] and age % 100 not in [12, 13, 14]:
        return "года"
    else:
        return "лет"

app.jinja_env.filters["russian_years"] = pluralize_years

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'auth_token' not in session or 'shelter_id' not in session:
            # app.logger.debug("🔐 Unauthorized access — session: %s", dict(session))
            return redirect(url_for('main_page'))
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def fetch_api_data(endpoint, method='GET', data=None, files=None):
    """Универсальная функция для запросов к API с поддержкой JWT-авторизации.

    Если параметр files не None, запрос делается как multipart/form-data.
    """
    headers = {}
    if 'auth_token' in session:
        headers['Authorization'] = f'Bearer {session["auth_token"]}'
    try:
        if files:
            response = requests.request(
                method=method,
                url=f"{base_url}{endpoint}",
                files=files,
                data=data,
                headers=headers
            )
        else:
            response = requests.request(
                method=method,
                url=f"{base_url}{endpoint}",
                json=data,
                headers=headers
            )
        app.logger.debug(f"API ответ: код={response.status_code} body={response.text[:200]}")
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.HTTPError as e:
        app.logger.debug(f"API HTTPError: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        app.logger.debug(f"API RequestException: {e}")
        return None


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('main_page'))


@app.route("/")
def main_page():
    if 'auth_token' in session:
        return redirect(url_for('stat_and_video_workers'))

    # Пример данных
    # shelters_data = API_EXAMPLES["shelters"]
    # Реальный запрос:
    shelters_data = fetch_api_data("/api/shelters") or []
    if shelters_data == []:
        return render_template(
            "error.html",
            error="Приюты не найдены ! Попробуйте еще раз...")
    return render_template("main_page.html", shelters=shelters_data)


@app.route("/stat_and_video_clients")
def stat_and_video_clients():
    try:
        shelter_id = int(request.args.get("shelter_id"))
    except (TypeError, ValueError):
        return "Некорректный ID приюта", 400

    # Пример данных
    # animals_data = API_EXAMPLES["shelter_pets"]
    # shelter_data = next((s for s in API_EXAMPLES["shelters"] if s["id"] == shelter_id), None)

    # Реальные запросы:
    animals_data = fetch_api_data(f"/api/shelters/{shelter_id}/pets") or []
    shelter_data = fetch_api_data(f"/api/shelters/{shelter_id}")
    # if not animals_data:
    #     return render_template(
    #         "error.html",
    #         error="Данные о животных не найдены ! Попробуйте еще раз...")
    if not shelter_data:
        return render_template(
            "error.html",
            error="Данные о приюте не найдены ! Попробуйте еще раз...")

    for animal in animals_data:
        animal["photos"] = url_for('get_pet_photo', pet_id=animal["id"])
    return render_template(
        "stat_and_video_clients.html",
        animals=animals_data,
        shelter=shelter_data
    )


@app.route("/stat_and_video_workers")
@login_required
def stat_and_video_workers():
    shelter_id = session.get("shelter_id")

    # Пример данных
    # animals_data = API_EXAMPLES["shelter_pets"]
    # shelter_data = next((s for s in API_EXAMPLES["shelters"] if s["id"] == shelter_id), None)

    # Реальные запросы:
    animals_data = fetch_api_data(f"/api/shelters/{shelter_id}/pets") or []
    shelter_data = fetch_api_data(f"/api/shelters/{shelter_id}") or []

    # if not animals_data:
    #     session.clear()
    #     return render_template(
    #         "error.html",
    #         error="Данные о животных не найдены ! Попробуйте еще раз...")
    if not shelter_data:
        session.clear()
        return render_template(
            "error.html",
            error="Данные о приюте не найдены ! Попробуйте еще раз...")

    for animal in animals_data:
        animal["photos"] = url_for('get_pet_photo', pet_id=animal["id"])

    return render_template(
        "stat_and_video_workers.html",
        animals=animals_data,
        shelter=shelter_data,
    )


@app.route("/pets_stat_users")
def pets_stat_users():
    if 'auth_token' in session:
        return redirect(url_for('stat_and_video_workers'))

    animal_id = request.args.get("animal_id", type=int)
    if not animal_id:
        return render_template(
            "error.html",
            error="Не найден ID животного ! Попробуйте еще раз...")

    animal_data = fetch_api_data(f"/api/pets/{animal_id}")
    video = url_for('get_pet_video', pet_id=animal_id)
    if not animal_data:
        return render_template(
            "error.html",
            error="Животное не найдено ! Попробуйте еще раз...")

    activities = fetch_api_data(f"/api/pets/{animal_id}/activities")
    grouped_activities = {}

    if activities:
        for item in activities:
            activity_type = item.get("activityType", "UNKNOWN")
            start_time_raw = item.get("startTime")
            try:
                formatted_time = start_time_raw
                time = list(map(int, start_time_raw.split(":")))
                seconds = time[0] * 3600 + time[1] * 60 + time[2]
            except Exception as e:
                print(f"Ошибка форматирования времени: {e}")
                formatted_time = start_time_raw
                seconds = 0

            if activity_type not in grouped_activities:
                grouped_activities[activity_type] = []
            grouped_activities[activity_type].append({
                'formatted': formatted_time,
                'seconds': seconds
            })

    activity_data = fetch_api_data(f"/api/pets/{animal_id}/top-activities")
    if not activity_data:
        activity_data = []
    else:
        # Ограничиваем количество отображаемых активностей до 3
        activity_data = activity_data[:3]

    return render_template(
        "pets_stat_users.html",
        animal=animal_data,
        animal_photo_url=url_for('get_pet_photo', pet_id=animal_id),
        animal_id=animal_id,
        video=video,
        grouped_activities=grouped_activities,
        activity_data=activity_data
    )


@app.route("/pets_stat_workers")
@login_required
def pets_stat_workers():
    animal_id = request.args.get("animal_id", type=int)
    if not animal_id:
        session.clear()
        return render_template(
            "error.html",
            error="Не найден ID животного ! Попробуйте еще раз...")

    animal_data = fetch_api_data(f"/api/pets/{animal_id}")
    video = url_for('get_pet_video', pet_id=animal_id)
    if not animal_data:
        session.clear()
        return render_template(
            "error.html",
            error="Животное не найдено ! Попробуйте еще раз...")

    activities = fetch_api_data(f"/api/pets/{animal_id}/activities")
    grouped_activities = {}

    if activities:
        for item in activities:
            activity_type = item.get("activityType", "UNKNOWN")
            start_time_raw = item.get("startTime")
            try:
                formatted_time = start_time_raw
                time = list(map(int, start_time_raw.split(":")))
                seconds = time[0] * 3600 + time[1] * 60 + time[2]
            except Exception as e:
                print(f"Ошибка форматирования времени: {e}")
                formatted_time = start_time_raw
                seconds = 0

            if activity_type not in grouped_activities:
                grouped_activities[activity_type] = []
            grouped_activities[activity_type].append({
                'formatted': formatted_time,
                'seconds': seconds
            })
    activity_data = fetch_api_data(f"/api/pets/{animal_id}/top-activities")
    if not activity_data:
        activity_data = []
    else:
        # Ограничиваем количество отображаемых активностей до 3
        activity_data = activity_data[:3]

    return render_template(
        "pets_stat_workers.html",
        animal=animal_data,
        animal_photo_url=url_for('get_pet_photo', pet_id=animal_id),
        animal_id=animal_id,
        video=video,
        grouped_activities=grouped_activities,
        activity_data=activity_data
    )


@app.route("/auth_for_workers", methods=['GET', 'POST'])
def auth_for_workers():
    if 'auth_token' in session:
        return redirect(url_for('stat_and_video_workers'))

    if request.method == 'POST':
        # Пример успешного ответа
        # login_data = API_EXAMPLES["auth_response"]
        # Реальный запрос:
        login_data = fetch_api_data(
            "/api/auth/login",
            method='POST',
            data={
                "login": request.form.get('login'),
                "password": request.form.get('password')
            }
        )
        # app.logger.debug(f"🔐 Returned token and shelter_id by API: {login_data}")
        if login_data:
            session['auth_token'] = login_data["token"]
            session["shelter_id"] = login_data["shelterId"]
            # app.logger.debug(f"🔐 Added in session: {dict(session)}")
            return redirect(url_for('stat_and_video_workers'))


        return render_template(
            "auth_for_workers.html",
            error="Неверный логин или пароль")

    return render_template("auth_for_workers.html")


@app.route("/add_animal", methods=['GET', 'POST'])
@login_required
def add_animal():
    with open('/root/home/impl/frontend/static/breeds/dogs.json', 'r', encoding='utf-8') as f:
        dog_breeds = json.load(f)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        group = request.form.get('group')
        try:
            age = int(request.form.get('age'))
            weight = float(request.form.get('weight'))
            height = float(request.form.get('height'))
        except (ValueError, TypeError):
            return render_template(
                'add_animal.html',
                error="Некорректные числовые данные, попробуйте снова", dog_breeds=dog_breeds)
        breed = request.form.get('breed')
        species = request.form.get('species', 'Собака')

        main_photo_file = request.files.get('main_photo')
        if not main_photo_file:
            return render_template(
                'add_animal.html',
                error="Основное фото не выбрано, попробуйте снова", dog_breeds=dog_breeds)
        files = {
            'file': (
                main_photo_file.filename,
                main_photo_file.stream,
                main_photo_file.mimetype)}
        main_temp_response = fetch_api_data(
            "/api/uploads/temp", method='POST', files=files)
        if not main_temp_response or 'tempId' not in main_temp_response:
            app.logger.debug(f"🔐 Main_temp_response: {main_temp_response} ")
            return render_template(
                'add_animal.html',
                error="Ошибка загрузки основного фото, попробуйте снова", dog_breeds=dog_breeds)
        mainImageId = main_temp_response['tempId']

        additional_photos = request.files.getlist('additional_photos')
        if len(additional_photos) != 8:
            return render_template(
                'add_animal.html',
                error="Вы отправили не 8 дополнительных фото, попробуйте снова", dog_breeds=dog_breeds)
        tempImageIds = []
        for photo in additional_photos:
            files = {'file': (photo.filename, photo.stream, photo.mimetype)}
            temp_response = fetch_api_data(
                "/api/uploads/temp", method='POST', files=files)
            if not temp_response or 'tempId' not in temp_response:
                return render_template(
                    'add_animal.html',
                    error="Ошибка загрузки дополнительных фото, попробуйте снова", dog_breeds=dog_breeds)
            tempImageIds.append(temp_response['tempId'])

        pet_data = {
            "name": name,
            "age": age,
            "weight": weight,
            "description": description,
            "group": group,
            "height": height,
            "breed": breed,
            "species": species,
            "mainImageId": mainImageId,
            "tempImageIds": tempImageIds
        }

        status = fetch_api_data("/api/pets/add", method='POST', data=pet_data)
        if status is None:
            return redirect(url_for('stat_and_video_workers'))
        return render_template(
            'add_animal.html',
            error="Ошибка добавления животного")


    return render_template('add_animal.html', dog_breeds=dog_breeds)


@app.route("/delete_animal/<int:animal_id>", methods=['POST'])
@login_required
def delete_animal(animal_id):
    deletion_result = fetch_api_data(
        f"/api/pets/{animal_id}/delete",
        method='DELETE')
    if deletion_result is None:
        return redirect(url_for('stat_and_video_workers'))
    else:
        error_message = "Ошибка удаления животного"
        return render_template(
            "stat_and_video_workers.html",
            error=error_message)


@app.route("/get_pet_photo/<int:pet_id>")
def get_pet_photo(pet_id):
    headers = {}
    if 'auth_token' in session:
        headers['Authorization'] = f'Bearer {session["auth_token"]}'
    try:
        response = requests.get(
            f"{base_url}/api/pets/{pet_id}/photo",
            headers=headers)
        response.raise_for_status()
        mimetype = response.headers.get("Content-Type", "image/jpeg")
        return Response(response.content, mimetype=mimetype)
    except Exception as e:
        print(f"Error retrieving pet photo: {e}")
        return redirect(url_for('static', filename='photo/dog.jpg'))


@app.route("/get_pet_video/<int:pet_id>")
def get_pet_video(pet_id):
    headers = {}
    if 'auth_token' in session:
        headers['Authorization'] = f'Bearer {session["auth_token"]}'

    try:
        range_header = request.headers.get('Range', None)
        req_headers = {'Range': range_header} if range_header else {}
        req_headers.update(headers)

        response = requests.get(
            f"{base_url}/api/pets/{pet_id}/video",
            headers=req_headers,
            stream=True
        )

        response.raise_for_status()

        mimetype = response.headers.get("Content-Type", "video/mp4")
        content_length = response.headers.get('Content-Length')
        content_range = response.headers.get('Content-Range')

        res_headers = {}
        if content_length:
            res_headers['Content-Length'] = content_length
        if content_range:
            res_headers['Content-Range'] = content_range
        if range_header:
            res_headers['Accept-Ranges'] = 'bytes'
            res_status = 206
        else:
            res_status = 200

        return Response(
            response.iter_content(chunk_size=1024 * 1024),
            status=res_status,
            mimetype=mimetype,
            headers=res_headers,
            direct_passthrough=True
        )

    except Exception as e:
        print(f"Error retrieving pet video: {e}")
        return redirect(url_for('static', filename='video/placeholder.mp4'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
