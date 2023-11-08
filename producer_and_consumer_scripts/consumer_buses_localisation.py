import json
from datetime import datetime, timedelta
import math
import yaml
import pandas as pd
from shapely.geometry import Point, LineString
from confluent_kafka import Consumer
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account


# Load the configuration from the YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract the settings
PROJECT_ID = config["project_id"]
DATASET_ID = config["dataset_id"]
BUS_CORDS_TABLE = config["bus_cords_table"]
TRAM_CORDS_TABLE = config["tram_cords_table"]
JSON_KEY_PATH = config["json_key_path"]
KAFKA_CONFIG = config["kafka_config"]
YOUR_BUSES_TOPIC = config["trams_topic"]

# Load the BigQuery credentials
CREDENTIALS = service_account.Credentials.from_service_account_file(
    JSON_KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
CLIENT = bigquery.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id)

# Create a Kafka consumer with the specified configuration
consumer = Consumer(KAFKA_CONFIG)
consumer.subscribe([YOUR_BUSES_TOPIC])


def create_transport_localisation(row):
    """
    Create a transport localization shape based on the input row's coordinates.

    Args:
        row (pandas.Series): A pandas Series containing latitude (Lat) and longitude (Lon) coordinates.

    Returns:
        str: A Well-Known Text (WKT) representation of the transport localization shape.

    This function scales and rotates a transport shape centered at the provided latitude and longitude coordinates
    (Lat and Lon). It returns a WKT representation of the transformed shape.
    """
    scale_factor = 100
    rotation_angle = math.radians(270)

    transport_vertices = [
        # Define the vertices of the scaled and rotated bus shape
        (row['Lon'] + 0.00003 * scale_factor, row['Lat'] - 0.00001 * scale_factor),  # Rear left corner
        (row['Lon'] + 0.00003 * scale_factor, row['Lat'] - 0.0000075 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] - 0.0000075 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] + 0.0000075 * scale_factor),
        (row['Lon'] + 0.00003 * scale_factor, row['Lat'] + 0.0000075 * scale_factor),
        (row['Lon'] + 0.00003 * scale_factor, row['Lat'] + 0.00001 * scale_factor),  # Rear right corner
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] + 0.00001 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] + 0.000015 * scale_factor),
        (row['Lon'] + 0.000015 * scale_factor, row['Lat'] + 0.000015 * scale_factor),
        (row['Lon'] + 0.000015 * scale_factor, row['Lat'] + 0.00001 * scale_factor),
        (row['Lon'] + 0.00001 * scale_factor, row['Lat'] + 0.00001 * scale_factor),
        (row['Lon'] + 0.00001 * scale_factor, row['Lat'] - 0.00001 * scale_factor),
        (row['Lon'] + 0.000015 * scale_factor, row['Lat'] - 0.00001 * scale_factor),
        (row['Lon'] + 0.000015 * scale_factor, row['Lat'] - 0.000015 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] - 0.000015 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] - 0.00001 * scale_factor),
        (row['Lon'] + 0.00001 * scale_factor, row['Lat'] - 0.00001 * scale_factor),
        (row['Lon'] + 0.00001 * scale_factor, row['Lat'] - 0.0000075 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] - 0.0000075 * scale_factor),
        (row['Lon'] + 0.00002 * scale_factor, row['Lat'] - 0.00001 * scale_factor),
        (row['Lon'] + 0.00003 * scale_factor, row['Lat'] - 0.00001 * scale_factor)  # Close the shape
    ]

    rotated_car_vertices = [
        (
            (x - row['Lon']) * math.cos(rotation_angle) - (y - row['Lat']) * math.sin(rotation_angle) + row['Lon'],
            (x - row['Lon']) * math.sin(rotation_angle) + (y - row['Lat']) * math.cos(rotation_angle) + row['Lat']
        )
        for x, y in transport_vertices
    ]

    transport_shape = LineString(rotated_car_vertices)
    return transport_shape.wkt


def process_and_store_data():
    """
    Process GPS data from a Kafka topic, filter, transform, and store it in a BigQuery table.

    This function polls for messages from a Kafka topic containing GPS data. It processes the data by
    converting the 'Time' column to datetime, filtering data for the last 60 seconds, creating transport
    localization shapes, and storing the processed data in a BigQuery table.

    Returns:
        None

    This function performs the following steps:
    1. Poll for new messages from the Kafka topic.
    2. Skip processing if no messages are received or if the message value is equal to 'no_signal.'
    3. Parse the message value as JSON.
    4. Create a pandas DataFrame from the JSON data.
    5. Convert the 'Time' column to datetime format.
    6. Filter the data for the last 5 minutes.
    7. Remove rows with missing longitude (Lon) or latitude (Lat) coordinates.
    8. Create a new column 'LineString' with rotated transport shapes centered at each GPS point.
    9. Prepare and structure the data for BigQuery storage.
    10. Store the data in a BigQuery table.
    """
    try:
        msg = consumer.poll(30)

        # In case of no signal in kafka message from API UM Warsaw
        no_signal = b'"B\\u0142\\u0119dna metoda lub parametry wywo\\u0142ania"'
        if msg is None or msg.value() == no_signal:
            pass

        row = json.loads(msg.value().decode("utf-8"))
        print(f'Captured data: {datetime.now()}')

        df = pd.DataFrame(row)
        df['Time'] = pd.to_datetime(df['Time'])  # Convert 'Time' column to datetime

        # Filter data for the localisation from last 60 seconds
        df = df[df['Time'] >= (datetime.now() - timedelta(minutes=1))]

        df.dropna(subset=['Lon', 'Lat'], inplace=True)  # Drop rows with missing coordinates

        # Create a new column 'LineString' with rotated car shapes centered at each GPS point
        df['LineString'] = df.apply(create_transport_localisation, axis=1)

        df['Route'] = df['Lines']
        df['Info'] = 'Trasa: ' + df['Lines'] + ', o godzinie: ' + df['Time'].astype(str)

        df = df[['Route', 'LineString', 'Info']]

        # Store data in BigQuery table
        pandas_gbq.to_gbq(df, f'{DATASET_ID}.{BUS_CORDS_TABLE}', project_id=f'{PROJECT_ID}', if_exists='replace',
                          credentials=CREDENTIALS)

        print(f'Message with trams coordinates saved to BigQuery table. On time: {datetime.now()}')

    except Exception as e:
        print(f'Error occurred: {e}')


if __name__ == '__main__':
    while True:
        # Consume data
        process_and_store_data()
