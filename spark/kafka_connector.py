import json
import psycopg2
import sys

if __name__ == "__main__":
    data = json.loads(sys.argv[1])

    conn = psycopg2.connect(
        host="postgres_db",
        database="cryptoproj",
        user="myuser",
        password="mypassword"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_prices (
            coin_name VARCHAR(100), 
            price DECIMAL(20, 10),
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    for coin_name, value in data.items():
        cursor.execute(
            "INSERT INTO coin_prices (coin_name, price) VALUES (%s, %s);", (coin_name, value))
        conn.commit()

    cursor.close()
    conn.close()
