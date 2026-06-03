from datetime import datetime

from dateutil.relativedelta import relativedelta

start_new_api = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(years=3)
start_higher_model_level = datetime(2019, 7, 7)


class ApiRequest:
    """
    Class to prepare the API request. The API to get European-CAMS-data provides data for three years in the past and
    four days in the future.
    """

    def __init__(self, date_start: str, date_end: str) -> None:
        """
        :param date_start: first date of forecast, e.g., "2020-01-05"
        :param date_end: last date of forecast, e.g., "2020-01-10"
        """
        self.date_start = date_start
        self.date_end = date_end
        self.date_start_dt = datetime.strptime(self.date_start, "%Y-%m-%d")
        self.date_end_dt = datetime.strptime(self.date_end, "%Y-%m-%d")
        self.variables = ["nitrogen_dioxide", "particulate_matter_10um", "particulate_matter_2.5um"]
        self.berlin_bbox = [52.7, 13, 52.3, 13.8]

    def api_request_body(self) -> dict:
        """
        Prepare body of the API request. Both date_start and date_end will be in the API result, i.e., it's a closed
        interval.
        Forecasts are retrieved for all dates from date_start to date_end for 96 hours in the future.
        :return: dictionary to be used in a post request to the API
        """
        date_range = f"{self.date_start}/{self.date_end}"

        return {
            "date": date_range,
            "type": "forecast",
            "variable": self.variables,
            "time": "00:00",
            "area": self.berlin_bbox,
            "format": "netcdf_zip",
            "model": "ensemble",
            "level": "0",
            "leadtime_hour": [str(x) for x in (range(4 * 24))],
        }

    def api_address(self) -> str:
        """
        Address of the Copernicus (Athmosphere) Data Store (CDS) API
        """
        return "cams-europe-air-quality-forecasts"

    def format(self) -> str:
        """
        Target format delivered to the API
        """
        return "download_netcdf.zip"
