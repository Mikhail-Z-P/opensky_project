"""
Основной модуль проекта.

Оркестрирует работу: получает данные из API Nominatim и OpenSky,
заполняет таблицы в PostgreSQL, демонстрирует методы DBManager.
"""
import time
from api_client import NominatimClient, OpenSkyClient
from db_manager import DBManager

# Список стран для мониторинга (минимум 10 для выполнения критерия оценки)
COUNTRIES = [
    "Germany",
    "France",
    "United States",
    "United Kingdom",
    "Russia",
    "China",
    "Japan",
    "Spain",
    "Italy",
    "Canada",
    "Australia",
    "Brazil",
]


def main():
    """
    Главная функция: выполняет все шаги проекта последовательно.
    """
    nominatim = NominatimClient()
    opensky = OpenSkyClient()
    db = DBManager()

    # ── Шаг 1: Создание таблиц в БД ──
    print("Создание таблиц в БД...")
    db.create_tables()
    print("Таблицы countries и aeroplanes созданы.\n")

    # ── Шаг 2: Получение координат стран через Nominatim ──
    print("Получение координат стран через Nominatim...")
    country_ids = {}
    for country in COUNTRIES:
        coords = nominatim.get_country_coordinates(country)
        if coords:
            country_id = db.insert_country(
                coords["name"], coords["latitude"], coords["longitude"]
            )
            country_ids[country] = country_id
            print(f"  {country}: lat={coords['latitude']}, lon={coords['longitude']}")
            time.sleep(1)  # лимит Nominatim: 1 запрос в секунду
        else:
            print(f"  {country}: координаты не найдены")
    print(f"В БД добавлено стран: {len(country_ids)}\n")

    # ── Шаг 3: Получение данных о самолётах через OpenSky ──
    print("Получение данных о самолётах через OpenSky...")
    states = opensky.get_all_states()
    print(f"Получено state vectors: {len(states)}")

    # ── Шаг 4: Фильтрация и сохранение самолётов в БД ──
    print("Фильтрация и сохранение самолётов...")
    aeroplanes_to_insert = []
    for state in states:
        parsed = OpenSkyClient.parse_state_vector(state)
        origin = parsed["origin_country"]
        if origin in country_ids:
            parsed["country_id"] = country_ids[origin]
            aeroplanes_to_insert.append(parsed)

    print(f"Самолётов из выбранных стран: {len(aeroplanes_to_insert)}")
    db.insert_aeroplanes_batch(aeroplanes_to_insert)
    print("Самолёты сохранены в БД.\n")

    # ── Шаг 5: Демонстрация работы методов DBManager ──
    print("=== get_countries_and_aeroplanes_count() ===")
    rows = db.get_countries_and_aeroplanes_count()
    for row in rows:
        print(f"  {row[0]}: {row[1]} самолётов")

    print("\n=== get_all_aeroplanes() (первые 5) ===")
    rows = db.get_all_aeroplanes()
    for row in rows[:5]:
        print(f"  {row}")

    print(f"Всего самолётов в БД: {len(rows)}")

    print("\n=== get_avg_speed() ===")
    avg = db.get_avg_speed()
    print(f"  Средняя скорость: {avg:.2f} м/с" if avg else "  Нет данных")

    print("\n=== get_aeroplanes_with_higher_speed() (первые 5) ===")
    rows = db.get_aeroplanes_with_higher_speed()
    for row in rows[:5]:
        print(f"  {row[1]}: {row[2]} м/с")
    print(f"Всего самолётов выше средней скорости: {len(rows)}")

    print("\n=== get_aeroplanes_with_keyword('ACA') ===")
    rows = db.get_aeroplanes_with_keyword("ACA")
    for row in rows[:5]:
        print(f"  {row}")
    print(f"Найдено: {len(rows)}")


if __name__ == "__main__":
    main()
