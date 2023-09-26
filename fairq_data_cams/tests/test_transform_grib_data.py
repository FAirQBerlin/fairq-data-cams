import os

import pandas as pd
from pandas.testing import assert_frame_equal

from fairq_data_cams.transform_grib_data import df_from_grib_file, transform_units


def test_df_from_grib_file():
    test_file_name = (
        "adaptor.mars_constrained.external-1656056684.1777284-11098-9-e961d6d8-898d-450d-9c02-b0a5ded3d3f9.grib"
    )
    res = df_from_grib_file(file_path=os.path.join(os.path.dirname(__file__), "data", test_file_name))

    assert res.columns.tolist() == ["date_time", "date_forecast", "lat", "lon", "no2", "pm25", "pm10"]
    # We want exactly this column order - like in the database
    assert any(res.no2.notnull())
    assert any(res.pm25.notnull())
    assert any(res.pm10.notnull())


def test_transform_units():
    input_df = pd.DataFrame({"pm25": [1e-9, 0.000000123], "pm10": [0.000000123, 1e-9], "no2": [1 / 1.225, 1e-9]})
    expected = pd.DataFrame({"pm25": [1.0, 123.0], "pm10": [123.0, 1.0], "no2": [1e9, 1.225]})
    res = transform_units(input_df)
    assert_frame_equal(res, expected)
