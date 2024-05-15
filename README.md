# starrydata Package

This is a starrydata package.

## Development

### Build

```shell
rm -rf dist
python -m build
```

```shell
python -m twine upload --repository testpypi dist/* -u "__token__" -p $TEST_PYPI_API_TOKEN
```
