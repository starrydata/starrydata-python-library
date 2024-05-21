# __init__.py
from .dataset import Dataset

def load_dataset(date):
    return Dataset(date)

__all__ = ['load_dataset']
