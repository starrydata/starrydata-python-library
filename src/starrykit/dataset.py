import requests
import os
import zipfile
from datetime import datetime
import logging

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


def download_and_prepare_dataset(download_url, published_date):
    """Download and extract the dataset."""
    zip_path = f"{published_date}.zip"
    dir_path = f"./{published_date}"

    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            with open(zip_path, 'wb') as file:
                file.write(response.content)

            os.makedirs(dir_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(dir_path)
            return dir_path
    except Exception as e:
        logging.info(f"An error occurred: {e}")
    return None


def download_dataset():
    """Fetch, download, and prepare the latest dataset from the Starrydata project on Figshare."""
    download_url, published_date = fetch_latest_dataset()
    if download_url and published_date:
        download_and_prepare_dataset(download_url, published_date)
        return published_date
    else:
        logging.info("Failed to fetch the latest dataset.")
        return None
