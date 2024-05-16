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

# Update version
bumpversion $VERSION

# Clean up the build directory
rm -rf dist

# Build the package
python -m build

# Upload to the specified repository
python -m twine upload --repository $REPOSITORY dist/* -u "__token__" -p $API_TOKEN
