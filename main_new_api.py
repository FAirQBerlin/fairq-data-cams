# The new API is the CAMS-EU API

from datetime import datetime

import pandas as pd
from dateutil.utils import today

from fairq_data_cams.api_request import ApiRequest, start_new_api
from fairq_data_cams.db_connect import send_data_clickhouse
from fairq_data_cams.retrieve_api_data import api_client, download_data_from_api
from fairq_data_cams.transform_nc_data import all_nc_files_to_one_df

date_start = start_new_api
date_end = datetime.strftime(today(), "%Y-%m-%d")
all_dates_new_api = [datetime.strftime(x, "%Y-%m-%d") for x in pd.date_range(date_start, date_end)]

client = api_client()
for date in all_dates_new_api:
    print(date)
    request = ApiRequest(date_start=date, date_end=date)
    api_res = client.retrieve(request.api_address(), request.api_request_body(), request.format())
    download_data_from_api(api_res.location)

full_df = all_nc_files_to_one_df()
send_data_clickhouse(full_df, "cams")
