import logging
import os
from logging.config import dictConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
from clickhouse_driver import Client
from dotenv import load_dotenv

from logging_config.logger_config import get_logger_config

logger = logging.getLogger(__name__)
load_dotenv()

dictConfig(get_logger_config())


def db_connect() -> Client:
    """
    Return Client object for db connection to clickhouse.
    :return: Client object for db connection to clickhouse
    """
    return Client(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        secure=True,
        verify=True,
        ca_certs="certificates/INWT-IPA-CA.pem",
        settings={"use_numpy": True},
    )


def send_data_clickhouse(
    df: pd.DataFrame,
    table_name: str,
    mode: str = "replace",
    schema_name: str = "fairq_raw",
) -> None:
    """
    Send data of a given df to clickhouse.
    :param df: dataframe containing data to write to db
    :param mode: "insert", "replace", or "truncate". "insert" just inserts the data. "truncate" removes everything from
    the table first and then inserts the new data. "replace" inserts the data and then optimizes the table to remove
    all duplicates w.r.t. the order statement. Only allowed if the table engine is ReplacingMergeTree.
    Default in the repo is "replace".
    :param schema_name: name of db schema
    :param table_name: name of db table
    """
    if mode not in ["insert", "replace", "truncate"]:
        msg = "Allowed modes are: insert, replace, truncate"
        raise ValueError(msg)

    if mode == "replace":
        check_for_replacing_merge_tree(table_name, schema_name)

    if mode == "truncate":
        with db_connect() as db:
            logger.info("Truncating table...")
            db.execute(f"truncate table {schema_name}.{table_name};")

    if df.shape[0] > 0:
        with db_connect() as db:
            logger.info("Sending data to database...")
            db.insert_dataframe(f"INSERT INTO {schema_name}.{table_name} VALUES", df)

            if mode == "replace":
                logger.info("Optimizing table to remove duplicates...")
                db.execute(f"Optimize table {schema_name}.{table_name} final;")
            if materialized_view_exists(table_name, schema_name):
                logger.info("Optimize table processed by materialized view...")
                db.execute(f"Optimize table {schema_name}.{table_name}_processed final;")

            logger.info("Done <3")


def check_for_replacing_merge_tree(table_name: str, schema_name: str) -> None:
    """
    Check if target table has engine "check_for_replacing_merge_tree"; raise error if not.
    :param table_name: name of the table
    :param schema_name: name of the database schema
    """
    with db_connect() as db:
        logger.info("Checking if table engine is 'ReplacingMergeTree'...")
        table_engine = db.execute(
            f"SELECT engine FROM system.tables where database = '{schema_name}' and name = '{table_name}';"  # noqa: S608 - internal identifiers only, no user input
        )[0][0]
    if table_engine != "ReplacingMergeTree":
        msg = f"Can't use mode 'replace' for table {table_name} since table engine is not ReplacingMergeTree."
        raise ValueError(msg)


def materialized_view_exists(table_name: str, schema_name: str) -> bool:
    """
    Check if target table for materialized view exists, so
    it can be optimized after insert as well.
    :param table_name: name of the table
    :param schema_name: name of the database schema
    """
    with db_connect() as db:
        logger.info("Checking if materialized view exists ...")
        mv_exists = db.execute(f"exists {schema_name}.{table_name}_processed;")[0][0]
    return mv_exists == 1
