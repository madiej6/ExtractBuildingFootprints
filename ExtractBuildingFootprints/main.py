import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from joblib import Parallel, delayed
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
import duckdb

def create_db():

    # create a database file
    spatial="LOAD spatial;"
    if os.path.exists('buildings.db'):
        spatial="INSTALL spatial;" + spatial

    con = duckdb.connect('buildings.db') 
    con.execute(spatial)

    return con

def check_tmp_dir():
    total, used, free = shutil.disk_usage("/tmp") 
    print("Total: %d GB" % (total // (2**30)))
    print("Used: %d GB" % (used // (2**30)))
    print("Free: %d GB" % (free // (2**30)))

def download_single_state(state: str):

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

        # check remaining availability of temp dir
        check_tmp_dir()

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

def main():

    # set up some multiprocessing vars
    num_cpus = mp.cpu_count()
    in_use_cpus = int(np.floor(num_cpus*0.7))

    states_df = pd.read_csv("states.tsv", sep='\t')
    states = states_df['State'].to_list()
    states=['District of Columbia', 'Delaware', 'Rhode Island', 'Connecticut', 'Maryland']

    results = Parallel(n_jobs=2)(delayed(download_single_state)(state) for state in states[0:5])
    # # Create a pool of processes based on the number of CPUs
    # with ThreadPool(in_use_cpus) as pool:
    #     # Run the process_item function on each item in the list
    #     results = pool.map(download_single_state, states[0:5])


    # query the table
    result = con.execute(f"SELECT COUNT(*) as count_bldgs FROM {state}").fetchdf()



if __name__ == "__main__":
    main()
