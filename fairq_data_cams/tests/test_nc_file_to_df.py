from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from fairq_data_cams.transform_nc_data import nc_file_to_df


@pytest.fixture
def dummy_nc_file(tmp_path: Path) -> str:
    """
    Pytest fixture to create a dummy .nc file for testing.
    The file will be created in a temporary directory managed by pytest.
    """
    times = pd.to_datetime(["2023-01-01", "2023-01-02"])
    lats = np.array([10.0, 20.0])
    lons = np.array([100.0, 110.0])
    data_values = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])  # Shape: (time, lat, lon)

    ds = xr.Dataset(
        {"temperature": (("time", "lat", "lon"), data_values), "pressure": (("time", "lat", "lon"), data_values * 10)},
        coords={"time": times, "lat": lats, "lon": lons},
    )

    file_path = tmp_path / "test_data.nc"

    ds.to_netcdf(file_path)

    return str(file_path)


def test_nc_file_to_df_conversion(dummy_nc_file: str) -> None:
    """
    Test case for the nc_file_to_df function.
    It uses the dummy_nc_file fixture to get a path to a test .nc file.
    """
    df = nc_file_to_df(dummy_nc_file)

    # 1. Check if the output is a pandas DataFrame
    assert isinstance(df, pd.DataFrame)

    # 2. Check if the DataFrame is not empty
    assert not df.empty

    # 3. Check for expected columns
    expected_columns = ["time", "lat", "lon", "temperature", "pressure"]
    assert all(col in df.columns for col in expected_columns)
