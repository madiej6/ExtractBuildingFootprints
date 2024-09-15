# ExtractBuildingFootprints

This program downloads and extracts Microsoft building footprints their source in [github](https://github.com/Microsoft/USBuildingFootprints) to a local DuckDB database using open source Python libraries.

Given a state, this program does the following:
1. Download & extract the building footprints for the given state and load them to a DuckDB database named `buildings.db`
2. Print the number of buildings that exist for the state.

The database `buildings.db` will remain persistent in the working directory of the repo, so you can  run queries on the database and tables (see below):

## Instructions:

Install Python requirements.txt

```
pip install -r requirements.txt
```

Run the program, providing the state as an argument. If no state is provided, the program will default to 'District of Columbia'.

```
python ExtractBuildingFootprints/main.py --state=Maryland
```

Then, query away on the buildings!


```
$ duckdb buildings.db
```

```
D SELECT COUNT(*) AS bldg_count FROM DistrictofColumbia;
┌────────────┐
│ bldg_count │
│   int64    │
├────────────┤
│      77851 │
└────────────┘
```

```
D SELECT * FROM DistrictofColumbia LIMIT 5;
┌─────────┬───────────────┬─────────┬─────────────────────┬──────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│  type   │ geometry_type │ release │ capture_dates_range │       geom_wkt       │                                 geometry                                 │
│ varchar │    varchar    │  int64  │       varchar       │       varchar        │                                 geometry                                 │
├─────────┼───────────────┼─────────┼─────────────────────┼──────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Feature │ Polygon       │       2 │ 9/22/2020-9/23/2020 │ POLYGON ((-76.9049…  │ \x02\x04\x00\x00\x00\x00\x00\x00Z\xCF\x99\xC2c\x94\x1BB@\xCF\x99\xC2\x…  │
│ Feature │ Polygon       │       2 │ 9/22/2020-9/23/2020 │ POLYGON ((-76.9060…  │ \x02\x04\x00\x00\x00\x00\x00\x00\xFF\xCF\x99\xC2\x87\x94\x1BB\xDF\xCF\…  │
│ Feature │ Polygon       │       2 │ 9/22/2020-9/23/2020 │ POLYGON ((-76.9063…  │ \x02\x04\x00\x00\x00\x00\x00\x00\x16\xD0\x99\xC2\x9B\x90\x1BB\x05\xD0\…  │
│ Feature │ Polygon       │       2 │ 9/22/2020-9/23/2020 │ POLYGON ((-76.9068…  │ \x02\x04\x00\x00\x00\x00\x00\x00Z\xD0\x99\xC2\x1C\x8E\x1BBH\xD0\x99\xC…  │
│ Feature │ Polygon       │       2 │ 9/22/2020-9/23/2020 │ POLYGON ((-76.9068…  │ \x02\x04\x00\x00\x00\x00\x00\x00_\xD0\x99\xC2,\x92\x1BBH\xD0\x99\xC2O\…  │
└─────────┴───────────────┴─────────┴─────────────────────┴──────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```