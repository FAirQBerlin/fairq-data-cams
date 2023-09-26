from datetime import datetime

from dateutil.relativedelta import relativedelta

start_new_api = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(years=3)
start_higher_model_level = datetime(2019, 7, 7)


class ApiRequest:
    """
    Class to prepare the API request. Depending on the date, the old vs. new API is addressed.
    The new API is faster, but provides only data after some date in May 2019.
    """

    def __init__(self, date_start: str, date_end: str):
        """
        :param date_start: first date of forecast, e.g., "2020-01-05"
        :param date_end: last date of forecast, e.g., "2020-01-10"
        """
        self.date_start = date_start
        self.date_end = date_end
        self.date_start_dt = datetime.strptime(self.date_start, "%Y-%m-%d")
        self.date_end_dt = datetime.strptime(self.date_end, "%Y-%m-%d")

        self.use_new_api = self.check_if_new_api()
        self.check_different_model_levels()

        self.variables = ["nitrogen_dioxide", "particulate_matter_10um", "particulate_matter_2.5um"]
        self.berlin_bbox = [52.7, 13, 52.3, 13.8]

    def api_request_body(self) -> dict:
        """
        Prepare body of the API request. Both date_start and date_end will be in the API result, i.e., it's a closed
        interval.
        Forecasts are retrieved for all dates from date_start to date_end for 96 hours in the future.
        :return: dictionary to be used in a post request to the API; depending on date_start and date_end, it has the
        appropriate format for the old vs. new API.
        """
        date_range = f"{self.date_start}/{self.date_end}"

        request_body = {
            "date": date_range,
            "type": "forecast",
            "variable": self.variables,
            "time": "00:00",
            "area": self.berlin_bbox,
        }

        if self.use_new_api:
            request_body["format"] = "netcdf"
            request_body["model"] = "ensemble"
            request_body["level"] = "0"
            request_body["leadtime_hour"] = [str(x) for x in (range(4 * 24))]

        if not self.use_new_api:
            request_body["format"] = "grib"
            # NO2 is a multi-level variable, so we need to select pressure or model level.
            # The maximum level before July 7 2019 was 60, and 137 on July 7 2019 and later.
            # The maximum level is the bottom of the atmosphere, so we use this.
            request_body["model_level"] = "60" if self.date_start_dt < start_higher_model_level else "137"
            request_body["leadtime_hour"] = [str(x) for x in (range(5 * 24))]

        return request_body

    def api_address(self) -> str:
        """
        Address of the old vs. new API
        """
        return (
            "cams-europe-air-quality-forecasts" if self.use_new_api else "cams-global-atmospheric-composition-forecasts"
        )

    def format(self) -> str:
        """
        Target format delivered to the API
        """
        return "download.nc" if self.use_new_api else "download.netcdf_zip"

    def check_if_new_api(self) -> bool:
        """
        Check if the period from start to end date does not overlap the date where we have to change from the old to the
        new API. If both are in the period of the old API, False is returned; if both are in the period of the new API,
        True is returned.
        """
        if (self.date_start_dt < start_new_api) & (self.date_end_dt < start_new_api):
            use_new_api = False
        elif (self.date_start_dt >= start_new_api) & (self.date_end_dt >= start_new_api):
            use_new_api = True
        else:
            raise ValueError(
                f"We have to use different APIs for days before {start_new_api} ",
                f"vs. days for {start_new_api} and later. Please make separate API calls.",
            )
        return use_new_api

    def check_different_model_levels(self):
        if not self.use_new_api:
            if (self.date_start_dt < start_higher_model_level) and (self.date_end_dt >= start_higher_model_level):
                raise ValueError(
                    f"We have to use different model levels for days before {start_higher_model_level} ",
                    f"vs. days for {start_higher_model_level} and later. Please make separate API calls.",
                )
