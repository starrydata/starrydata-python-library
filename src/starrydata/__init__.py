# __init__.py
from .dataset import Dataset

def load_dataset(date=None):
    if date:
        return Dataset(date=date)
    else:
        return Dataset()

__all__ = ['load_dataset']
