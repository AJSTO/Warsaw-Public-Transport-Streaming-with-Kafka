import pandas as pd
import requests
import warnings
from google.cloud import bigquery
from google.oauth2 import service_account
from shapely.geometry import LineString
import pandas_gbq
import yaml


# Load the configuration from the YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract the settings
PROJECT_ID = config["project_id"]
DATASET_ID = config["dataset_id"]
JSON_KEY_PATH = config["json_key_path"]
API_KEY = config["api_key"]
RESOURCE_ID = config["resource_id"]
CREDENTIALS = service_account.Credentials.from_service_account_file(
    JSON_KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
CLIENT = bigquery.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id)


def get_bus_stop_info(api_key: str, resource_id: str) -> pd.DataFrame:
    """
    Retrieve bus stop information from an API and return a pandas DataFrame.

    Args:
        api_key (str): API key for the Warsaw public transport system.
        resource_id (str): Resource ID for the API endpoint.

    Returns:
        pd.DataFrame: DataFrame containing bus stop information.
    """
    url = f'https://api.um.warszawa.pl/api/action/dbstore_get/?id={resource_id}&apikey={api_key}'
    bus_stop_info = requests.get(url).json()['result']
    rows = []
    for d in bus_stop_info:
        row = {}
        for item in d['values']:
            row[item['key']] = item['value']
        rows.append(row)

    url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/?id={resource_id}&busstopId={{}}&busstopNr={{}}&apikey={api_key}'
    bus_stops_lines = []
    for row in rows:
        stop = requests.get(url.format(row["zespol"], row["slupek"])).json()['result']
        error_msg = 'Błędna metoda lub parametry wywołania'
        if stop == error_msg:
            continue
        for d in stop:
            for item in d['values']:
                r = row.copy()
                r['line'] = item['value']
                bus_stops_lines.append(r)

    df = pd.DataFrame(bus_stops_lines)

    return df


def fetch_public_transport_routes(url: str) -> pd.DataFrame:
    """
    Fetches data from the given API endpoint and returns a pandas DataFrame containing public transport routes.

    Args:
        url (str): The API endpoint to fetch data from.

    Returns:
        pd.DataFrame: A DataFrame containing public transport routes.
    """

    bus_stop_info = requests.get(url).json()['result']

    df = pd.DataFrame(
        columns=['linia_nazwa_trasy', 'odleglosc', 'ulica_id', 'nr_zespolu', 'typ', 'nr_przystanku', 'num_porzadkowy'])

    for line_num, r_d in bus_stop_info.items():
        for route_name, details in r_d.items():
            for k, v in details.items():
                line_and_route_df = pd.DataFrame(v, index=[0])
                line_and_route_df['linia_nazwa_trasy'] = f'{line_num};{route_name}'
                line_and_route_df['num_porzadkowy'] = k
                df = pd.concat([df, line_and_route_df])

    return df


def create_and_upload_routes_linestring_to_bigquery(api_key: str, resource_id: str, url: str):
    """
    Fetches public transport routes data from an API and bus stop information from a database, merges the dataframes,
    and generates linestrings for each unique route before uploading the results to a BigQuery table.

    Args:
        api_key (str): The API key for accessing the database and API.
        resource_id (str): The ID of the resource to fetch from the database.
        url (str): The URL of the API to fetch the public transport routes data from.

    Returns:
        None
    """
    # Suppress the warning
    warnings.filterwarnings("ignore", message="^.*Returning a view.*$")
    bus_stops_df = get_bus_stop_info(api_key, resource_id)
    routes_df = fetch_public_transport_routes(url)
    routes_df = routes_df.rename(columns={'nr_zespolu': 'zespol', 'nr_przystanku': 'slupek'})
    routes_df['slupek'] = routes_df['slupek'].str.pad(width=2, fillchar='0')
    route_with_coords_df = pd.merge(routes_df, bus_stops_df, on=['zespol', 'slupek'], how='left')
    route_with_coords_df = route_with_coords_df.drop(['Unnamed: 0'], axis=1)
    unique_bus_routes_id = route_with_coords_df['linia_nazwa_trasy'].unique()
    routes_linestring = pd.DataFrame(columns=['route', 'linestring'])
    for unique_route in unique_bus_routes_id:
        # Filter the DataFrame to include only the rows with route 'A'
        filtered_df = route_with_coords_df.copy()[route_with_coords_df['linia_nazwa_trasy'] == unique_route]
        # Sort by num_porzadkowy
        filtered_df['num_porzadkowy'] = filtered_df['num_porzadkowy'].astype(int)
        filtered_df = filtered_df.sort_values('num_porzadkowy')
        filtered_df.dropna(subset=['szer_geo', 'dlug_geo'], inplace=True)
        # Concatenate the values in the 'szer_geo' and 'dlug_geo' columns
        result_list = [f"{dlug_geo} {szer_geo}" for szer_geo, dlug_geo in
                       zip(filtered_df['szer_geo'], filtered_df['dlug_geo'])]
        linestring = f"LINESTRING({', '.join(result_list)})"
        row_to_add = pd.DataFrame([
            [unique_route, linestring]
        ], columns=['route', 'linestring'])
        routes_linestring = pd.concat([routes_linestring, row_to_add], ignore_index=True)
    routes_linestring = routes_linestring[routes_linestring['linestring'].str.len() >= 50]

    # Adjust table id
    pandas_gbq.to_gbq(routes_linestring, f'{DATASET_ID}.ROUTES_TABLE', project_id=f'{PROJECT_ID}',
                      if_exists='append', credentials=CREDENTIALS)


if __name__ == '__main__':
    """
    Entry point of the script. Calls the function `create_and_upload_routes_linestring_to_bigquery()` to fetch public 
    transport routes data and bus stop information, process it, and upload the resulting data to a BigQuery table.
    """
    create_and_upload_routes_linestring_to_bigquery(
        API_KEY,
        RESOURCE_ID,
        f'https://api.um.warszawa.pl/api/action/public_transport_routes/?apikey={API_KEY}'
    )
