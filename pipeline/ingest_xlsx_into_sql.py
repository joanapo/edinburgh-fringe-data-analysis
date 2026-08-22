import click
import os
import pandas as pd
from pathlib import Path
import sqlalchemy
from tqdm import tqdm

from df_datatypes import DataFrameDataTypes

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

def _clean_raw_data(file) -> pd.DataFrame:
    """
    Cleans raw excel, transforming it into a dataframe.
    :param file: Excel file to process.
    :return: Cleaned Pandas dataframe.
    """
    df = pd.read_excel(file)
    
    # reposition the header
    new_header = df.iloc[1]
    df = df[2:]
    df.columns = new_header

    # change column datatypes
    df = df.astype(DataFrameDataTypes.dtype)
    for col in DataFrameDataTypes.parse_dates:
        df[col] = pd.to_datetime(df[col])

    return df




def _ingest_table_into_db(target_table_name):
    pass


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='edi_fringe', help='PostgreSQL database name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db):
    """
    Ingest Fringe data into PostgreSQL database.
    """
    engine = sqlalchemy.create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    raw_data_dir = DATA_DIR / "raw"
    
    for file in tqdm(os.listdir(raw_data_dir), desc="Injecting XLSX into PostgreSQL"):
        if file.endswith(".xlsx"):
            filepath = raw_data_dir / file
            cleaned_df = _clean_raw_data(filepath)
            year = cleaned_df["Year"][0]
            table_name = f"fringe_data_{year}"

            cleaned_df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace'
        )


if __name__ == '__main__':
    run()