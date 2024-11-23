# import pandas as pd
# import numpy as np
# import mlflow
# import time
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import classification_report, accuracy_score
# from sklearn.compose import ColumnTransformer
# from sklearn.impute import SimpleImputer
# import boto3
# import os
# from io import StringIO

# def load_data():
#     bucket_name = os.getenv('BUCKET_NAME')
#     file_key = os.getenv('FILE_KEY')

#     # Create an S3 client
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
#     )

#     # Read the CSV file from S3
#     response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
#     csv_content = response['Body'].read().decode('utf-8')
    
#     # Load into a pandas DataFrame
#     return pd.read_csv(StringIO(csv_content))

# # Preprocess data
# def preprocess_data(df):
#     # Create 'distance_to_merchant' as an example feature
#     df['distance_to_merchant'] = np.sqrt((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)
#     df['trans_dayofweek'] = pd.to_datetime(df['trans_date_trans_time']).dt.dayofweek
#     df['trans_hour'] = pd.to_datetime(df['trans_date_trans_time']).dt.hour
    
#     features = ['amt', 'distance_to_merchant', 'city_pop', 'trans_dayofweek', 'trans_hour']
#     X = df[features]
#     y = df['is_fraud']
#     return train_test_split(X, y, test_size=0.2, random_state=42)

# # Create the pipeline
# def create_pipeline():
#     return Pipeline(steps=[
#         ("scaler", StandardScaler()),
#         ("classifier", RandomForestClassifier(random_state=42))
#     ])

# # Train model
# def train_model(pipe, X_train, y_train, param_grid, cv=2, n_jobs=-1, verbose=3):
#     model = GridSearchCV(pipe, param_grid, cv=cv, n_jobs=n_jobs, verbose=verbose, scoring="accuracy")
#     model.fit(X_train, y_train)
#     return model

# # Log metrics and model to MLflow
# def log_metrics_and_model(model, X_train, y_train, X_test, y_test, artifact_path, registered_model_name):
#     train_score = accuracy_score(y_train, model.predict(X_train))
#     test_score = accuracy_score(y_test, model.predict(X_test))
#     mlflow.log_metric("Train Accuracy", train_score)
#     mlflow.log_metric("Test Accuracy", test_score)
#     mlflow.sklearn.log_model(
#         sk_model=model.best_estimator_,
#         artifact_path=artifact_path,
#         registered_model_name=registered_model_name
#     )

# # Main function to execute the workflow
# def run_experiment(experiment_name, param_grid, artifact_path, registered_model_name):
#     start_time = time.time()

#     # Load and preprocess data
#     df = load_data()
#     X_train, X_test, y_train, y_test = preprocess_data(df)

#     # Create pipeline
#     pipe = create_pipeline()

#     # Set experiment's info 
#     mlflow.set_experiment(experiment_name)
#     experiment = mlflow.get_experiment_by_name(experiment_name)

#     # Call mlflow autolog
#     mlflow.sklearn.autolog()

#     with mlflow.start_run(experiment_id=experiment.experiment_id):
#         # Train model
#         model = train_model(pipe, X_train, y_train, param_grid)
        
#     print(f"...Training Done! --- Total training time: {time.time() - start_time} seconds")

# # Entry point for the script
# if __name__ == "__main__":
#     experiment_name = "fraud_detection_hyperparameter_tuning"
#     param_grid = {
#         "classifier__n_estimators": [100, 150],
#         "classifier__max_depth": [10, 20, 30],
#         "classifier__min_samples_split": [2, 5],
#         "classifier__min_samples_leaf": [1, 2]
#     }
#     artifact_path = "fraud_detection_model"
#     registered_model_name = "fraud_detector_rf"

#     run_experiment(experiment_name, param_grid, artifact_path, registered_model_name)

import pandas as pd
import numpy as np
import mlflow
import time
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import boto3
import os
from io import StringIO

def load_data():
    bucket_name = os.getenv('BUCKET_NAME')
    file_key = os.getenv('FILE_KEY')

    # Create an S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    # Read the CSV file from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_content = response['Body'].read().decode('utf-8')
    
    # Load into a pandas DataFrame
    return pd.read_csv(StringIO(csv_content))

# Preprocess data
def preprocess_data(df):
    # Create 'distance_to_merchant' as an example feature
    df['distance_to_merchant'] = np.sqrt((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)
    df['trans_dayofweek'] = pd.to_datetime(df['trans_date_trans_time']).dt.dayofweek
    df['trans_hour'] = pd.to_datetime(df['trans_date_trans_time']).dt.hour
    
    features = ['amt', 'distance_to_merchant', 'city_pop', 'trans_dayofweek', 'trans_hour']
    X = df[features]
    y = df['is_fraud']
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Create the pipeline with both models
def create_pipeline():
    return [
        ("RandomForest", Pipeline(steps=[
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(random_state=42))
        ])),
        ("LogisticRegression", Pipeline(steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(random_state=42, max_iter=1000))
        ]))
    ]

# Train model
def train_model(pipelines, X_train, y_train, param_grids, cv=2, n_jobs=-1, verbose=3):
    best_model = None
    best_score = 0
    best_pipeline = None

    for name, pipe in pipelines:
        print(f"Training with pipeline: {name}")
        model = GridSearchCV(pipe, param_grids[name], cv=cv, n_jobs=n_jobs, verbose=verbose, scoring="accuracy")
        model.fit(X_train, y_train)

        # Check if this model is the best one so far
        if model.best_score_ > best_score:
            best_score = model.best_score_
            best_model = model
            best_pipeline = name

    print(f"Best model selected: {best_pipeline} with score: {best_score}")
    return best_model

# Log metrics and model to MLflow
def log_metrics_and_model(model, X_train, y_train, X_test, y_test, artifact_path, registered_model_name):
    train_score = accuracy_score(y_train, model.predict(X_train))
    test_score = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("Train Accuracy", train_score)
    mlflow.log_metric("Test Accuracy", test_score)
    mlflow.sklearn.log_model(
        sk_model=model.best_estimator_,
        artifact_path=artifact_path,
        registered_model_name=registered_model_name
    )

# Main function to execute the workflow
def run_experiment(experiment_name, param_grids, artifact_path, registered_model_name):
    start_time = time.time()

    # Load and preprocess data
    df = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(df)

    # Create pipelines
    pipelines = create_pipeline()

    # Set experiment's info 
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    # Call mlflow autolog
    mlflow.sklearn.autolog()

    with mlflow.start_run(experiment_id=experiment.experiment_id):
        # Train model
        model = train_model(pipelines, X_train, y_train, param_grids)
        
    print(f"...Training Done! --- Total training time: {time.time() - start_time} seconds")

# Entry point for the script
if __name__ == "__main__":
    experiment_name = "fraud_detection_hyperparameter_tuning"
    
    # Parameter grids for both RandomForest and LogisticRegression
    param_grids = {
        "RandomForest": {
            "classifier__n_estimators": [100, 150],
            "classifier__max_depth": [10, 20, 30],
            "classifier__min_samples_split": [2, 5],
            "classifier__min_samples_leaf": [1, 2]
        },
        "LogisticRegression": {
            "classifier__C": [0.1, 1.0, 10],  # Regularization strength
            "classifier__penalty": ['l2'],   # Regularization type
            "classifier__solver": ['lbfgs', 'liblinear']  # Solvers for optimization
        }
    }
    
    artifact_path = "fraud_detection_model"
    registered_model_name = "fraud_detector_best_model"

    run_experiment(experiment_name, param_grids, artifact_path, registered_model_name)

