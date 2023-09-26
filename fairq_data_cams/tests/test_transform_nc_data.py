import os
from datetime import date, timedelta

import pandas as pd
from pandas import Timestamp

from fairq_data_cams.transform_nc_data import add_date_columns, df_from_nc_file


def test_df_from_nc_file():
    res = df_from_nc_file(file_path=os.path.join(os.path.dirname(__file__), "data/ENS_FORECAST_2022-05-24.nc"))
    assert res.columns.tolist() == ["date_time", "date_forecast", "lat", "lon", "no2", "pm25", "pm10"]
    # We want exactly this column order - like in the database


def test_add_date_columns():
    input_df = pd.DataFrame({"time": [timedelta(hours=x) for x in [0, 1, 24, 95]]})
    res = add_date_columns(
        file_path=os.path.join(os.path.dirname(__file__), "data/ENS_FORECAST_2022-05-24.nc"), df=input_df
    )

    assert set(res.date_forecast) == {date(2022, 5, 24)}
    assert res.date_time.to_list() == [
        Timestamp(2022, 5, 24, 0),
        Timestamp(2022, 5, 24, 1),
        Timestamp(2022, 5, 25, 0),
        Timestamp(2022, 5, 27, 23),
    ]


# __file__ = "fairq_data_cams/tests/test_transform_nc_data.py"
