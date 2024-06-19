# __init__.py
from .dataset import Dataset


def load_dataset(date=None, zip_path=None):
    return Dataset(date=date, zip_path=zip_path)


__all__ = ['load_dataset']
