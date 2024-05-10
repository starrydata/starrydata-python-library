import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from starrykit.dataset import fetch_latest_dataset, load_dataset


class TestDatasetFunctions(unittest.TestCase):

    def test_fetch_latest_dataset_success(self):
        """Test the fetch_latest_dataset function when API responses are successful."""
        with patch('requests.get') as mock_get:
            # Setting up the mock to return a successful response
            mock_articles_response = MagicMock()
            mock_articles_response.status_code = 200
            mock_articles_response.json.return_value = [{
                'published_date': '2020-01-01',
                'url_public_api': 'http://api.example.com/public_api'
            }]

            mock_article_response = MagicMock()
            mock_article_response.status_code = 200
            mock_article_response.json.return_value = {
                'published_date': '2020-01-01T00:00:00Z',
                'files': [{'download_url': 'http://api.example.com/download'}]
            }

            mock_get.side_effect = [mock_articles_response, mock_article_response]

            expected_url = 'http://api.example.com/download'
            expected_date = '20200101'
            url, date = fetch_latest_dataset()

            self.assertEqual(url, expected_url)
            self.assertEqual(date, expected_date)

    def test_load_dataset_success(self):
        """Test the load_dataset function when the file is successfully downloaded and loaded into a DataFrame."""
        with patch('requests.get') as mock_get, \
             patch('io.BytesIO') as mock_bytes_io, \
             patch('zipfile.ZipFile') as mock_zip_file, \
             patch('pandas.read_csv') as mock_read_csv:
            # Setting up the mock to return a successful response
            mock_articles_response = MagicMock()
            mock_articles_response.status_code = 200
            mock_articles_response.json.return_value = [{
                'published_date': '2020-01-01',
                'url_public_api': 'http://api.example.com/public_api'
            }]

            mock_article_response = MagicMock()
            mock_article_response.status_code = 200
            mock_article_response.json.return_value = {
                'published_date': '2020-01-01T00:00:00Z',
                'files': [{'download_url': 'http://api.example.com/download'}]
            }

            # Mocking requests.get to simulate successful file download
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'file content'

            mock_get.side_effect = [mock_articles_response, mock_article_response, mock_response]

            # Mocking zipfile to simulate extracting and reading files
            mock_zip = MagicMock()
            mock_zip_file.return_value.__enter__.return_value = mock_zip
            mock_zip.open.return_value.__enter__.return_value = 'file content'

            # Setting up pandas to return a DataFrame
            mock_read_csv.return_value = pd.DataFrame({"data": [1, 2, 3]})

            df = load_dataset(dataset_type='samples')

            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df['data'].tolist(), [1, 2, 3])

    # さらにエラーケースや他の関数のテストも追加できます。

if __name__ == '__main__':
    unittest.main()
