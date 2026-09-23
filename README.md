# Проект 3. Поиск информации с подключением БД

## Описание
Проект получает данные о самолётах в воздухе через открытый API OpenSky Network
и географические координаты стран через Nominatim API, затем сохраняет данные
в базу данных PostgreSQL.

## Структура проекта
- `config.py` — конфигурация подключения к PostgreSQL (в .gitignore)
- `api_client.py` — клиенты для API Nominatim и OpenSky
- `db_manager.py` — класс DBManager для работы с БД
- `main.py` — основной модуль, оркестрирующий работу
- `requirements.txt` — зависимости проекта
- `.gitignore` — исключения для Git

## Установка
1. Клонируйте репозиторий
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте: `source venv/bin/activate` (Linux) или `venv\Scripts\activate` (Windows)
4. Установите зависимости: `pip install -r requirements.txt`
5. Создайте БД в PostgreSQL: `CREATE DATABASE aeroplanes_db;`
6. Скопируйте `config.py.example` в `config.py` и укажите свои данные
7. Запустите: `python main.py`

## Использование
Класс DBManager предоставляет методы:
- `get_countries_and_aeroplanes_count()` — страны и количество самолётов
- `get_all_aeroplanes()` — все воздушные судна
- `get_avg_speed()` — средняя скорость
- `get_aeroplanes_with_higher_speed()` — самолёты выше средней скорости
- `get_aeroplanes_with_keyword(keyword)` — поиск по позывному
