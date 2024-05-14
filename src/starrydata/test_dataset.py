import io
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from starrydata.dataset import fetch_latest_dataset, load_dataset, read_dataset, fetch_dataset_by_date


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

    def test_read_dataset_csv(self):
        """Test the read_dataset function with CSV content."""
        csv_content = "column1,column2\nvalue1,value2"
        dataset_type = 'samples'
        df = read_dataset(csv_content, dataset_type)

        expected_df = pd.DataFrame({
            'column1': ['value1'],
            'column2': ['value2']
        })

        pd.testing.assert_frame_equal(df, expected_df)

    def test_load_dataset_success(self):
        """Test the load_dataset function when the file is successfully downloaded and loaded into a DataFrame."""
        with patch('requests.get') as mock_get, \
                patch('io.BytesIO') as mock_bytes_io, \
                patch('zipfile.ZipFile') as mock_zip_file, \
                patch('zipfile.ZipFile.open', create=True) as mock_open, \
                patch('starrydata.dataset.read_dataset') as mock_read_dataset:
            # Setting up the mock to simulate successful file download
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'file content'
            mock_get.return_value = mock_response

            # Mocking zipfile to simulate extracting and reading files
            mock_zip = MagicMock()
            mock_zip_file.return_value.__enter__.return_value = mock_zip
            mock_open.return_value.__enter__.return_value = io.StringIO("column1,column2\nvalue1,value2")

            # Setting up the read_dataset mock
            expected_df = pd.DataFrame({
                'column1': ['value1'],
                'column2': ['value2']
            })
            mock_read_dataset.return_value = expected_df

            df = load_dataset('http://api.example.com/download', 'samples')

            pd.testing.assert_frame_equal(df, expected_df)

    def test_fetch_dataset_by_date_success(self):
        """Test fetching dataset by date successfully returns a DataFrame."""
        with patch('requests.post') as mock_post, \
             patch('requests.get') as mock_get, \
             patch('io.BytesIO') as mock_bytes_io, \
             patch('zipfile.ZipFile') as mock_zip_file, \
             patch('zipfile.ZipFile.open', create=True) as mock_open:
            # Setup mock for POST request
            mock_post_response = MagicMock()
            mock_post_response.status_code = 200
            mock_post_response.json.return_value = [{
                'files': [{'download_url': 'http://api.example.com/download'}]
            }]
            mock_post.return_value = mock_post_response

            # Setup mock for GET request (file download)
            mock_get_response = MagicMock()
            mock_get_response.status_code = 200
            mock_get_response.content = b'file content'
            mock_get.return_value = mock_get_response

            # Mocking zipfile to simulate extracting and reading files
            mock_zip = MagicMock()
            mock_zip_file.return_value.__enter__.return_value = mock_zip
            mock_open.return_value.__enter__.return_value = io.StringIO("data1,data2\nvalue1,value2")

            df = fetch_dataset_by_date('20240510')

            expected_df = pd.DataFrame({
                'data1': ['value1'],
                'data2': ['value2']
            })

            pd.testing.assert_frame_equal(df, expected_df)

    def test_fetch_dataset_by_date(self):
        fetch_dataset_by_date(date="20240505")


if __name__ == '__main__':
    unittest.main()

