# Maintainer Deployment Guide for starrydata Package

This guide outlines the steps for version management, building, and deploying the `starrydata` package to both the PyPI Test and Production repositories using automated scripts.

## Prerequisites

- Python 3.9 or higher
- `bumpversion` for version management
- `build` for building the package
- `twine` for uploading the package to PyPI

## Installation of Required Tools

First, ensure you have the necessary tools installed:

```sh
pip install bumpversion build twine
```

## Automated Deployment Script

## Usage

To deploy a new version of the `starrydata` package, run the `publish.sh` script with the appropriate version bump argument and optionally specify `--test` to deploy to the PyPI Test repository:

- For a patch version update (e.g., 0.0.8 → 0.0.9):

  ```sh
  ./publish.sh patch
  ```

- For a minor version update (e.g., 0.0.8 → 0.1.0):

  ```sh
  ./publish.sh minor
  ```

- For a major version update (e.g., 0.0.8 → 1.0.0):

  ```sh
  ./publish.sh major
  ```

To deploy to the PyPI Test repository, add the `--test` flag:

  ```sh
  ./publish.sh patch --test
  ```

This script will:

1. Update the version using `bumpversion` and commit the changes.
2. Clean the `dist` directory.
3. Build the package using `python -m build`.
4. Upload the built package to the specified PyPI repository (Test or Production) using `twine`.

## Installation

You can install Starrydata from PyPI using the following command:

```sh
pip install starrydata
```

If you want to install from the PyPI test repository for testing purposes, use the following command:

```sh
pip install --index-url https://test.pypi.org/simple/ --no-deps starrydata
```

## Notes

- Ensure that your `TEST_PYPI_API_TOKEN` and `PYPI_API_TOKEN` environment variables are set with your Test PyPI and Production PyPI API tokens, respectively.
- The `.bumpversion.cfg` file should be adjusted if additional files or specific configurations are needed.

By following this guide, maintainers can streamline the deployment process of the `starrydata` package, making it more efficient and less error-prone.
