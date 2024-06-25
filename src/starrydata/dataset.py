import json
import requests
import io
import zipfile
import logging
from tqdm import tqdm

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Dataset:
    def __init__(self, date: str = None, zip_path: str = None):
        """
        Initialize the Dataset object and download the dataset ZIP file if local_zip_path is not provided.

        :param date: The date of the dataset to load in 'YYYY-MM-DD' format. If None, the latest dataset is loaded.
        :param zip_path: Path to the local ZIP file. If provided, the ZIP file will be loaded from this path.
        """
        self.project_id = 155129
        self.api_url = "https://api.figshare.com/v2"
        self.date = date
        self.local_zip_path = zip_path

        if zip_path:
            self.zip_data = self._load_local_zip(zip_path)
        else:
            self.zip_data = self._download_zip()

        self._print_dataset_timestamp()

    def _load_local_zip(self, path: str) -> io.BytesIO:
        """
        Load the ZIP file from a local path.

        :param path: Path to the local ZIP file.
        :return: A BytesIO object containing the ZIP file data.
        """
        logging.info(f"Loading ZIP file from local path: {path}")
        buffer = io.BytesIO()
        with open(path, 'rb') as f:
            buffer.write(f.read())
        buffer.seek(0)  # Reset buffer position to the beginning
        logging.info("Local ZIP file loaded into memory.")
        return buffer

    def _fetch_article(self) -> dict:
        logging.info("Fetching dataset information.")
        if self.date:
            search_for = f"{self.date.replace('-', '')}_starrydata2"
            search_url = f"{self.api_url}/articles/search"
            headers = {"Content-Type": "application/json", "User-Agent": "Starrydata"}
            search_body = {"project_id": self.project_id, "search_for": search_for}
            response = requests.post(search_url, headers=headers, data=json.dumps(search_body))

            if response.status_code == 200:
                articles = response.json()
                if not articles:
                    logging.error(
                        f"No datasets found for the specified date: {self.date}. "
                        "Please check the valid dates at https://figshare.com/projects/Starrydata_datasets/155129"
                    )
                    return None
                logging.info(f"Found dataset for date {self.date}: {articles[0]['title']}")
                return articles[0]
            else:
                logging.error(
                    f"Failed to fetch articles. Status code: {response.status_code}, Response: {response.text}")
                return None

        logging.info("No specific date provided. Fetching the latest dataset.")
        response = requests.get(f"{self.api_url}/projects/{self.project_id}/articles")

        if response.status_code == 200:
            articles = response.json()
            latest_article = max(articles, key=lambda x: x['published_date'])
            logging.info(f"Found latest dataset: {latest_article['title']}")
            return latest_article
        else:
            logging.error(f"Failed to fetch articles. Status code: {response.status_code}, Response: {response.text}")
            return None

    def _download_zip(self) -> io.BytesIO:
        logging.info("Starting the download of the ZIP file.")
        article = self._fetch_article()
        if not article:
            logging.error("Article fetch failed. Exiting download process.")
            return None
        article_details = requests.get(article['url_public_api']).json()
        download_url = article_details['files'][0]['download_url']
        file_name = article_details['files'][0]['name']
        logging.info(f"Downloading file: {file_name}")
        # Attempt to download the file with certificate verification
        try:
            response = requests.get(download_url, stream=True)
        except requests.exceptions.SSLError as e:
            logging.warning("SSL verification failed, retrying without verification.")
            response = requests.get(download_url, stream=True, verify=False)
        file_size = int(response.headers.get('Content-Length', 0))
        logging.info(f"File size: {file_size} bytes")
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
                    logging.debug(f"Downloaded chunk of size: {len(chunk)} bytes")
        buffer.seek(0)  # Reset buffer position to the beginning
        logging.info(f"Download complete. ZIP file '{file_name}' loaded into memory.")
        return buffer

    def _extract_file_from_zip(self, filename: str) -> io.BytesIO:
        with zipfile.ZipFile(self.zip_data, 'r') as zip_ref:
            with zip_ref.open(filename) as file:
                return io.BytesIO(file.read())

    @property
    def samples_csv(self) -> io.BytesIO:
        """
        Extract and load the 'starrydata_samples.csv' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'starrydata_samples.csv'.
        """
        filename = "starrydata_samples.csv"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def papers_json(self) -> io.BytesIO:
        """
        Extract and load the 'all_papers.json' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'all_papers.json'.
        """
        filename = "all_papers.json"
        try:
            file_data = self._extract_file_from_zip(filename)
        except KeyError:
            raise FileNotFoundError(
                "The 'all_papers.json' file was not found. Please note that the dataset format changed on 2024/06/26 "
                "from JSON to CSV. Use the 'papers_csv' property to access the 'starrydata_papers.csv' file instead."
                "https://github.com/starrydata/starrydata_datasets/blob/master/README.md#20240626"
            )
        return file_data

    @property
    def papers_csv(self) -> io.BytesIO:
        """
        Extract and load the 'starrydata_papers.csv' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'starrydata_papers.csv'.
        """
        filename = "starrydata_papers.csv"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def curves_csv(self) -> io.BytesIO:
        """
        Extract and load the 'starrydata_curves.csv' file from the downloaded ZIP file into a pandas DataFrame.

        :return: A pandas DataFrame containing the data from 'starrydata_curves.csv'.
        """
        filename = "starrydata_curves.csv"
        file_data = self._extract_file_from_zip(filename)
        return file_data

    @property
    def dataset_timestamp(self) -> str:
        """
        Extract and return the contents of the 'db_snapshot.txt' file from the downloaded ZIP file as a string.

        :return: A string containing the contents of 'db_snapshot.txt'.
        """
        filename = "db_snapshot.txt"
        file_data = self._extract_file_from_zip(filename)
        return file_data.getvalue().decode('utf-8').strip()

    def _print_dataset_timestamp(self):
        """
        Print the dataset timestamp after downloading the dataset.
        """
        timestamp = self.dataset_timestamp
        print(f"Dataset timestamp: {timestamp}")
