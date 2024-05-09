from dataset import load_dataset


def test_load_dataset():
    df = load_dataset(dataset_type="papers")
    if df is not None:
        print("Dataset loaded successfully.")
        print(df.head())  # Print the first few rows of the DataFrame
    else:
        print("Failed to load the dataset.")


def test_load_curve_dataset():
    df = load_dataset(dataset_type="curves")
    if df is not None:
        print("Dataset loaded successfully.")
        print(df.head())  # Print the first few rows of the DataFrame
    else:
        print("Failed to load the dataset.")

if __name__ == "__main__":
    # test_load_dataset()
    test_load_curve_dataset()