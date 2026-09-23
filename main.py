import time
from src.api_client import NominatimClient, OpenSkyClient
from src.db_manager import DBManager
from dotenv import load_dotenv

load_dotenv()

COUNTRIES = [
    "Russia",
    "United States",
    "China",
    "India",
    "Brazil",
    "Australia",
    "Canada",
    "Germany",
    "France",
    "Japan",
    "United Kingdom",
    "Italy",
]


def main() -> None:
    """Основной поток: координаты -> самолёты -> БД -> вывод результатов."""
    db = DBManager()
    db.create_tables()

    # Шаг 1: координаты стран -> БД
    country_id_map: dict = {}
    for country in COUNTRIES:
        coords = NominatimClient.get_country_coordinates(country)
        if coords:
            country_id = db.insert_country(
                country, coords["latitude"], coords["longitude"]
            )
            country_id_map[country] = country_id
            print(f"Страна {country} добавлена (ID={country_id}).")
        else:
            print(f"Не удалось получить координаты для {country}.")
        time.sleep(1)

    # Шаг 2: получение самолётов из OpenSky
    print("\nПолучение данных о самолётах...")
    states = OpenSkyClient.get_all_states()

    # Шаг 3: фильтрация — только самолёты из выбранных стран и в воздухе
    planes = []
    for state in states:
        parsed = OpenSkyClient.parse_state_vector(state)
        if (
            parsed["origin_country"] in country_id_map
            and parsed["on_ground"] is False
        ):
            planes.append(parsed)
    print(f"Найдено самолётов: {len(planes)}")

    # Шаг 4: массовая вставка в БД
    db.insert_aeroplanes_batch(planes, country_id_map)
    print("Данные сохранены в БД.")

    # Шаг 5: вывод результатов всех методов
    print("\n=== Страны и количество самолётов ===")
    for item in db.get_countries_and_aeroplanes_count():
        print(f"  {item['name']}: {item['aeroplanes_count']}")

    print("\n=== Средняя скорость ===")
    avg = db.get_avg_speed()
    if avg is not None:
        print(f"  {avg} м/с")
    else:
        print("  Нет данных")

    print("\n=== Самолёты со скоростью выше средней ===")
    for item in db.get_aeroplanes_with_higher_speed():
        print(f"  {item['icao24']} | {item['callsign']} | {item['velocity']} м/с")

    print("\n=== Самолёты с позывным, содержащим ACA ===")
    for item in db.get_aeroplanes_with_keyword("ACA"):
        print(f"  {item['icao24']} | {item['callsign']} | {item['origin_country']}")

    db.close()


if __name__ == "__main__":
    main()
