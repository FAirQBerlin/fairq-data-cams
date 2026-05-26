# fairq-data-cams

This repo contains Python code to retrieve pollutant predictions from the API of the Copernicus Consortium and
store it in a Clickhouse database.


## How to get started

- Get an API key for the CAMS API (https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome)
- Create an .env file in the project folder, see `env_template` for the structure
- Create database as described in https://github.com/fairqBerlin/fairq-data/tree/main/inst/db (schema `fairq_raw`)


## Most important files

- `get_last_3_years.py`: Retrieves data from the CAMS EU API (see below) for newer dates (Beginning in May 2019) and writes it to a Clickhous DB

## Input and output

### Input

We use two APIs: CAMS-EU and CAMS-Global.
CAMS-EU provides a rolling window of the past three years.
For older dates, we have to use CAMS-Global, which has a lower resolution (temporal and spatial) and is slower.

APIs:
- CAMS-EU: https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=form
- CAMS-Global: https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-atmospheric-composition-forecasts?tab=form

Documentation:
- CAMS-EU: https://confluence.ecmwf.int/display/CKB/CAMS+Regional%3A+European+air+quality+analysis+and+forecast+data+documentation
- CAMS-Global: https://confluence.ecmwf.int/display/CKB/CAMS%3A+Global+atmospheric+composition+forecast+data+documentation

To process data from the CAMS-Global API, you need to install a system dependency:
```commandline
sudo apt install libeccodes-dev
```

### Output

- Database, schema `fairq_raw`


## Style checking

The Jenkins file of this repo contains rigorous style checking. You can run those checks in the console as well.
This sections lists the checks and tells how to fix problems.

### mypy static type enforcement
- Check: `mypy . --namespace-packages`
- Fix problems by fixing inconsistent typing

### Ruff Styleguide Enforcement & import errors
- Check: `uv run ruff check .`
- Fix the displayed problems manually in the files

### Ruff Formatting
- Check formatting : `uv run ruff format --check .`
- Autmatic formatting via `uv run ruff format .`
