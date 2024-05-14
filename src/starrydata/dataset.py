import json
import requests
import io
import zipfile
import logging
from tqdm import tqdm

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Dataset:
    def __init__(self, project_id: int = 155129, api_url: str = "https://api.figshare.com/v2", date: str = None):
        """
        Initialize the Dataset object and download the dataset ZIP file.

        :param project_id: The ID of the Figshare project containing the datasets.
        :param api_url: The base URL of the Figshare API.
        :param date: The date of the dataset to load in 'YYYY-MM-DD' format. If None, the latest dataset is loaded.
        """
        self.project_id = project_id
        self.api_url = api_url
        self.date = date
        self.zip_data = self._download_zip()

    def _fetch_article(self) -> dict:
        if self.date:
            search_for = f"{self.date.replace('-', '')}_starrydata2"
            search_url = f"{self.api_url}/articles/search"
            headers = {"Content-Type": "application/json"}
            search_body = {"project_id": self.project_id, "search_for": search_for}
            response = requests.post(search_url, headers=headers, data=json.dumps(search_body))
            articles = response.json()
            if not articles:
                logging.error(
                    f"No articles found for the specified date: {self.date}. "
                    "Please check the valid dates at https://figshare.com/projects/Starrydata_datasets/155129"
                )
                return None
            return articles[0]

        articles = requests.get(f"{self.api_url}/projects/{self.project_id}/articles").json()
        return max(articles, key=lambda x: x['published_date'])

    def _download_zip(self) -> io.BytesIO:
        article = self._fetch_article()
        if not article:
            return None
        article_details = requests.get(article['url_public_api']).json()
        download_url = article_details['files'][0]['download_url']
        response = requests.get(download_url, stream=True)
        file_size = int(response.headers.get('Content-Length', 0))
        chunk_size = 1024  # Set chunk size to 1024 bytes (1 KB)
        buffer = io.BytesIO()
        with tqdm(
                desc="Downloading dataset ZIP file",
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,  # Use 1024 to match byte size correctly
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    buffer.write(chunk)
                    progress_bar.update(len(chunk))
        buffer.seek(0)  # Reset buffer position to the beginning
        return buffer

    def _extract_file_from_zip(self, filename: str) -> io.BytesIO:
        with zipfile.ZipFile(self.zip_data, 'r') as zip_ref:
            with zip_ref.open(filename) as file:
                return io.BytesIO(file.read())

    @property
    def all_samples(self) -> io.BytesIO:
        """
        Extract and load the 'all_samples.csv' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'all_samples.csv'.
        """
        filename = "all_samples.csv"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def all_papers(self) -> io.BytesIO:
        """
        Extract and load the 'all_papers.json' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'all_papers.json'.
        """
        filename = "all_papers.json"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def all_curves(self) -> io.BytesIO:
        """
        Extract and load the 'all_curves.csv' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'all_curves.csv'.
        """
        filename = "all_curves.csv"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def database_snapshot(self) -> str:
        """
        Extract and return the contents of the 'db_snapshot.txt' file from the downloaded ZIP file as a string.

        :return: A string containing the contents of 'db_snapshot.txt'.
        """
        filename = "db_snapshot.txt"
        file_data = self._extract_file_from_zip(filename)
        return file_data.getvalue().decode('utf-8')
