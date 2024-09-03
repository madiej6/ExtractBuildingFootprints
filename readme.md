# ExtractBuildingFootprints

Download Microsoft building footprints their source in [github](https://github.com/Microsoft/USBuildingFootprints) to a DuckDB database using open source Python libraries.

## Instructions:

1. Download and unzip nationwide geojson files from [github](https://github.com/Microsoft/USBuildingFootprints).

2. Update `config.py` to contain proper file paths to geojson files and output shapefiles.

3. Create new conda environment with Python 3 and install requirements.txt

4. From new conda environment, cd into repo root folder and run `json_to_shp_conversion.py`
