from flask import Flask, jsonify
from flask_cors import CORS
import psycopg
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "Brak zmiennej środowiskowej DATABASE_URL. "
            "Ustaw ją lokalnie w PowerShell: "
            '$env:DATABASE_URL="Connection string do bazy danych PostgreSQL"'
        )

    return psycopg.connect(DATABASE_URL)


@app.route("/")
def home():
    return {
        "status": "running",
        "service": "IMGW ETL API"
    }


@app.route("/weather")
def weather():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            miasto,
            temperatura,
            cisnienie,
            roznica_cisnienia,
            wilgotnosc_wzgledna,
            predkosc_wiatru,
            suma_opadu,
            data_pomiaru,
            godzina_pomiaru,
            created_at
        FROM POGODA_MIASTA
        ORDER BY created_at DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "miasto": row[0],
            "temperatura": row[1],
            "cisnienie": row[2],
            "roznica_cisnienia": row[3],
            "wilgotnosc_wzgledna": row[4],
            "predkosc_wiatru": row[5],
            "suma_opadu": row[6],
            "data_pomiaru": row[7],
            "godzina_pomiaru": row[8],
            "created_at": str(row[9])
        })

    cursor.close()
    conn.close()

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
