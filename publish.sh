#!/bin/bash

# Update version
if [ "$1" == "patch" ] || [ "$1" == "minor" ] || [ "$1" == "major" ]; then
    bumpversion $1
else
    echo "Usage: $0 [patch|minor|major]"
    exit 1
fi

# Clean up the build directory
rm -rf dist

# Build the package
python -m build

# Upload to PyPI Test repository
python -m twine upload --repository testpypi dist/* -u "__token__" -p $TEST_PYPI_API_TOKEN
