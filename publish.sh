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
if ! bumpversion $VERSION; then
    echo "Error: bumpversion failed."
    exit 1
fi

# Clean up the build directory
if ! rm -rf dist; then
    echo "Error: Failed to clean up the build directory."
    exit 1
fi

# Build the package
if ! python -m build; then
    echo "Error: Build failed."
    exit 1
fi

# Upload to the specified repository
if ! python -m twine upload --repository $REPOSITORY dist/* -u "__token__" -p $API_TOKEN; then
    echo "Error: Failed to upload the package."
    exit 1
fi

# Push changes to Git
if ! git push origin main; then
    echo "Error: Failed to push changes to Git."
    exit 1
fi

echo "All steps completed successfully."
