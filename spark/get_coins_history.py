import json
import psycopg2
import requests

if __name__ == "__main__":
    url = "https://api.coincap.io/v2/assets?limit=100"

    json_data = requests.get(url).text

    parsed_json = json.loads(json_data)
    coins = [item['id'] for item in parsed_json['data']]

    conn = psycopg2.connect(
        host="postgres_db",
        database="cryptoproj",
        user="myuser",
        password="mypassword"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'coin_prices'
        );
    """)
    table_exists = cursor.fetchone()[0]

    if table_exists:
        print("History has already been fetched. Not running again.")
        cursor.close()
        conn.close()
        exit(0)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_prices (
                coin_name VARCHAR(100), 
                price DECIMAL(20, 10),
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()

    for coin_name in coins:
        url = f"https://api.coincap.io/v2/assets/{coin_name}/history?interval=d1&start=1673475603000&end=1705010689000"
        json_data = requests.get(url).text
        parsed_json = json.loads(json_data)
        data = parsed_json['data']
        if len(data) == 0:
            continue
        for item in data:
            value = item['priceUsd']
            time = item['time']
            cursor.execute(
                "INSERT INTO coin_prices (coin_name, price, time) VALUES (%s, %s, TO_TIMESTAMP(%s / 1000.0));", (coin_name, value, time))
        print("Last 6 months of data for " + coin_name + " inserted.")
        conn.commit()

    cursor.close()
    conn.close()
