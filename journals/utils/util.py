from time import sleep
from random import random
from requests import get
import pandas as pd
import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def random_sleep(bottom: int, top: int) -> None:
    """Does nothing for random amount of seconds between range[0] and range[1] both points included"""
    r = random()
    amount = bottom + r * (top - bottom)
    logger.info(f"Sleeping for {round(amount, 1)} sec...")
    sleep(amount)

def parse_link(link, fake_agent=False) -> BeautifulSoup:
    headers = {}
    if fake_agent:
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    
    response = get(link, headers=headers)
    page_html = response.text

    if response.status_code != 200:
        return response.status_code

    return BeautifulSoup(page_html, features="html.parser")

def add_to_csv(path: str, data: dict) -> None:
    logger.debug(f"Adding data to {path}")
    file_path = Path(path)
    if not file_path.is_file():
        file_path.touch()

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()

    new_row = pd.DataFrame(data, index=[0])  # Convert the dictionary to a DataFrame
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)

def get_csv_name(journal_name: str) -> str:
    script_path = Path(__file__).parent
    journals_dir = script_path.parent
    data_dir = journals_dir.joinpath("parsed_data")
    return data_dir.joinpath(f"{journal_name}.csv")