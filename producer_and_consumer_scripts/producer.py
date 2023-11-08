import json
import requests
import time
import yaml
from datetime import datetime

from confluent_kafka import Producer

# Load the configuration from the YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract the settings
API_KEY = config["api_key"]
RESOURCE_ID = config["resource_id"]
YOUR_BUSES_TOPIC = config["buses_topic"]
YOUR_TRAMS_TOPIC = config["trams_topic"]

TRAMS_URL = f"https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id={RESOURCE_ID}&apikey={API_KEY}&type=2"
BUSES_URL = f"https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id={RESOURCE_ID}&apikey={API_KEY}&type=1"

producer = Producer(
    {
        'bootstrap.servers': 'localhost:9092'
    }
)


def produce_data():
    """
    Retrieve data from bus and tram APIs and send it to Kafka topics.

    Returns:
        None
    """
    try:
        # Retrieve bus and tram information
        bus_info = requests.get(BUSES_URL).json()['result']
        tram_info = requests.get(TRAMS_URL).json()['result']

        # Send bus and tram information to Kafka topics
        producer.produce(YOUR_BUSES_TOPIC, json.dumps(bus_info))
        producer.produce(YOUR_TRAMS_TOPIC, json.dumps(tram_info))

        print(f'Produced data at {datetime.now()}')

    except Exception as e:
        print(f'Error occurred: {e}')


if __name__ == '__main__':
    while True:
        # Produce data and sleep
        produce_data()
        time.sleep(15)  # Adjust time in seconds
