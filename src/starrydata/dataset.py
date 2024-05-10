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
    """Fetch the latest dataset from the specified project on Figshare and return its download URL and publication
    date. """
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


def read_dataset(file_content, dataset_type):
    """Read dataset from file content based on the type ('curves', 'samples', or 'papers') and return a pandas
    DataFrame. """
    if dataset_type == 'papers':
        data = json.loads(file_content)
    else:
        data = pd.read_csv(io.StringIO(file_content))
    return pd.DataFrame(data)


def load_dataset(download_url, dataset_type):
    """Load dataset from a URL into a pandas DataFrame."""
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            zip_data = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                filename = f"all_{dataset_type}.{('json' if dataset_type == 'papers' else 'csv')}"
                with zip_ref.open(filename) as file:
                    file_content = file.read().decode()
                    df = read_dataset(file_content, dataset_type)
                    logging.info(f"Successfully loaded the latest {filename} into a DataFrame.")
                    return df
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    return None


# Example usage
url, date = fetch_latest_dataset()
if url:
    df = load_dataset(url, 'samples')
    print(df.head())
else:
    logging.error("Failed to fetch dataset.")
