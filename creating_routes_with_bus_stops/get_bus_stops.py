import pandas_gbq
import requests
import yaml
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


# Load the configuration from the YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract the settings
PROJECT_ID = config["project_id"]
DATASET_ID = config["dataset_id"]
JSON_KEY_PATH = config["json_key_path"]
API_KEY = config["api_key"]
RESOURCE_ID = config["resource_id"]

URL = f'https://api.um.warszawa.pl/api/action/dbstore_get/?id={RESOURCE_ID}&apikey={API_KEY}'

# Load the BigQuery credentials
CREDENTIALS = service_account.Credentials.from_service_account_file(
    JSON_KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
CLIENT = bigquery.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id)

bus_stop_info = requests.get(URL).json()['result']

bus_stops_list = []
for d in bus_stop_info:
    bus_stop = {}
    for item in d['values']:
        bus_stop[item['key']] = item['value']
    bus_stops_list.append(bus_stop)

enriched_bus_stops = []
for bus_stop in bus_stops_list:
    resource_id = '88cd555f-6f31-43ca-9de4-66c479ad5942'
    URL = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/?id={RESOURCE_ID}&busstopId={bus_stop["zespol"]}' \
          f'&busstopNr={bus_stop["slupek"]}&apikey={API_KEY}'
    stop = requests.get(URL).json()['result']

    for d in stop:
        for item in d['values']:
            r = bus_stop.copy()
            r['line'] = item['value']
            enriched_bus_stops.append(r)

    bus_stops_df = pd.DataFrame(enriched_bus_stops)

    # Adjust table name
    pandas_gbq.to_gbq(bus_stops_df, f'{DATASET_ID}.BUS_STOPS_WITH_LINES_INFO', project_id=f'{PROJECT_ID}',
                          if_exists='append', credentials=CREDENTIALS)

    print(f'Bus stops detailed info saved!')

