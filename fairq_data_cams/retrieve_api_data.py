import os
import subprocess
from logging.config import dictConfig
from pathlib import Path
from zipfile import ZipFile

import cdsapi

from logging_config.logger_config import get_logger_config

dictConfig(get_logger_config())


def api_client() -> cdsapi.Client:
    """
    Create API client from the credentials taken from a yaml file stored in .cdsapirc.
    For the structure of the file see .cdsapirc_template.
    :return: Client object from cdsapi package
    """
    return cdsapi.Client(url=os.getenv("API_URL"), key=os.getenv("API_KEY"), verify=True, progress=False)


def unzip_file_to_nc_folder(file_path: str, attach: str = "") -> None:
    """
    Unzip a given zip file to the data/nc folder
    :param file_path: local path of the zip file
    :param attach: addition to each file name, excluding extension; defaults to an empty string
    """
    extraction_folder = Path("data") / "nc"

    with ZipFile(file_path, "r") as zip_obj:
        # List of all files and directories in the zip file
        zip_contents = zip_obj.namelist()

        # Extract each file individually
        for file_name in zip_contents:
            # Extract the file to the destination folder
            zip_obj.extract(file_name, extraction_folder)

            # Full path of the extracted file
            original_file_path = extraction_folder / file_name

            # Apply the attachment if provided
            if attach:
                # Split the file name and extension
                file_base = Path(file_name).stem
                file_extension = Path(file_name).suffix
                # Append the attachment to the base name
                new_file_name = f"{file_base}{attach}{file_extension}"
                new_file_path = extraction_folder / new_file_name
                # Rename the file to include the attachment
                original_file_path.rename(new_file_path)


def rm_old_data() -> None:
    """Remove all zip and all nc files."""
    subprocess.run(["/bin/rm", "-f", "*.zip"], cwd=".", check=True)
    subprocess.run(["/bin/rm", "-f", "*.nc"], cwd="data/nc", check=True)
