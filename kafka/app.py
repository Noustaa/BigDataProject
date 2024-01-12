import json
from websockets.sync.client import connect
import subprocess
import json
import requests

BOOTSTRAP_SERVER = "localhost:9092"


def create_topic(topic_name):
    command = f"kafka-topics --create --topic {topic_name} --bootstrap-server {BOOTSTRAP_SERVER}"
    subprocess.run(command, shell=True)


def write_to_topic(topic_name, message):
    command = f"echo '{message}' | kafka-console-producer --topic {topic_name} --bootstrap-server {BOOTSTRAP_SERVER}"
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    create_topic("coin_prices")

    url = "https://api.coincap.io/v2/assets?limit=100"

    json_data = requests.get(url).text

    parsed_json = json.loads(json_data)
    coins = [item['id'] for item in parsed_json['data']]

    websocket_url = "wss://ws.coincap.io/prices?assets=" + ",".join(coins)

    with connect(websocket_url) as websocket:
        for message in websocket:
            data = json.loads(message)
            write_to_topic("coin_prices", json.dumps(data))
