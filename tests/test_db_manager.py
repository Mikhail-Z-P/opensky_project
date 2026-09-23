def test_insert_country_and_count(db_manager):
    """Проверяет вставку страны и подсчёт через get_countries_and_aeroplanes_count."""
    db_manager.insert_country("TestCountry", 10.0, 20.0)
    result = db_manager.get_countries_and_aeroplanes_count()
    assert any(item["name"] == "TestCountry" for item in result)


def test_avg_speed_empty(db_manager):
    """В пустой БД средняя скорость — None."""
    avg = db_manager.get_avg_speed()
    assert avg is None


def test_insert_and_higher_speed(db_manager):
    """Проверяет вставку самолётов и фильтр выше средней скорости."""
    country_id = db_manager.insert_country("TestCountry", 0.0, 0.0)
    with db_manager.conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO aeroplanes (icao24, velocity, country_id)
            VALUES (%s, %s, %s), (%s, %s, %s);
            """,
            ("A1", 100.0, country_id, "A2", 200.0, country_id),
        )
    db_manager.conn.commit()

    avg = db_manager.get_avg_speed()
    assert avg == 150.0

    higher = db_manager.get_aeroplanes_with_higher_speed()
    assert len(higher) == 1
    assert higher[0]["velocity"] == 200.0


def test_keyword_search(db_manager):
    """Проверяет поиск по позывному."""
    country_id = db_manager.insert_country("TestCountry", 0.0, 0.0)
    with db_manager.conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO aeroplanes (icao24, callsign, country_id)
            VALUES (%s, %s, %s), (%s, %s, %s);
            """,
            ("A1", "ACA123", country_id, "A2", "XYZ789", country_id),
        )
    db_manager.conn.commit()

    results = db_manager.get_aeroplanes_with_keyword("ACA")
    assert len(results) == 1
    assert results[0]["callsign"] == "ACA123"
