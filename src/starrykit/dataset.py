import requests
import io
import zipfile
from datetime import datetime
import logging
import pandas as pd

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Loading dataset module...")


def fetch_latest_dataset(project_id=155129, api_url="https://api.figshare.com/v2"):
    """Fetch the latest dataset from the specified project on Figshare."""
    response = requests.get(f"{api_url}/projects/{project_id}/articles")
    if response.status_code == 200:
        articles = response.json()
        latest_article = max(articles, key=lambda x: x['published_date'])
        response = requests.get(latest_article['url_public_api'])
        if response.status_code == 200:
            latest_file = response.json()
            download_url = latest_file['files'][0]['download_url']
            published_date = datetime.fromisoformat(latest_file['published_date'].rstrip("Z")).strftime("%Y%m%d")
            return download_url, published_date
    return None, None


def download_and_load_dataset(download_url):
    """Download and load the dataset from Figshare into a pandas DataFrame."""
    try:
        # Download the file
        response = requests.get(download_url)

        if response.status_code == 200:
            zip_data = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                csv_file = zip_ref.namelist()[0]  # Assume the first file in the zip is the CSV
                with zip_ref.open("all_curves.csv") as file:
                    df = pd.read_csv(file)
                    return df
        else:
            logging.info(f"Failed to download the file. Status code: {response.status_code}")
    except Exception as e:
        logging.info(f"An error occurred: {e}")
    return None


def load_latest_dataset():
    """Fetch and load the latest dataset from the Starrydata project on Figshare into a pandas DataFrame."""
    download_url, published_date = fetch_latest_dataset()
    if download_url:
        df = download_and_load_dataset(download_url)
        if df is not None:
            logging.info(f"Successfully loaded the dataset from {published_date} into a DataFrame.")
            return df
        else:
            logging.info("Failed to load the dataset into a DataFrame.")
    else:
        logging.info("Failed to fetch the latest dataset.")
    return None
