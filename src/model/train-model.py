import os
import glob
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data', 'processed')
MODELS_DIR = os.path.join(ROOT_DIR, '..', '..', 'models')
REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

data_files = glob.glob(os.path.join(
    DATA_DIR, '*-processed-gold-price-data.csv'))


def get_currency(file_path):
    base_name = os.path.basename(file_path)
    return base_name.split('-')[0]


def process_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').rename(
        columns={'timestamp': 'ds', 'price': 'y'})

    # Check and handle null values
    if df.isnull().sum().sum() > 0:
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

    return df[['ds', 'y']]


def train_and_save_model(df, currency):
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    model_path = os.path.join(MODELS_DIR, f"{currency}_prophet_model.pkl")
    with open(model_path, 'wb') as f:
        joblib.dump(model, f)

    return model


def compute_metrics(y_true, y_pred, split_name, currency):
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MSE': mean_squared_error(y_true, y_pred)
    }

    with open(os.path.join(REPORTS_DIR, f'{split_name}_metrics.txt'), 'a') as f:
        for metric_name, metric_value in metrics.items():
            f.write(
                f'Prophet {split_name} {metric_name} for {currency}: {metric_value}\n')


for file_path in data_files:
    df = process_data(file_path)

    currency = get_currency(file_path)
    model = train_and_save_model(df, currency)

    # Split data for evaluation
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    test_df = df[train_size:]

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # Compute metrics
    train_pred = forecast.loc[:train_size-1, 'yhat']
    test_pred = forecast.loc[train_size:, 'yhat']

    compute_metrics(train_df['y'], train_pred, 'train', currency)
    compute_metrics(test_df['y'], test_pred, 'test', currency)

print("Models trained and saved successfully with Prophet.")
