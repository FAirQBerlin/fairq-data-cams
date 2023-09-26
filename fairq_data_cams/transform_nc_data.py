# This file contains functions to process the nc files downloaded from the new API (CAMS-EU).
# The resulting data frame is ready to be written to the database.

import re
from datetime import datetime

import netCDF4
import pandas as pd
import xarray as xr

from fairq_data_cams.transform_utils import check_for_duplicates, list_files_of_type

# Functions dealing with all files at once -----------------------------------------------------------------------------


def all_nc_files_to_one_df() -> pd.DataFrame:
    """
    Load all nc files from the nc folder, prepare the data and put them into one single data frame ready for the
    database (including duplicate check)
    :return: data frame with columns "date_time", "date_forecast", "lat", "lon", "no2", "pm25", and "pm10"
    """
    nc_file_paths = list_files_of_type("nc")
    df_list = [df_from_nc_file(path) for path in nc_file_paths]
    full_df = pd.concat(df_list).drop_duplicates()
    check_for_duplicates(full_df)
    return full_df


# Functions processing one file / one dataframe ------------------------------------------------------------------------


def df_from_nc_file(file_path: str) -> pd.DataFrame:
    """
    Wrapper around all functions to extract a df from one nc file
    :param file_path: path to nc file
    :return: data frame with columns "date_time", "date_forecast", "lat", "lon", "no2", "pm25", "pm10"
    """
    df = nc_file_to_df(file_path)
    df = add_date_columns(df, file_path)
    df = df.drop(columns=["time", "level"])
    df = df.rename(
        columns={"latitude": "lat", "longitude": "lon", "no2_conc": "no2", "pm10_conc": "pm10", "pm2p5_conc": "pm25"}
    )
    df = df.loc[:, ["date_time", "date_forecast", "lat", "lon", "no2", "pm25", "pm10"]]
    return df


def nc_file_to_df(file_path: str) -> pd.DataFrame:
    """
    Transform data from an nc file to a data frame

    :param file_path: path to nc file, e.g., "data/nc/ENS_FORECAST_2022-05-24.nc"
    :return: data frame with all columns from the nc file where all information is in the columns (and not in the row
    index anymore)
    """
    ds = xr.open_dataset(file_path)
    df = ds.to_dataframe()
    return df.reset_index()


def add_date_columns(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Add two date columns: when the forecast was made and for which day and hour. The latter is transformed from UTC into
    Berlin time
    :param df: data frame with a "time" column of type timedelta that contains the forecast horizon (usually between 0
    and 95 hours)
    :param file_path: path to the original nc file to extract the time when the forecast was made
    :return: data frame with additional columns "date_forecast" (date) and "date_time" (datetime)
    """
    nc = netCDF4.Dataset(file_path)
    date_info = nc.FORECAST
    match_str = re.search(r"\d{4}\d{2}\d{2}", date_info)
    assert match_str is not None  # To make mypy happy because we are sure that this will never be None
    date_forecast = datetime.strptime(match_str.group(), "%Y%m%d")
    df["date_forecast"] = date_forecast.date()
    df["date_time"] = date_forecast + df["time"]
    return df
