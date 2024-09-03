import glob
import os
import json
# import geopandas as gpd
# from shapely import geometry
import pandas as pd
# from fiona.crs import from_epsg
import constants
import duckdb



def main():

    states_df = pd.read_csv("states.tsv", sep='\t')

    # os.chdir(jsonfolder)

    list_json = glob.glob("*json")

    for statejson in list_json:
        cur_json = os.path.join(jsonfolder, statejson)
        state = os.path.basename(cur_json.split(".")[0])
        print(state)
        final_output = os.path.join(shpfolder, state+".shp")

        with open(cur_json) as json_file:
            data = json.load(json_file)
        num_feats = len(data['features'])
        print("number of features: ", num_feats)

        newdata = gpd.GeoDataFrame()
        newdata['geometry'] = None
        newdata['release'] = None
        newdata['capture_dates_range'] = None

        newdata['release'] = pd.to_numeric(newdata['release'])

        i = 0
        X = 0

        for feat in data['features']:
            coords = feat['geometry']['coordinates']
            release = feat['properties']['release']
            capture_dates_range = feat['properties']['capture_dates_range']

            if len(coords) == 1:
                geom = []
                for coord in coords[0]:
                    p = geometry.Point(coord[0],coord[1])
                    geom.append(p)

                poly = geometry.Polygon(geom)
            else:
                print("length of coords is greater than 1")
                X += 1
                continue

            newdata.loc[i, 'geometry'] = poly
            newdata.loc[i, 'release'] = release
            newdata.loc[i, 'capture_dates_range'] = capture_dates_range


            i += 1

        print("{} errors.".format(X))

        newdata.crs = from_epsg(4326)
        newdata.to_file(final_output)
    return


if __name__ == "__main__":
    main()
