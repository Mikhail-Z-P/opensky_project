import os

import psycopg2
import pytest
from dotenv import load_dotenv

from src.db_manager import DBManager

load_dotenv()


@pytest.fixture(scope="function")
def db_manager():
    """Создаёт временную тестовую БД, возвращает DBManager, удаляет БД после теста."""
    test_db = "aeroplanes_db_test"

    # Подключаемся к серверу
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname="postgres",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        client_encoding="UTF8",
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {test_db};")
        cur.execute(f"CREATE DATABASE {test_db};")
    conn.close()

    # Подменяем имя БД для теста
    os.environ["DB_NAME"] = test_db
    db = DBManager()
    db.create_tables()
    yield db

    # Очистка
    db.close()
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname="postgres",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {test_db};")
    conn.close()
