import os
import glob
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import numpy as np

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data', 'merged')
MODELS_DIR = os.path.join(ROOT_DIR, '..', '..', 'models')
REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

currency = "EUR"

data_files = glob.glob(os.path.join(
    DATA_DIR, f'{currency}-merged-gold-price-data.csv'))


def process_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    return df


def train_linear_regression_model(df):
    time = df['timestamp'].astype('int64').values.reshape(-1, 1)
    X_other = df[['prev_close_price', 'open_price', 'low_price',
                  'high_price', 'ch', 'chp', 'sentiment_score']]
    X = np.concatenate((time, X_other), axis=1)
    y = df['price'].values

    model = LinearRegression()
    model.fit(X, y)
    return model


def compute_metrics(y_true, y_pred, split_name):
    mse = mean_squared_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    r_squared = r2_score(y_true, y_pred)

    with open(os.path.join(REPORTS_DIR, f'{split_name}_metrics.txt'), 'a') as f:
        f.write(f'Linear Regression {split_name} MSE for {currency}: {mse}\n')
        f.write(
            f'Linear Regression {split_name} MAPE for {currency}: {mape}\n')
        f.write(
            f'Linear Regression {split_name} R-squared for {currency}: {r_squared}\n')


def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


if __name__ == "__main__":
    for file_path in data_files:
        df = process_data(file_path)

        if df.isnull().sum().sum() > 0:
            df.fillna(method='ffill', inplace=True)
            df.fillna(method='bfill', inplace=True)

        train_size = int(len(df) * 0.8)
        train_df = df[:train_size]
        test_df = df[train_size:]

        model = train_linear_regression_model(train_df)

        time_train = train_df['timestamp'].astype(
            'int64').values.reshape(-1, 1)
        X_train = np.concatenate((time_train, train_df[[
                                 'prev_close_price', 'open_price', 'low_price', 'high_price', 'ch', 'chp', 'sentiment_score']].values), axis=1)
        time_test = test_df['timestamp'].astype('int64').values.reshape(-1, 1)
        X_test = np.concatenate((time_test, test_df[[
                                'prev_close_price', 'open_price', 'low_price', 'high_price', 'ch', 'chp', 'sentiment_score']].values), axis=1)

        train_pred = model.predict(X_train)
        compute_metrics(train_df['price'], train_pred, 'train')

        test_pred = model.predict(X_test)
        compute_metrics(test_df['price'], test_pred, 'test')

        model_path = os.path.join(
            MODELS_DIR, f"{currency}_linear_regression_model.pkl")
        with open(model_path, 'wb') as f:
            joblib.dump(model, f)

    print("Linear regression models trained and saved successfully.")
