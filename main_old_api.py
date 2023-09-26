# The old API is the CAMS-Global API

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from fairq_data_cams.api_request import ApiRequest
from fairq_data_cams.db_connect import db_connect, send_data_clickhouse
from fairq_data_cams.retrieve_api_data import api_client, download_data_from_api
from fairq_data_cams.transform_grib_data import all_grib_files_to_one_df

# See what's the earliest day we already have in the DB
with db_connect() as db:
    min_date = db.execute("select min(date_forecast) from cams_old")[0][0]
print(min_date)

# Create pairs with first and last day of month
first_of_month = []
for year in range(2015, 2019):
    for month in range(1, 13):
        first_of_month.append(datetime.strptime(f"{year}{month}", "%Y%m"))
last_of_month = [x + relativedelta(months=1) - timedelta(days=1) for x in first_of_month]
first_of_month = [datetime.strftime(x, "%Y-%m-%d") for x in first_of_month]
last_of_month = [datetime.strftime(x, "%Y-%m-%d") for x in last_of_month]
month_ranges = zip(first_of_month, last_of_month)

client = api_client()
for dates in month_ranges:
    print(dates)
    request = ApiRequest(date_start=dates[0], date_end=dates[1])
    api_res = client.retrieve(request.api_address(), request.api_request_body(), request.format())
    download_data_from_api(api_res.location)

full_df = all_grib_files_to_one_df()
send_data_clickhouse(full_df, "cams_old")
