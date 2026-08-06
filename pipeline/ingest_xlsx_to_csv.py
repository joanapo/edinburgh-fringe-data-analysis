import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from df_datatypes import DataFrameDataTypes

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

def clean_raw_data(file) -> pd.DataFrame:
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

def ingest_data_into_csv(df: pd.DataFrame) -> None:
    """
    Ingest cleaned dataframe into a single .csv file.
    :param df: Dataframe.
    :return: None
    """
    # create output path 
    csv_file_dir = DATA_DIR / "processed"

    csv_file_path = csv_file_dir / "edinburgh_fringe_data.csv"

    if not os.path.exists(csv_file_dir):
        os.makedirs(csv_file_dir)

        # Headers only
        df.head(n=0).to_csv(csv_file_path)

    df.to_csv(csv_file_path, mode="a", header=False)


def run() -> None:
    """
    Ingest Edinburgh Fringe data from Excel into a single CSV file.
    :return: None
    """
    raw_data_dir = DATA_DIR / "raw"

    for file in tqdm(os.listdir(raw_data_dir), desc="Injecting XLSX into CSV"):
        if file.endswith(".xlsx"):
            filepath = raw_data_dir / file
            cleaned_df = clean_raw_data(filepath)
            ingest_data_into_csv(cleaned_df)

if __name__ == '__main__':
    run()