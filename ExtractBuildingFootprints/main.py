from multiprocessing.pool import Pool
import os
import json
from shapely import Point, Polygon
import pandas as pd
from typing import List
from constants import URL_TEMPLATE
import numpy as np
import shutil
import zipfile
import tempfile
import requests
import argparse
import duckdb

def create_db():
    """Create local DuckDB database named 'buildings.db' and enable spatial extension."""
    spatial = None

    # create a database file
    if not os.path.exists('buildings.db'):
        spatial="INSTALL spatial; LOAD spatial;"

    con = duckdb.connect('buildings.db') 

    # if database is new, enable duckdb spatial extension
    if spatial:
        con.execute(spatial)

    return con

def download_single_state(state: str):
    """Extract buildings to DuckDB table."""

    print(f'Running: {state}')

    # remove spaces
    state=state.replace(' ', '')

    # set up db connection
    con = create_db()

    # get the state's download url
    download_url = URL_TEMPLATE.format(state)

    # create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        # download the ZIP file
        response = requests.get(download_url)
        
        # path to save the downloaded ZIP file
        zip_path = os.path.join(temp_dir, f"{state}.zip")
        
        # save the downloaded ZIP file
        with open(zip_path, 'wb') as zip_file:
            zip_file.write(response.content)
        
        # extract the ZIP file into the temporary directory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # list the extracted files
        extracted_files = os.listdir(temp_dir)
        print("Extracted files:", extracted_files)


        # Load JSON data into a Python object
        with open(os.path.join(temp_dir, f"{state}.geojson")) as json_file:
            data = json.load(json_file)
        
        # load the data into a dataframe
        df = pd.json_normalize(data['features'])

        # transform the data
        df = transform(df)

        # insert the DataFrame into a DuckDB table
        con.execute(f"CREATE TABLE IF NOT EXISTS {state} AS SELECT *, ST_GeomFromText(geom_wkt) AS geometry FROM df")

        # kill the directory and it's contents
        shutil.rmtree(temp_dir)
        
        
def transform(df: pd.DataFrame):
    """Perform some basic transformations on the DataFrame.
    
    Args:
        df (pd.DataFrame): dataframe containing entire set of data for single state
    """
    df['release'] = pd.to_numeric(df['properties.release'])
    df['geom_wkt'] = df['geometry.coordinates'].apply(convert_geom)

    df.rename(columns={'properties.capture_dates_range':'capture_dates_range', 'geometry.type':'geometry_type'}, inplace=True)
    # only save some columns
    df = df[['type', 'geometry_type', 'release', 'capture_dates_range', 'geom_wkt']]

    return df


def convert_geom(coords: List):
    """Convert list of coordinates to WKT geometry.
    
    Args:
    """

    if len(coords) == 1:
        geom = []
        for coord in coords[0]:
            p = Point(coord[0],coord[1])
            geom.append(p)

        poly = Polygon(geom).wkt
        return poly
    else:
        print("length of coords is greater than 1")
        num_errors += 1
        return None

def main(state: str):

    states_df = pd.read_csv("states.tsv", sep='\t')
    states = states_df['State'].to_list()

    download_single_state(state=state)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--state', 
                        dest='state',
                        default='District of Columbia',
                        help='State to extract buildings for.')
    
    args = parser.parse_args()
    state = args.state
    main(state)
