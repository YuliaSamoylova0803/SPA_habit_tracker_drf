## SPA Habit Tracker API drf
Описание проект
Бэкенд SPA приложения для трекера полезных привычек по методологии "Атомные привычки". Позволяет создавать, отслеживать и управлять привычками с напоминаниями в Telegram.

Технологический стек
- Python 3.10+
- Django 4.2
- Django REST Framework
- PostgreSQL
- Celery + Redis
- Poetry (управление зависимостями)
- JWT аутентификация
- Telegram Bot API

Установка через Poetry
1. Клонирование репозитория
bash
git clone https://github.com/YuliaSamoylova0803/SPA_habit_tracker_drf
cd habit-tracker
2. Установка Poetry
Если Poetry не установлен:
bash
curl -sSL https://install.python-poetry.org | python -
3. Установка зависимостей
bash
poetry install
4. Активация виртуального окружения
bash
poetry shell
5. Настройка окружения
Создайте .env файл:

bash
cp .env.example .env
Заполните реальными значениями (особенно SECRET_KEY, DB параметры и TELEGRAM_TOKEN).
NAME=postgres
USER=postgres
PASSWORD=postgres
SECRET_KEY=ваш-secret-key

6. Запуск сервисов
В разных терминалах:

bash
## Django сервер
poetry run python manage.py runserver

## Celery worker
poetry run celery -A config worker -l info

## Celery beat
poetry run celery -A config beat -l info
Зависимости проекта
Основные зависимости (управляются через Poetry):

toml
[tool.poetry.dependencies]
python = "^3.13"
django = "^5.2.2"
ipython = "^9.3.0"
pillow = "^11.2.1"
python-dotenv = "^1.1.0"
psycopg2-binary = "^2.9.10"
djangorestframework = "^3.16.0"
django-filter = "^25.1"
djangorestframework-simplejwt = "^5.5.0"
drf-yasg = "^1.21.10"
coverage = "^7.8.2"
celery = "^5.5.3"
eventlet = "^0.40.0"
redis = "^6.2.0"
django-celery-beat = "^2.8.1"
requests = "^2.32.4"
python-telegram-bot = "^22.1"
django-cors-headers = "^4.7.0"

toml
[tool.poetry.group.dev.dependencies]
flake8 = "^7.2.0"
black = "^25.1.0"
mypy = "^1.16.0"
isort = "^6.0.1"
Команды Poetry
Установка зависимостей: poetry install

Добавление новой зависимости: poetry add package-name

Добавление dev-зависимости: poetry add --group dev package-name

Запуск скриптов: poetry run python manage.py ...

Активация окружения: poetry shell

Конфигурация проекта
Основные настройки в файле pyproject.toml:

toml
[tool.poetry]
name = "spa-habit-tracker-drf"
version = "0.1.0"
description = ""
authors = ["Yulia Samoylova <u.u.samoylova@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
...

[tool.poetry.group.dev.dependencies]
...

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

Дополнительные команды
Миграции
bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
Тестирование
bash
poetry run python manage.py test
Проверка кода
bash
poetry run flake8
poetry run black --check .
poetry run isort --check .
Форматирование кода
bash
poetry run black .
poetry run isort .
Развертывание
Для production используйте:

bash
poetry install --without dev
Это установит только production-зависимости.

## 🚀 Локальный запуск
1. Клонируйте репозиторий:

bash
git clone https://github.com/YuliaSamoylova0803/SPA_habit_tracker_drf
cd habit-tracker

2. Запустите Docker-контейнеры:

bash
docker-compose up -d --build

3. Примените миграции:

bash
docker-compose exec backend python manage.py migrate

## 🛠 Настройка сервера

## 🌐 Демо-версия
Приложение доступно по адресу:  
🔗 [http://158.160.129.21](http://158.160.129.21)  

Требования:
Ubuntu 22.04+
Docker и Docker Compose
SSH-доступ

### Шаги:
#### Установите Docker:

bash
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

#### Скопируйте проект на сервер:

bash
scp -r .env docker-compose.yml backend/ nginx/ user@server:/opt/habit-tracker

#### Запустите систему:

bash
docker-compose up -d --build

## ⚙️ CI/CD (GitHub Actions)
#### Конфигурация автоматического деплоя:

deploy:
  steps:
    - uses: actions/checkout@v3
    - uses: webfactory/ssh-agent@v0.9.0
      with:
        ssh-private-key: ${{ secrets.SSH_KEY }}
    - run: scp -r .env docker-compose.yml backend/ nginx/ ${{ secrets.SSH_USER }}@${{ secrets.SERVER_IP }}:${{ secrets.DEPLOY_PATH }}
    - run: ssh ${{ secrets.SSH_USER }}@${{ secrets.SERVER_IP }} "cd ${{ secrets.DEPLOY_PATH }} && docker-compose up -d --build"

#### Секреты GitHub:

SSH_KEY — приватный ключ для доступа к серверу

DEPLOY_PATH — путь на сервере (/home/yulia/myapp)

## 📦 Зависимости
- Python 3.13
- Django 5.0
- PostgreSQL 14
- Redis 7
- Celery 5.3+

## Документация:
Дополнительную информацию о структуре проекта доступна по ссылке: http://localhost:8000/swagger/ -  для Swagger UI, http://localhost:8000/redoc/ - для Redoc

## Команда проекта:
+ **Юлия Самойлова** - Python-разработчик 
+ **Команда SkyPro**