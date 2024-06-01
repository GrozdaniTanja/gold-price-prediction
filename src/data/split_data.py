import pandas as pd


def main():
    current_data = pd.read_csv("data/current_data.csv")

    test_size = int(0.1 * len(current_data))

    test_data = current_data.head(test_size)
    train_data = current_data.iloc[test_size:]

    test_data.to_csv("data/test.csv", index=False)
    train_data.to_csv("data/train.csv", index=False)


if __name__ == "__main__":
    main()