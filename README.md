# Starrydata

Starrydata is a library that allows users to easily download and utilize datasets related to inorganic materials. This library enables efficient data retrieval for research and projects.

## Installation

You can install Starrydata from PyPI using the following command:

```sh
pip install starrydata
```

## Usage

Below is an example of how to use Starrydata.

### Downloading a Dataset

To download a specific dataset, use the `Dataset` class. Here is an example of how to download and load a dataset into a pandas DataFrame:

```python
import starrydata as sd  # Import the Starrydata library
import pandas as pd  # Import the pandas library

# Load the dataset for the specified date
sd_dataset = sd.load_dataset(date="20240521")

# Print the dataset timestamp to confirm the download date
print(sd_dataset.dataset_timestamp)

# Read the 'all_curves.csv' file from the dataset and convert it to a pandas DataFrame
df_curves = pd.read_csv(sd_dataset.curves_csv)

# Read the 'all_samples.csv' file from the dataset and convert it to a pandas DataFrame
df_samples = pd.read_csv(sd_dataset.samples_csv)

# Read the 'all_papers.json' file from the dataset and convert it to a pandas DataFrame
df_papers = pd.read_json(sd_dataset.papers_json)
```

More details is [1_how_to_use.ipynb](https://github.com/starrydata/starrydata-python-library/blob/main/example_notebooks/1_how_to_use.ipynb)

## Documentation

For more detailed documentation and usage examples, please refer to the [official documentation](https://pypi.org/project/starrydata/).

## Contributing

Bug reports and feature requests are welcome at the [GitHub repository](https://github.com/starrydata/starrydata-python-library/). Contributions to the codebase are also appreciated. Follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push the branch (`git push origin feature-branch`)
5. Create a pull request

## License

This project is licensed under the MIT License. See the [LICENSE file](https://github.com/starrydata/starrydata-python-library?tab=MIT-1-ov-file#readme) for more details.

