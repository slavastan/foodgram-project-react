[![foodgram workflow](https://github.com/slavastan/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/slavastan/foodgram-project-react/actions/workflows/main.yml)

Проект доступен по адресу http://62.84.122.155/
# Foodgram
***
### Описание проекта:

Foodgram - сервис «Продуктового помощника». Тут пользователи могут оставлять свои рецепты, добавлять рецепты по своим предпочтениям в "избранное", подписываться на тех пользователей, за публикациями которых им интересно следить, а так же скачивать список продуктов, которые необходимы для приготовления выбранных ими блюд.

### Технологии:
- [Python 3.9](https://www.python.org/)
- [Django 3.2.9](https://www.djangoproject.com/) - фреймворк для веб-приложений
- [Django REST framework 3.12.4](https://www.django-rest-framework.org/) (DRF) - мощный и гибкий инструмент для построения Web API.
- [Docker](https://www.docker.com/) - это программное обеспечение для автоматизации развёртывания и управления приложениями в средах с поддержкой контейнеризации, контейнеризатор приложений.
- [Gunicorn](https://gunicorn.org/) - это HTTP-сервер Python WSGI для UNIX.
- [nginx](https://www.nginx.com/) — это HTTP-сервер и обратный прокси-сервер, почтовый прокси-сервер, а также TCP/UDP прокси-сервер общего назначения

### Запуск проекта:
- Клонировать репозиторий с гитхаб
- Создать и активировать виртуальное окружение
- Установить перечень зависимостей проекта командой:
```
pip install -r requirements.txt
```
- Запустить docker-compose командой:
```
docker-compose up -d
```
- Выполнить миграции, собрать статику проекта и загрузить в проект данные командами:
```
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py collectstatic
docker-compose exec app python manage.py load_data
```
- Создать суперпользователя командой:
```
docker-compose exec web python manage.py createsuperuser
```

### Автор проекта
Вячеслав Сининкин
