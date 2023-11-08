To get bus stops coordinates run:
```bash
$ python get_bus_stops.py
```

If you want to create a linestring in shape e.g. square of bus-stop you can:
```bash
import pandas as pd
from shapely.geometry import LineString
from confluent_kafka import Consumer
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
# BigQuery configuration settings
PROJECT_ID = 'YOUR-PROJECT-ID'
DATASET_ID = 'YOUR-DATASET-ID'
BUS_CORDS_TABLE = 'BUS-CORDS-TABLE-ID'
BUS_CORDS_WITH_SHAPE = 'BUS-CORDS-WITH-SHAPE-TABLE-ID'
JSON_KEY_PATH = './credentials.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(
    JSON_KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
CLIENT = bigquery.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id, )

# Get bus stops coordinates
query = f"""
SELECT 
    * 
FROM 
`{PROJECT_ID}.{DATASET_ID}.{BUS_CORDS_TABLE}` 
;
    """
selected_rows = CLIENT.query(query)
bus_cords_df = selected_rows.to_dataframe()[['zespol', 'slupek', 'szer_geo', 'dlug_geo']].drop_duplicates()

def create_square(lat, lon, size=0.001):
    half_size = size / 1.5
    return LineString([(lon - half_size, lat - half_size),
                      (lon + half_size, lat - half_size),
                      (lon + half_size, lat + half_size),
                      (lon - half_size, lat + half_size),
                      (lon - half_size, lat - half_size)])

def create_diamond(lat, lon):
    return LineString([(lon, lat), (lon + 0.005, lat + 0.01), (lon + 0.01, lat), (lon + 0.005, lat - 0.01), (lon, lat)])

# Apply the function to create the LineString shapes and add an 'info' column
df['route'] = df.line
df['linestring'] = df.apply(lambda row: create_square(row['szer_geo'], row['dlug_geo']), axis=1)
df['info'] = 'Przystanek: ' + df['nazwa_zespolu'] + ' ' + df['slupek'].astype(str)
df = df[['route', 'linestring', 'info']]

pandas_gbq.to_gbq(df, f'{DATASET_ID}.{BUS_CORDS_WITH_SHAPE}', project_id=f'{PROJECT_ID}',
                          if_exists='replace', credentials=CREDENTIALS)
```

To create public transport routes:
```bash
$ python create_routes.py
```