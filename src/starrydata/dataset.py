import json

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


def load_dataset(dataset_type: str, project_id: int = 155129,
                 api_url: str = "https://api.figshare.com/v2") -> pd.DataFrame:
    """
    Fetch and load the latest specified dataset from the Starrydata project on Figshare into a pandas DataFrame.

    :param dataset_type: The type of dataset to load. Can be 'curves', 'samples', or 'papers'.
    :param project_id: The ID of the Figshare project containing the datasets.
    :param api_url: The base URL of the Figshare API.
    :return: A pandas DataFrame containing the loaded dataset, or None if the dataset could not be loaded.
    """
    if dataset_type not in ['curves', 'samples', 'papers']:
        logging.error(f"Invalid dataset type: {dataset_type}. Must be 'curves', 'samples', or 'papers'.")
        return None

    articles = requests.get(f"{api_url}/projects/{project_id}/articles").json()
    article = max(articles, key=lambda x: x['published_date'])

    article_details = requests.get(article['url_public_api']).json()
    download_url = article_details['files'][0]['download_url']

    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            zip_data = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                filename = f"all_{dataset_type}.{'json' if dataset_type == 'papers' else 'csv'}"
                with zip_ref.open(filename) as file:
                    if dataset_type == 'papers':
                        data = json.load(file)
                        df = pd.DataFrame(data)
                    else:
                        df = pd.read_csv(file)
                    logging.info(
                        f"Successfully loaded the latest {filename} from {article['published_date']} into a DataFrame.")
                    return df
        else:
            logging.error(f"Failed to download the file. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")