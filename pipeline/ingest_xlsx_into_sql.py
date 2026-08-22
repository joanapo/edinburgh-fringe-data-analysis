import click
import pandas as pd
from pathlib import Path
import sqlalchemy
from tqdm import tqdm
from typing import Optional

from df_datatypes import DataFrameDataTypes

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data'

def _get_source_files(raw_data_dir: Path) -> list:
    """
    Gets excel source files.
    :param filepath: Path to search for the excel files in.
    :returns: List of source filepaths.
    """
    source_filepaths = []
    for filepath in sorted(raw_data_dir.glob('*.xlsx')):
        if filepath.name.startswith('~$'):
            continue
        source_filepaths.append(filepath)

    return source_filepaths

def _clean_raw_data(file) -> pd.DataFrame:
    """
    Cleans raw excel, transforming it into a dataframe.
    :param file: Excel file to process.
    :return: Cleaned Pandas dataframe.
    """
    df = pd.read_excel(file)
    
    # reposition the header
    new_header = df.iloc[1]
    df = df[2:].reset_index(drop=True)
    df.columns = new_header

    # change column datatypes
    df = df.astype(DataFrameDataTypes.dtype)
    for col in DataFrameDataTypes.parse_dates:
        df[col] = pd.to_datetime(df[col])

    return df

def _get_year(df: pd.DataFrame) -> Optional[int]:
    try: 
        raw_year = df["Year"].iloc[0]
        return int(raw_year)
    except IndexError:
        return

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default=None, help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='edi_fringe', help='PostgreSQL database name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db):
    """
    Ingest Fringe data into PostgreSQL database.
    """
    if not pg_pass:
        raise click.UsageError('PostgreSQL password not provided. \n' \
        'Please provide the password as env variablePG_PASS or pass --pg-pass when running the script.')
    
    engine = sqlalchemy.create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    raw_data_dir = DATA_DIR / 'raw'
    source_filepaths = _get_source_files(raw_data_dir)

    ingested_years = {}
    
    for filepath in tqdm(source_filepaths, desc='Injecting XLSX into PostgreSQL'):
        try:
            cleaned_df = _clean_raw_data(filepath)
        except Exception as e:
            print(f'Skipping {filepath.name}: Failed to clean or parse the file.\nError: {e}')

        year = _get_year(cleaned_df)

        if not year:
            print(f'Skipping {filepath.name}: Failed to retrieve the year.')
            continue

        if year in ingested_years:
            print(f'Year {year} is already in the database. Overwriting.')
        ingested_years[year] = filepath.name

        table_name = f"fringe_data_{year}"

        try:
            cleaned_df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace'
        )
        except Exception as e:
            print(f'Failed to write table {table_name} to database.\nError: {e}')


if __name__ == '__main__':
    run()