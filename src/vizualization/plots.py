import os
import matplotlib.pyplot as plt
import pandas as pd
import joblib
from datetime import datetime, timedelta
import numpy as np

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'visualization')
MODELS_DIR = os.path.join(ROOT_DIR, '..', '..', 'models')
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data', 'merged')
os.makedirs(PLOTS_DIR, exist_ok=True)

currency = "EUR"
data_file = os.path.join(DATA_DIR, f'{currency}-merged-gold-price-data.csv')
model_file = os.path.join(
    MODELS_DIR, f"{currency}_linear_regression_model.pkl")


def plot_gold_price(data_file):
    df = pd.read_csv(data_file)
    print(df.head())  # Print first few rows of the DataFrame
    print(df.columns)  # Print column names
    if 'timestamp' not in df.columns:
        print("Error: 'timestamp' column not found in the DataFrame.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    plt.figure(figsize=(16, 10))  # Increase image size
    plt.plot(df['timestamp'], df['price'], marker='o', linestyle='-')
    plt.title('Gold Price Over Time')
    plt.xlabel('Date and Time')
    plt.ylabel('Gold Price')
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(
        '%Y-%m-%d %H:%M:%S'))  # Include hours in x-axis labels
    plt.tight_layout()

    plot_filename = os.path.join(PLOTS_DIR, 'gold_price_over_time.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f"Plot saved: {plot_filename}")


def plot_predictions(data_file, model_file, currency):
    df = pd.read_csv(data_file)
    if 'timestamp' not in df.columns:
        print("Error: 'timestamp' column not found in the DataFrame.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').rename(
        columns={'timestamp': 'ds', 'price': 'y'})
    df['ds'] = df['ds'].map(pd.Timestamp.toordinal)

    with open(model_file, 'rb') as f:
        model = joblib.load(f)

    # Prepare features for prediction
    X_other = df[['prev_close_price', 'open_price',
                  'low_price', 'high_price', 'ch', 'chp', 'sentiment_score']]
    time = df['ds'].values.reshape(-1, 1)
    X = np.concatenate((time, X_other), axis=1)

    # Future prediction
    future_dates = pd.date_range(
        start=df['timestamp'].iloc[-1], periods=30, freq='D').map(pd.Timestamp.toordinal)
    future_dates_df = pd.DataFrame({'ds': future_dates, 'prev_close_price': df['prev_close_price'].iloc[-1],
                                    'open_price': df['open_price'].iloc[-1],
                                    'low_price': df['low_price'].iloc[-1],
                                    'high_price': df['high_price'].iloc[-1],
                                    'ch': df['ch'].iloc[-1],
                                    'chp': df['chp'].iloc[-1],
                                    'sentiment_score': df['sentiment_score'].iloc[-1]})
    future_dates_df['ds'] = future_dates_df['ds'].map(pd.Timestamp.toordinal)
    future_pred = model.predict(future_dates_df)

    # Prepare actual and predicted data for plotting
    actual_dates = pd.to_datetime(df['ds'].map(datetime.fromordinal))
    future_dates = pd.to_datetime(
        future_dates_df['ds'].map(datetime.fromordinal))

    plt.figure(figsize=(10, 6))
    plt.plot(actual_dates, df['y'],
             label='Actual Data', marker='o', linestyle='-')
    plt.plot(actual_dates, model.predict(X),
             label='Predicted Data', linestyle='--')
    plt.plot(future_dates, future_pred, label='Future Prediction',
             linestyle='--', color='green')
    plt.title(f'Gold Price Prediction vs Actual Data ({currency})')
    plt.xlabel('Date')
    plt.ylabel('Gold Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_filename = os.path.join(
        PLOTS_DIR, f'{currency}_price_prediction_vs_actual.png')
    plt.savefig(plot_filename)
    plt.close()

    # Plot comparison between actual and predicted data
    plt.figure(figsize=(10, 6))
    plt.plot(actual_dates, df['y'],
             label='Actual Data', marker='o', linestyle='-')
    plt.plot(actual_dates, model.predict(X),
             label='Predicted Data', linestyle='--')
    plt.title(
        f'Gold Price Prediction Comparison with Actual Data ({currency})')
    plt.xlabel('Date')
    plt.ylabel('Gold Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    comparison_plot_filename = os.path.join(
        PLOTS_DIR, f'{currency}_price_prediction_comparison.png')
    plt.savefig(comparison_plot_filename)
    plt.close()

    print(f"Plots saved: {plot_filename}, {comparison_plot_filename}")


if __name__ == "__main__":
    plot_gold_price(data_file)
    plot_predictions(data_file, model_file, currency)
