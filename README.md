# DRF

Django-проект с Docker. 

## Prerequisites

- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

## Setup and Run

1. **Клонируем репозиторий**
```
git clone https://github.com/your_username/your_project.git
cd your_project
```
2. **Создаем**
```
docker-compose build
```
3. **Запускаем контейнеры**
```
docker-compose up
```
Это запустит сервер.

4. **Миграции**

В терминале:
```
docker-compose exec web python manage.py migrate
```

5. **Создаем админа**
```
docker-compose exec web python manage.py create_admin
```
6. **Доступ к приложению**

Open your browser and go to `http://localhost:8000`

---

## Тесты
```
docker-compose exec web python manage.py test
```
---

## Останавливаем контейнеры
```
docker-compose down
```
