from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data', 'processed')
MODELS_DIR = os.path.join(ROOT_DIR, '..', '..', 'models')
SENTIMENTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'data', 'raw')
currency = "EUR"


def load_model():
    model_path = f"{MODELS_DIR}/{currency}_linear_regression_model.pkl"
    with open(model_path, 'rb') as f:
        model = joblib.load(f)
    return model


def load_sentiments():
    sentiment_path = os.path.join(SENTIMENTS_DIR, "aggregated_sentiments.csv")
    sentiment_df = pd.read_csv(sentiment_path)
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date
    return sentiment_df


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        days = int(data['days'])
        model = load_model()
        sentiments = load_sentiments()

        last_date = pd.to_datetime('today').date()
        future_dates = [last_date + timedelta(days=i)
                        for i in range(1, days + 1)]
        future_timestamps = np.array(
            [pd.Timestamp(date).value for date in future_dates]).reshape(-1, 1)

        # Load recent data from processed file for feature replication
        sample_df = pd.read_csv(os.path.join(
            DATA_DIR, f'{currency}-processed-gold-price-data.csv'))
        recent_data = sample_df.tail(1)
        dummy_features = np.repeat(recent_data[[
                                   'prev_close_price', 'open_price', 'low_price', 'high_price', 'ch', 'chp']].values, days, axis=0)

        # Extract sentiment scores for future dates
        sentiment_scores = []
        for date in future_dates:
            score = sentiments[sentiments['date']
                               == date]['sentiment_score'].values
            if score.size > 0:
                sentiment_scores.append(score[0])
            else:
                # or use another default value or method
                sentiment_scores.append(0)

        sentiment_scores = np.array(sentiment_scores).reshape(-1, 1)

        X_future = np.concatenate(
            (future_timestamps, dummy_features, sentiment_scores), axis=1)

        predictions = model.predict(X_future)
        return jsonify({'predictions': predictions.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
