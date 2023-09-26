# Script for daily job
# Retrieve data from yesterday and today to avoid gaps if it does not work for one day

from datetime import datetime, timedelta

from dateutil.utils import today

from fairq_data_cams.api_request import ApiRequest
from fairq_data_cams.db_connect import send_data_clickhouse
from fairq_data_cams.retrieve_api_data import api_client, download_data_from_api
from fairq_data_cams.transform_nc_data import all_nc_files_to_one_df

date_start = datetime.strftime(today() - timedelta(days=1), "%Y-%m-%d")
date_end = datetime.strftime(today(), "%Y-%m-%d")

client = api_client()
request = ApiRequest(date_start=date_start, date_end=date_end)
api_res = client.retrieve(request.api_address(), request.api_request_body(), request.format())
download_data_from_api(api_res.location)
full_df = all_nc_files_to_one_df()
send_data_clickhouse(full_df, "cams")
