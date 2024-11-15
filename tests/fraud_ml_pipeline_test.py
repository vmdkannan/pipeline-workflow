import pytest
from unittest import mock
from app.fraud_detection_train import load_data, preprocess_data, create_pipeline, train_model
from io import StringIO
import os

bucket_name = "mymlflowbuc"  # Update with the path to your local file or online URL
file_key = "/transactions/fraudTestLess.csv"

# Test data loading
def test_load_data():
    # S3 Bucket and Key
    # bucket_name = os.getenv("BUCKET_NAME")
    # file_key = os.getenv("FILE_KEY")
    
    
    df = load_data(bucket_name, file_key)
 
    assert not df.empty, "Dataframe is empty"

# Test data preprocessing
def test_preprocess_data():
    # bucket_name = os.getenv("BUCKET_NAME")
    # file_key = os.getenv("FILE_KEY")
    df = load_data(bucket_name, file_key)
    X_train, X_test, y_train, y_test = preprocess_data(df)
    assert len(X_train) > 0, "Training data is empty"
    assert len(X_test) > 0, "Test data is empty"

# Test pipeline creation
def test_create_pipeline():
    pipe = create_pipeline()
    assert "scaler" in pipe.named_steps, "Scaler missing in pipeline"
    assert "classifier" in pipe.named_steps, "Classifier missing in pipeline"

# Test model training (mocking GridSearchCV)
# @mock.patch('app.train.GridSearchCV.fit', return_value=None)
@mock.patch('app.fraud_detection_train.GridSearchCV.fit', return_value=None)
def test_train_model(mock_fit):
    pipe = create_pipeline()
    # bucket_name = os.getenv("BUCKET_NAME")
    # file_key = os.getenv("FILE_KEY")
    X_train, X_test, y_train, y_test = preprocess_data(load_data(bucket_name, file_key))
    param_grid = {
        "classifier__n_estimators": [100, 150],
        "classifier__learning_rate": [0.01, 0.1],
        "classifier__max_depth": [3, 5]
    }
    model = train_model(pipe, X_train, y_train, param_grid)
    assert model is not None, "Model training failed"
