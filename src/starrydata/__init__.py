# __init__.py
from .dataset import Dataset

def load_dataset(date=None, zip_path=None):
    if date or zip_path:
        return Dataset(date=date, zip_path=zip_path)
    else:
        return Dataset()

__all__ = ['load_dataset']
