import os
import requests
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL")

API_URL = "https://danepubliczne.imgw.pl/api/data/synop"
REFERENCE_PRESSURE = 1013.25


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "Brak zmiennej środowiskowej DATABASE_URL. "
            "Ustaw ją lokalnie w PowerShell: "
            '$env:DATABASE_URL="Connection string do bazy danych PostgreSQL"'
        )

    return psycopg.connect(DATABASE_URL)


def fetch_imgw_data():
    response = requests.get(API_URL, timeout=20)
    response.raise_for_status()
    return response.json()


def create_table_if_not_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS POGODA_MIASTA (
            id SERIAL PRIMARY KEY,
            miasto VARCHAR(100),
            data_pomiaru VARCHAR(20),
            godzina_pomiaru VARCHAR(10),
            temperatura FLOAT,
            predkosc_wiatru FLOAT,
            wilgotnosc_wzgledna FLOAT,
            suma_opadu FLOAT,
            cisnienie FLOAT,
            roznica_cisnienia FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


def to_float(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_data(cursor, data):
    insert_query = """
        INSERT INTO POGODA_MIASTA (
            miasto,
            data_pomiaru,
            godzina_pomiaru,
            temperatura,
            predkosc_wiatru,
            wilgotnosc_wzgledna,
            suma_opadu,
            cisnienie,
            roznica_cisnienia
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    inserted_count = 0

    for item in data:
        city = item.get("stacja", "")

        if city.startswith("L") or city.startswith("K"):
            pressure = to_float(item.get("cisnienie"))

            pressure_difference = None
            if pressure is not None:
                pressure_difference = round(pressure - REFERENCE_PRESSURE, 2)

            cursor.execute(insert_query, (
                city,
                item.get("data_pomiaru"),
                item.get("godzina_pomiaru"),
                to_float(item.get("temperatura")),
                to_float(item.get("predkosc_wiatru")),
                to_float(item.get("wilgotnosc_wzgledna")),
                to_float(item.get("suma_opadu")),
                pressure,
                pressure_difference
            ))

            inserted_count += 1

    return inserted_count


def main():
    data = fetch_imgw_data()

    conn = get_connection()
    cursor = conn.cursor()

    create_table_if_not_exists(cursor)
    inserted_count = load_data(cursor, data)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"ETL completed. Inserted rows: {inserted_count}")


if __name__ == "__main__":
    main()
