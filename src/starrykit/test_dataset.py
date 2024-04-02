from dataset import load_latest_dataset


def test_load_latest_dataset():
    df = load_latest_dataset()
    if df is not None:
        print("Dataset loaded successfully.")
        print(df.head())  # Print the first few rows of the DataFrame
    else:
        print("Failed to load the dataset.")

if __name__ == "__main__":
    test_load_latest_dataset()