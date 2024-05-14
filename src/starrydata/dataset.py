import json
import requests
import io
import zipfile
from datetime import datetime
import logging
import pandas as pd
from tqdm import tqdm

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Loading dataset module...")

def load_dataset(dataset_type: str, project_id: int = 155129,
                 api_url: str = "https://api.figshare.com/v2", date: str = None) -> pd.DataFrame:
    """
    Fetch and load the specified dataset from the Starrydata project on Figshare into a pandas DataFrame.

    :param dataset_type: The type of dataset to load. Can be 'curves', 'samples', or 'papers'.
    :param project_id: The ID of the Figshare project containing the datasets.
    :param api_url: The base URL of the Figshare API.
    :param date: The date of the dataset to load in 'YYYY-MM-DD' format. If None, the latest dataset is loaded.
    :return: A pandas DataFrame containing the loaded dataset, or None if the dataset could not be loaded.
    """
    if dataset_type not in ['curves', 'samples', 'papers']:
        logging.error(f"Invalid dataset type: {dataset_type}. Must be 'curves', 'samples', or 'papers'.")
        return None

    if date:
        search_for = f"{date.replace('-', '')}_starrydata2"
        search_url = f"{api_url}/articles/search"
        headers = {
            "Content-Type": "application/json"
        }
        search_body = {
            "project_id": project_id,
            "search_for": search_for
        }

        response = requests.post(search_url, headers=headers, data=json.dumps(search_body))
        articles = response.json()

        if not articles:
            logging.error(f"No articles found for the specified date: {date}")
            return None

        article = articles[0]
    else:
        articles = requests.get(f"{api_url}/projects/{project_id}/articles").json()
        article = max(articles, key=lambda x: x['published_date'])

    article_details = requests.get(article['url_public_api']).json()
    download_url = article_details['files'][0]['download_url']

    # Get the file size
    head_response = requests.head(download_url)
    file_size = int(head_response.headers.get('Content-Length', 0))

    # Initialize the progress bar
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

    # Download the file and update the progress bar
    response = requests.get(download_url, stream=True)
    with open('temp.zip', 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress_bar.update(len(chunk))

    # Close the progress bar
    progress_bar.close()

    # Read the downloaded zip file
    zip_data = io.BytesIO(open('temp.zip', 'rb').read())

    if response.status_code == 200:
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            filename = f"all_{dataset_type}.{'json' if dataset_type == 'papers' else 'csv'}"
            with zip_ref.open(filename) as file:
                if dataset_type == 'papers':
                    data = json.load(file)
                    df = pd.DataFrame(data)
                else:
                    df = pd.read_csv(file)
                logging.info(
                    f"Successfully loaded {filename} from {article['published_date']} into a DataFrame.")
                return df
    else:
        logging.error(f"Failed to download the file. Status code: {response.status_code}")
