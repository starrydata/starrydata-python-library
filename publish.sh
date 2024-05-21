#!/bin/bash

# Function to show usage
usage() {
    echo "Usage: $0 [patch|minor|major] [--test]"
    exit 1
}

# Check version argument
if [ "$1" == "patch" ] || [ "$1" == "minor" ] || [ "$1" == "major" ]; then
    VERSION=$1
else
    usage
fi

# Check for test option
if [ "$2" == "--test" ]; then
    REPOSITORY="testpypi"
    API_TOKEN=$TEST_PYPI_API_TOKEN
else
    REPOSITORY="pypi"
    API_TOKEN=$PROD_PYPI_API_TOKEN
fi

# Check if Git working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Git working directory is not clean. Please commit or stash your changes."
    exit 1
fi

# Update version
bumpversion $VERSION

# Clean up the build directory
rm -rf dist

# Build the package
python -m build

# Upload to the specified repository
python -m twine upload --repository $REPOSITORY dist/* -u "__token__" -p $API_TOKEN
