# This file contains functions to process the nc files downloaded from the old API (CAMS-Global).
# The resulting data frame is ready to be written to the database.

import numpy as np
import pandas as pd
import xarray as xr

# Functions dealing with all files at once -----------------------------------------------------------------------------
from fairq_data_cams.transform_utils import check_for_duplicates, list_files_of_type


def all_grib_files_to_one_df() -> pd.DataFrame:
    """
    Load all grib files from the grib folder, prepare the data and put them into one single data frame ready for the
    database (including duplicate check)
    :return: data frame with columns "date_time", "date_forecast", "lat", "lon", "no2", "pm25", and "pm10"
    """
    grib_file_paths = list_files_of_type("grib")
    df_list = [df_from_grib_file(path) for path in grib_file_paths]
    full_df = pd.concat(df_list).drop_duplicates()
    full_df = full_df.replace(to_replace=np.nan, value=None)
    check_for_duplicates(full_df)
    return full_df


# Functions processing one file / one dataframe ------------------------------------------------------------------------


def df_from_grib_file(file_path: str) -> pd.DataFrame:
    """
    Load grib file and put data into a data frame.
    File needs to be loaded twice in different ways: once for particulate matter and once for NO2.
    :param file_path: path to grib file
    :return: data frame with columns "date_time", "date_forecast", "lat", "lon", "no2", "pm25", and "pm10"
    """
    grib_file_pm = load_grib_file(file_path, "surface")
    df_pm = (
        grib_file_pm.to_dataframe()
        .reset_index()
        .loc[:, ["valid_time", "time", "latitude", "longitude", "pm2p5", "pm10"]]
    )
    grib_file_no2 = load_grib_file(file_path, "hybrid")
    df_no2 = grib_file_no2.to_dataframe().reset_index().loc[:, ["valid_time", "time", "latitude", "longitude", "no2"]]

    df = df_pm.merge(df_no2, on=["latitude", "longitude", "time", "valid_time"], how="outer")
    df = df.rename(
        columns={
            "time": "date_forecast",
            "latitude": "lat",
            "longitude": "lon",
            "valid_time": "date_time",
            "pm2p5": "pm25",
        }
    )
    df = transform_units(df)
    return df.loc[:, ["date_time", "date_forecast", "lat", "lon", "no2", "pm25", "pm10"]]


def load_grib_file(file_path: str, type_of_level: str):
    """
    Load the grib file for a given "typeOfLevel"
    :param file_path: path to grib file
    :param type_of_level: "surface" to load PM info, "hybrid" to load NO2 info
    :return: xarray object
    """
    return xr.open_dataset(
        file_path,
        engine="cfgrib",
        filter_by_keys={"typeOfLevel": type_of_level},
    )


def transform_units(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data such that we have the same units as in the "new" API
    - Particulate matter is in kg per m3, but we need micrograms
    - NO2 is in kg/kg, but we need micrograms per m³
    :param df: data frame with columns pm25, pm10, and no2
    :return: data frame with same columns but transformed values for pm and no2
    """
    # The particulate matter is in kg per m3, but we need micrograms
    df["pm25"] = df["pm25"] * 1e9
    df["pm10"] = df["pm10"] * 1e9
    # NO2 is in kg/kg, but we need micrograms per m³
    # 1 m³ of air has about 1.225 kg at 15 degrees Celsius
    df["no2"] = df["no2"] * 1.225 * 1e9
    return df
