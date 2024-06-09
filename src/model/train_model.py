import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
import dagshub
from mlflow.tracking import MlflowClient
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from onnxruntime.quantization import quantize_dynamic, QuantType
from sklearn.model_selection import train_test_split
import joblib
from dotenv import load_dotenv


load_dotenv()
os.environ['DAGSHUB_API_TOKEN'] = os.getenv("DAGSHUB_API_TOKEN")
print(f"DAGSHUB_API_TOKEN: {os.getenv('DAGSHUB_API_TOKEN')}")
dagshub.init("gold-price-prediction", "GrozdaniTanja", mlflow=True)

tracking_uri = mlflow.get_tracking_uri()
print(f"MLflow tracking URI: {tracking_uri}")

experiment_name = "random_forest"
mlflow.set_experiment(experiment_name)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
MODELS_DIR = os.path.join(ROOT_DIR, '..', '..', 'models')
REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')


data_path = os.path.join(DATA_DIR, "current_data.csv")
df = pd.read_csv(data_path)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
df['timestamp'] = df['timestamp'].astype('int64').values.reshape(-1, 1)


X = df.drop(columns='price')
y = df['price']


preprocessor = ColumnTransformer(
    transformers=[
        ('imputer', SimpleImputer(strategy='mean'), [
            'prev_close_price', 'open_price', 'low_price', 'high_price', 'ch', 'chp', 'sentiment_score'
        ])
    ],
    remainder='passthrough'
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)


pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])


def compute_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    mlflow.log_metric('mse', mse)
    mlflow.log_metric('mae', mae)
    mlflow.log_metric('r2', r2)

    with open(os.path.join(REPORTS_DIR, 'metrics.txt'), 'a') as f:
        f.write(f'MSE: {mse}\n')
        f.write(f'MAE: {mae}\n')
        f.write(f'R2: {r2}\n')

    return mse, mae, r2


def get_production_model(model_name):
    client = mlflow.tracking.MlflowClient()
    find_model = f"name='{model_name}'"
    results = client.search_model_versions(find_model)
    for version in results:
        if version.current_stage == 'Production':
            print(f"Found production model: Version {version.version}")
            run_id = version.run_id
            metrics = client.get_run(run_id).data.metrics
            print(f"Metrics for run_id {run_id}: {metrics}")
            return metrics
    return None


def transition_model_version_stage(model_name, model_version, stage):
    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=model_version,
        stage=stage
    )


with mlflow.start_run() as run:
    try:
        mlflow.set_tag("mlflow.runName", "run_" +
                       pd.Timestamp.now().strftime("%Y%m%d_%H%M%S"))

        mlflow.log_param("experiment_name", experiment_name)
        mlflow.log_params({"n_estimators": 100,
                           "random_state": 42})

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        new_mse, new_mae, new_r2 = compute_metrics(y_test, y_pred)

        model_info = mlflow.sklearn.log_model(pipeline, "model")

        print(f"Model logged in run {run.info.run_id}")

        model_name = "gold_price_prediction_model"

        model_version = mlflow.register_model(
            model_uri=model_info.model_uri, name=model_name)

        print(
            f"Model registered as {model_name} with version {model_version.version}")

        production_model = get_production_model(model_name)
        print(f"Production model: {production_model}")

        if production_model is None:
            print("No production model found. Transitioning new model to production.")
            transition_model_version_stage(
                model_name, model_version.version, 'Production')
        else:
            production_mse = production_model.get('mse')
            production_mae = production_model.get('mae')
            production_r2 = production_model.get('r2')
            if production_mse is not None and production_mae is not None and production_r2 is not None:
                if new_mse < production_mse and new_r2 > production_r2 and new_mae < production_mae:
                    print(
                        f"New model {model_version.version}  is better than the production model. Transitioning the new model to Production.")
                    transition_model_version_stage(
                        model_name, model_version.version, 'Production')
                else:
                    print(
                        f"New model {model_version.version} is not better than the production model. Keeping the current production model.")
            else:
                print(
                    "Production model metrics are incomplete. Cannot compare with the new model.")

        # Localy save the model
        model_path = os.path.join(
            MODELS_DIR, "gold_price_prediction_model.pkl")
        with open(model_path, 'wb') as f:
            joblib.dump(pipeline, f)

        print(f"Model saved as {model_path}")

        # Convert the pipeline to ONNX format
        input_column_names = X_train.columns.tolist()
        initial_type = [(input_column_names[i], FloatTensorType([None, 1]))
                        for i in range(len(input_column_names))]
        onnx_model = convert_sklearn(pipeline, initial_types=initial_type)
        onnx_model_path = os.path.join(
            MODELS_DIR, "gold_price_prediction_model.onnx")
        with open(onnx_model_path, "wb") as f:
            f.write(onnx_model.SerializeToString())

        print(f"Model converted to ONNX and saved as {onnx_model_path}")

        # Apply dynamic quantization
        quantized_model_path = os.path.join(
            MODELS_DIR, "gold_price_prediction_model.quant.onnx")
        quantize_dynamic(onnx_model_path, quantized_model_path,
                         weight_type=QuantType.QUInt8)

        # Log the ONNX models as artifacts in MLflow
        mlflow.log_artifact(onnx_model_path, "onnx_models")
        mlflow.log_artifact(quantized_model_path, "quantized_models")

        # Register the quantized model with the correct URI
        quantized_model_info = mlflow.register_model(
            model_uri=f"runs:/{run.info.run_id}/quantized_models/quantized_model.onnx", name=f"{model_name}_quantized")

        # Handle quantized model transition based on non-quantized model transition
        if production_model is None:
            print(
                "No production quantized model found. Transitioning new quantized model to production.")
            transition_model_version_stage(
                f"{model_name}_quantized", quantized_model_info.version, 'Production')
        else:
            if new_mse < production_mse and new_r2 > production_r2 and new_mae < production_mae:
                print(
                    f"New quantized model {quantized_model_info.version} is better than the production model. Transitioning the new quantized model to Production.")
                transition_model_version_stage(
                    f"{model_name}_quantized", quantized_model_info.version, 'Production')
            else:
                print(
                    f"New quantized model {quantized_model_info.version} is not better than the production model. Keeping the current production quantized model.")

    except Exception as e:
        print(f"An error occurred: {e}")
        mlflow.end_run(status='FAILED')
    else:
        mlflow.end_run(status='FINISHED')
