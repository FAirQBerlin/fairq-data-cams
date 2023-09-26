import pandas as pd
from pytest import raises

from fairq_data_cams.transform_utils import check_for_duplicates


def test_check_for_duplicates():
    df_ok = pd.DataFrame(
        {"date_time": [1, 1, 2, 2], "date_forecast": [1, 1, 2, 2], "lat": [2, 3, 4, 5], "lon": [2, 3, 4, 4]}
    )
    df_duplicates = pd.DataFrame(
        {"date_time": [1, 1, 2, 2], "date_forecast": [1, 1, 2, 2], "lat": [2, 2, 4, 5], "lon": [2, 2, 4, 4]}
    )
    check_for_duplicates(df_ok)

    with raises(ValueError):
        check_for_duplicates(df_duplicates)
