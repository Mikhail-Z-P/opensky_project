import os
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()


class DBManager:
    """Менеджер для работы с БД PostgreSQL: создание таблиц, вставка и выборка данных."""

    def __init__(self) -> None:
        """Создаёт подключение к БД на основе переменных окружения."""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "opensky_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            client_encoding="UTF8",
        )

        self.conn.autocommit = False

    def create_tables(self) -> None:
        """Создаёт таблицы countries и aeroplanes, если их ещё нет."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS aeroplanes (
                    id SERIAL PRIMARY KEY,
                    icao24 VARCHAR(10) NOT NULL,
                    callsign VARCHAR(20),
                    origin_country VARCHAR(255),
                    longitude FLOAT,
                    latitude FLOAT,
                    baro_altitude FLOAT,
                    on_ground BOOLEAN,
                    velocity FLOAT,
                    true_track FLOAT,
                    vertical_rate FLOAT,
                    geo_altitude FLOAT,
                    squawk VARCHAR(10),
                    country_id INTEGER REFERENCES countries(id),
                    UNIQUE (icao24)
                );
                """
            )
        self.conn.commit()

    def insert_country(
        self, name: str, latitude: float, longitude: float
    ) -> int:
        """
        Вставляет страну в БД. Если страна уже есть — обновляет координаты.

        :return: ID страны в БД.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO countries (name, latitude, longitude)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                RETURNING id;
                """,
                (name, latitude, longitude),
            )
            row = cur.fetchone()
            country_id = row[0] if row else None
        self.conn.commit()
        return country_id

    def insert_aeroplanes_batch(
        self,
        planes: List[Dict[str, Any]],
        country_id_map: Dict[str, int],
    ) -> None:
        """
        Массово вставляет самолёты в БД.
        Если самолёт с таким icao24 уже есть — пропускает.

        :param planes: Список словарей с данными самолётов.
        :param country_id_map: Словарь {название страны: id в БД}.
        """
        values: List[tuple] = []
        for p in planes:
            country_id = country_id_map.get(p["origin_country"])
            values.append(
                (
                    p["icao24"],
                    p["callsign"],
                    p["origin_country"],
                    p["longitude"],
                    p["latitude"],
                    p["baro_altitude"],
                    p["on_ground"],
                    p["velocity"],
                    p["true_track"],
                    p["vertical_rate"],
                    p["geo_altitude"],
                    p["squawk"],
                    country_id,
                )
            )

        if not values:
            return

        with self.conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO aeroplanes (
                    icao24, callsign, origin_country, longitude, latitude,
                    baro_altitude, on_ground, velocity, true_track,
                    vertical_rate, geo_altitude, squawk, country_id
                ) VALUES %s
                ON CONFLICT (icao24) DO NOTHING;
                """,
                values,
            )
        self.conn.commit()

    def get_countries_and_aeroplanes_count(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех стран и количество самолётов
        в их воздушном пространстве. Использует LEFT JOIN + GROUP BY.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, COUNT(a.id) AS aeroplanes_count
                FROM countries c
                LEFT JOIN aeroplanes a ON a.country_id = c.id
                GROUP BY c.name
                ORDER BY aeroplanes_count DESC;
                """
            )
            rows = cur.fetchall()
            return [
                {"name": row[0], "aeroplanes_count": row[1]} for row in rows
            ]

    def get_all_aeroplanes(self) -> List[Dict[str, Any]]:
        """Возвращает список всех воздушных судов со всеми полями."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM aeroplanes ORDER BY id;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def get_avg_speed(self) -> Optional[float]:
        """Возвращает среднюю скорость самолётов (м/с). None, если данных нет."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT AVG(velocity) FROM aeroplanes WHERE velocity IS NOT NULL;"
            )
            result = cur.fetchone()
            return float(result[0]) if result and result[0] is not None else None

    def get_aeroplanes_with_higher_speed(self) -> List[Dict[str, Any]]:
        """
        Возвращает список самолётов, у которых скорость выше средней.
        Средняя скорость вычисляется подзапросом.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT icao24, callsign, velocity
                FROM aeroplanes
                WHERE velocity > (
                    SELECT AVG(velocity) FROM aeroplanes WHERE velocity IS NOT NULL
                )
                ORDER BY velocity DESC;
                """
            )
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Возвращает самолёты, в позывном (callsign) которых содержится keyword.
        Поиск регистронезависимый (ILIKE).

        :param keyword: Подстрока для поиска, например 'ACA' для Air Canada.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT icao24, callsign, origin_country, velocity
                FROM aeroplanes
                WHERE callsign ILIKE %s;
                """,
                (f"%{keyword}%",),
            )
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def close(self) -> None:
        """Закрывает подключение к БД."""
        self.conn.close()
