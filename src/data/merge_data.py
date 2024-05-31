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


def get_existing_merged_data(output_file):
    if not os.path.exists(output_file):
        return None
    merged_df = pd.read_csv(output_file)
    merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
    return merged_df


def merge_data(price_file, aggregated_sentiment_df, output_file):
    price_df = pd.read_csv(price_file)
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])

    existing_merged_df = get_existing_merged_data(output_file)

    if existing_merged_df is not None:
        existing_dates = existing_merged_df['timestamp'].dt.date.unique()
        new_price_df = price_df[~price_df['timestamp'].dt.date.isin(
            existing_dates)]

        updated_price_df = price_df[price_df['timestamp'].dt.date.isin(
            existing_dates)]
        updated_sentiment_df = aggregated_sentiment_df[aggregated_sentiment_df['date'].isin(
            updated_price_df['timestamp'].dt.date)]

        updated_df = pd.merge(updated_price_df, updated_sentiment_df,
                              how='left', left_on=updated_price_df['timestamp'].dt.date, right_on='date').fillna(0)

        existing_merged_df = existing_merged_df[~existing_merged_df['timestamp'].dt.date.isin(
            updated_price_df['timestamp'].dt.date)]
    else:
        new_price_df = price_df
        updated_df = pd.DataFrame()

    if new_price_df.empty and updated_df.empty:
        print("No new data to merge.")
        return

    merged_df = pd.merge(new_price_df, aggregated_sentiment_df,
                         how='left', left_on=new_price_df['timestamp'].dt.date, right_on='date').fillna(0)

    if not updated_df.empty:
        updated_df.drop(columns=['date'], inplace=True)
        merged_df = pd.concat(
            [existing_merged_df, merged_df, updated_df], ignore_index=True)
    else:
        merged_df = pd.concat(
            [existing_merged_df, merged_df], ignore_index=True)

    merged_df.drop(columns=['date'], inplace=True)

    merged_df['timestamp'] = merged_df['timestamp'].dt.strftime(
        '%Y-%m-%d %H:%M:%S')

    merged_df.to_csv(output_file, index=False)
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
