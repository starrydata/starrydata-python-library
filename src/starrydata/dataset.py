import json
import requests
import io
import zipfile
import logging
import pandas as pd
from tqdm import tqdm

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Loading dataset module...")

def _validate_dataset_type(dataset_type: str) -> bool:
    """
    Validate the dataset type.

    :param dataset_type: The type of dataset to load.
    :return: True if the dataset type is valid, otherwise False.
    """
    valid_types = ['curves', 'samples', 'papers']
    if dataset_type not in valid_types:
        logging.error(f"Invalid dataset type: {dataset_type}. Must be one of {valid_types}.")
        return False
    return True

def _fetch_article(project_id: int, api_url: str, date: str = None) -> dict:
    """
    Fetch the article metadata from Figshare.

    :param project_id: The ID of the Figshare project.
    :param api_url: The base URL of the Figshare API.
    :param date: The date of the dataset to load in 'YYYY-MM-DD' format.
    :return: The article metadata as a dictionary.
    """
    if date:
        search_for = f"{date.replace('-', '')}_starrydata2"
        search_url = f"{api_url}/articles/search"
        headers = {"Content-Type": "application/json"}
        search_body = {"project_id": project_id, "search_for": search_for}

        response = requests.post(search_url, headers=headers, data=json.dumps(search_body))
        articles = response.json()

        if not articles:
            logging.error(f"No articles found for the specified date: {date}")
            return None
        return articles[0]

    articles = requests.get(f"{api_url}/projects/{project_id}/articles").json()
    return max(articles, key=lambda x: x['published_date'])

def _download_file(url: str, local_path: str) -> None:
    """
    Download a file from the specified URL and save it locally.

    :param url: The URL to download the file from.
    :param local_path: The local path to save the downloaded file.
    """
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))

    with open(local_path, 'wb') as file:
        for chunk in tqdm(response.iter_content(chunk_size=1024), total=file_size, unit='B', unit_scale=True):
            if chunk:
                file.write(chunk)

def _extract_file_from_zip(zip_path: str, filename: str) -> io.BytesIO:
    """
    Extract a specific file from a zip archive.

    :param zip_path: The path to the zip file.
    :param filename: The name of the file to extract.
    :return: A BytesIO object containing the extracted file data.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open(filename) as file:
            return io.BytesIO(file.read())

def _load_data_from_file(file_data: io.BytesIO, dataset_type: str) -> pd.DataFrame:
    """
    Load data from a file into a pandas DataFrame.

    :param file_data: The file data as a BytesIO object.
    :param dataset_type: The type of dataset ('curves', 'samples', 'papers').
    :return: A pandas DataFrame containing the data.
    """
    if dataset_type == 'papers':
        data = json.load(file_data)
        return pd.DataFrame(data)
    return pd.read_csv(file_data)

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
    if not _validate_dataset_type(dataset_type):
        return None

    article = _fetch_article(project_id, api_url, date)
    if not article:
        return None

    article_details = requests.get(article['url_public_api']).json()
    download_url = article_details['files'][0]['download_url']
    temp_zip_path = 'temp.zip'

    _download_file(download_url, temp_zip_path)

    filename = f"all_{dataset_type}.{'json' if dataset_type == 'papers' else 'csv'}"
    file_data = _extract_file_from_zip(temp_zip_path, filename)

    df = _load_data_from_file(file_data, dataset_type)
    logging.info(f"Successfully loaded {filename} from {article['published_date']} into a DataFrame.")
    return df
