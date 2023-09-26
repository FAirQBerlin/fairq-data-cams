import glob
import os


def list_files_of_type(file_type: str) -> list:
    """
    List all files of a type in the respective folder
    :param file_type: "nc" or "grib"
    :return: list with full file paths relative to project root
    """
    pattern = os.path.join("data", file_type, f"*.{file_type}")
    return glob.glob(pattern)


def check_for_duplicates(full_df):
    """
    Check if every combination of "date_time", "date_forecast", "lat", and "lon" appears only once
    :param full_df: full data frame with rows from all nc files
    :return: nothing; but may throw an error.
    """
    index_cols = ["date_time", "date_forecast", "lat", "lon"]
    duplicate_rows = full_df[full_df.duplicated(subset=index_cols, keep=False)].sort_values(index_cols)
    if duplicate_rows.shape[0] > 0:
        error_msg = "There are duplicates in the data."
        raise ValueError(error_msg)
