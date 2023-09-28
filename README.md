# fairq-data-cams

This repo contains Python code to retrieve pollutant predictions from the API of the Copernicus Consortium and
store it in a Clickhouse database.


## How to get started

- Get an API key for the CAMS API (https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome)
- Create an .env file in the project folder, see `env_template` for the structure
- Create database as described in https://github.com/fairqBerlin/fairq-data/tree/main/inst/db (schema `fairq_raw`)


## Most important files

- `main_old_api.py`: Retrieves data from the CAMS global API (see below) for older dates and writes it to a Clickhous DB
- `main_new_api.py`: Retrieves data from the CAMS EU API (see below) for newer dates and writes it to a Clickhous DB


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

### Flake8 Styleguide Enforcement
- Check: `flake8 .`
- Fix the displayed problems manually in the files

### Black Styleguide Enforcement
- Check: `black --line-length 120 --check .`
- Fix problems using the black auto formatter:
  - Installation: File -> Settings -> Tools -> External Tools -> "+" -> add "Black"
    - Program: `~/.local/share/virtualenvs/fairq-data-cams-xxxx/bin/black` (adjust for your VE path)
    - Arguments: `$FilePath$ --line-length 120`
    - Working directory: `$ProjectFileDir$`
  - Add a shortkey to run the auto formatter, e.g., CTRL+SHIFT+A

### isort: order of import statements
- Fix problems via `isort .`

### Example workflow:
1. Always use Black CTRL+SHIFT+A to fix formatting errors
2. use `isort .` to fix import errors
3. use `flake8 .` and fix missing docstrings, trailing commas and other small things
4. use `flake8 .` and fix remaining complexity errors.
5. In case flake 8 is really wrong (mostly it is not) you can whitelist an error by adding `# noqa: WPS123` to the line
