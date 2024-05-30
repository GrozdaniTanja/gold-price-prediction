import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MERGED_DATA_DIR = os.path.join(DATA_DIR, "merged")

os.makedirs(MERGED_DATA_DIR, exist_ok=True)


def aggregate_sentiment(sentiment_file):
    sentiment_df = pd.read_csv(sentiment_file)
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date

    aggregated_sentiment_df = sentiment_df.groupby(
        'date')['sentiment_score'].mean().reset_index()
    return aggregated_sentiment_df


def merge_data(price_file, aggregated_sentiment_df, output_file):
    price_df = pd.read_csv(price_file)
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp']).dt.date

    merged_df = pd.merge(price_df, aggregated_sentiment_df,
                         how='left', left_on='timestamp', right_on='date').fillna(0)

    merged_df.drop(columns=['date'], inplace=True)

    mode = 'a' if os.path.exists(output_file) else 'w'
    merged_df.to_csv(output_file, mode=mode, index=False,
                     header=not os.path.exists(output_file))
    print(f"Merged data saved to {output_file}")


if __name__ == "__main__":
    currency = "EUR"

    # Define file paths
    price_file = os.path.join(
        PROCESSED_DATA_DIR, f"{currency}-processed-gold-price-data.csv")
    sentiment_file = os.path.join(RAW_DATA_DIR, "aggregated_sentiments.csv")
    output_file = os.path.join(
        MERGED_DATA_DIR, f"{currency}-merged-gold-price-data.csv")

    # Aggregate sentiment data
    aggregated_sentiment_df = aggregate_sentiment(sentiment_file)

    # Perform the data merge
    merge_data(price_file, aggregated_sentiment_df, output_file)
