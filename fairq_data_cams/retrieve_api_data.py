import logging
import os
from logging.config import dictConfig
from zipfile import ZipFile

import cdsapi
import wget

from logging_config.logger_config import get_logger_config

dictConfig(get_logger_config())


def api_client() -> cdsapi.Client:
    """
    Create API client from the credentials taken from a yaml file stored in .cdsapirc.
    For the structure of the file see .cdsapirc_template.
    :return: Client object from cdsapi package
    """
    return cdsapi.Client(url=os.getenv("API_URL"), key=os.getenv("API_KEY"), verify=True, progress=False)


def download_data_from_api(api_file_location) -> None:
    """
    Downloads data from the API. If it's an nc or grib file, it is directly stored in data/nc resp. data/grib.
    If it's a zip file (containing nc), it's first stored in data/zip and then unpacked to the data/nc folder.
    :param api_file_location: location from api result
    :return: nothing
    """
    file_extension = api_file_location.split(".")[-1]
    file_path = os.path.join("data", file_extension, os.path.basename(api_file_location))

    if file_extension in ["zip", "nc", "grib"]:
        if os.path.exists(file_path):
            logging.info(f".{file_extension} file already exists")
        else:
            logging.info(f"Downloading .{file_extension} file")
            wget.download(api_file_location, out=os.path.join("data", file_extension))

    if file_extension == "zip":
        logging.info("Unzipping {}".format(file_path))
        unzip_file_to_nc_folder(file_path)


def unzip_file_to_nc_folder(file_path: str) -> None:
    """
    Unzip a given zip file to the data/nc folder
    :param file_path: local path of the zip file
    """
    with ZipFile(file_path, "r") as zip_obj:
        zip_obj.extractall(os.path.join("data", "nc"))
