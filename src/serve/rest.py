from flask import Flask, request, jsonify, send_file
import joblib
import numpy as np
import mlflow
from mlflow.tracking import MlflowClient
import onnxruntime as rt
import dagshub
import os
import pandas as pd
from datetime import datetime, timedelta
import json
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load environment variables from .env file
load_dotenv()

# Fetch DAGSHUB_API_TOKEN from environment
dagshub_api_token = os.getenv("DAGSHUB_API_TOKEN")
if not dagshub_api_token:
    raise EnvironmentError(
        "DAGSHUB_API_TOKEN not found in environment variables.")

# Debugging: Print the token to ensure it is being read correctly
print(f"Read DAGSHUB_API_TOKEN: {dagshub_api_token}")

# Remove any leading or trailing whitespace
dagshub_api_token = dagshub_api_token.strip()

try:
    dagshub.auth.add_app_token(dagshub_api_token)
    print("Successfully added DagsHub API token.")
except Exception as e:
    print(f"Error adding DagsHub API token: {e}")
    raise

dagshub.init("gold-price-prediction", "GrozdaniTanja", mlflow=True)
tracking_uri = mlflow.get_tracking_uri()
print(f"MLflow tracking URI: {tracking_uri}")

experiment_name = "random_forest"
model_name = "gold_price_prediction_model_quantized"
mlflow.set_experiment(experiment_name)
client = MlflowClient()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')
TESTING_REPORT = os.path.join(REPORTS_DIR, 'test_results.json')
VALIDATION_REPORT = os.path.join(REPORTS_DIR, 'validation_report.txt')


def get_production_model(model_name):
    client = mlflow.tracking.MlflowClient()
    find_model = f"name='{model_name}'"
    results = client.search_model_versions(find_model)
    for version in results:
        if version.current_stage == 'Production':
            local_dir = "/app/models/"
            client.download_artifacts(version.run_id, "model", local_dir)
            local_path = os.path.join(
                local_dir, "gold_price_prediction_model.quant.onnx")
            return local_path
    return None


def time_to_int(dt):
    return np.int64(dt.timestamp() * 1e9)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        days = data['days']

        # Load recent data from processed file for feature replication
        sample_df = pd.read_csv(os.path.join(DATA_DIR, 'current_data.csv'))
        recent_data = sample_df.tail(1).iloc[0]

        # Use recent data as default values
        prev_close_price = data.get(
            'prev_close_price', recent_data['prev_close_price'])
        open_price = data.get('open_price', recent_data['open_price'])
        low_price = data.get('low_price', recent_data['low_price'])
        high_price = data.get('high_price', recent_data['high_price'])
        ch = data.get('ch', recent_data['ch'])
        chp = data.get('chp', recent_data['chp'])
        sentiment_score = data.get(
            'sentiment_score', recent_data['sentiment_score'])

        # Generate future dates
        future_dates = [datetime.now() + timedelta(days=i)
                        for i in range(days)]

        # Create dataframe for predictions
        predict_request = pd.DataFrame({
            'timestamp': future_dates,
            'prev_close_price': [prev_close_price] * days,
            'open_price': [open_price] * days,
            'low_price': [low_price] * days,
            'high_price': [high_price] * days,
            'ch': [ch] * days,
            'chp': [chp] * days,
            'sentiment_score': [sentiment_score] * days
        })

        # Convert timestamp to int
        predict_request['timestamp'] = predict_request['timestamp'].apply(
            time_to_int)

        # Convert each column to a numpy array and store in a dictionary
        input_data = {col: predict_request[col].values.reshape(
            -1, 1).astype(np.float32) for col in predict_request.columns}

        model_name = "gold_price_prediction_model_quantized"
        model_path = get_production_model(model_name)

        if model_path is None:
            return jsonify({'error': 'No production model found'}), 500

        sess = rt.InferenceSession(model_path)
        input_names = [input.name for input in sess.get_inputs()]
        input_feed = {input_name: input_data[input_name]
                      for input_name in input_names}
        label_name = sess.get_outputs()[0].name
        prediction = sess.run([label_name], input_feed)[0]

        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/latest-models', methods=['GET'])
def get_model_production():
    try:
        stage = request.args.get('stage', 'Production')
        models = client.get_latest_versions(model_name, stages=[stage])
        model_info = [{'name': m.name, 'version': m.version,
                       'run_id': m.run_id, 'current_stage': m.current_stage} for m in models]
        return jsonify(model_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/models', methods=['GET'])
def get_models_all():
    try:
        stage = request.args.get('stage', None)
        if stage:
            models = client.search_model_versions(
                f"name='{model_name}' and current_stage='{stage}'")
        else:
            models = client.search_model_versions(f"name='{model_name}'")

        model_info = [{'name': m.name, 'version': m.version,
                       'run_id': m.run_id, 'current_stage': m.current_stage} for m in models]
        return jsonify(model_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/experiments', methods=['GET'])
def get_experiments():
    try:
        experiments = client.search_experiments()
        experiment_info = [{'experiment_id': exp.experiment_id, 'name': exp.name,
                            'artifact_location': exp.artifact_location, 'lifecycle_stage': exp.lifecycle_stage} for exp in experiments]
        return jsonify(experiment_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/runs', methods=['GET'])
def get_runs():
    experiment_id = request.args.get('experiment_id', None)
    try:
        if experiment_id:
            runs = mlflow.search_runs(experiment_ids=[experiment_id])
        else:
            runs = mlflow.search_runs(search_all_experiments=True)
        runs_info = runs.to_dict(orient='records')

        # Replace NaN values with None
        def replace_nan_with_none(obj):
            if isinstance(obj, list):
                return [replace_nan_with_none(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: replace_nan_with_none(value) for key, value in obj.items()}
            elif isinstance(obj, float) and np.isnan(obj):
                return None
            else:
                return obj

        runs_info = replace_nan_with_none(runs_info)
        print(f"Runs info: {runs_info}")  # Ensure this prints an array
        # This should automatically set Content-Type to application/json
        return jsonify(runs_info)
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return jsonify([])  # Ensure an empty array is returned on error


@app.route('/change_model_stage', methods=['POST'])
def change_model_stage():
    try:
        data = request.get_json()
        model_name = data['model_name']
        version = data['version']
        new_stage = data['new_stage']

        client.transition_model_version_stage(
            name=model_name, version=version, stage=new_stage)
        return jsonify({'message': f'Model {model_name} version {version} transitioned to {new_stage} stage successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/testing', methods=['GET'])
def get_results():
    try:
        if os.path.exists(TESTING_REPORT) and os.stat(TESTING_REPORT).st_size != 0:
            with open(TESTING_REPORT, 'r') as f:
                results = json.load(f)
            return jsonify(results)
        else:
            return jsonify({'error': 'No results available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/validation', methods=['GET'])
def get_validation_results():
    try:
        if os.path.exists(VALIDATION_REPORT):
            return send_file(VALIDATION_REPORT, as_attachment=True)
        else:
            return jsonify({'error': 'Validation results not found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
