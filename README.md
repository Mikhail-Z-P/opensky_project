# Проект 3. Поиск информации с подключением БД

## Описание
Сбор данных о самолётах в воздухе через открытый API OpenSky Network,
получение координат стран через Nominatim и загрузка данных в PostgreSQL.

## Установка

`poetry install`

## Настройка

1. Создайте базу данных PostgreSQL: `CREATE DATABASE aeroplanes_db;`
2. Скопируйте `.env.example` в `.env` и заполните данные.

## Запуск

`poetry run python main.py`

## Проверки

`poetry run pytest`

## Структура

- `src/api_client.py` — клиенты Nominatim и OpenSky
- `src/db_manager.py` — класс DBManager для работы с PostgreSQL
- `main.py` — точка входа
- `tests/` — тесты pytest
