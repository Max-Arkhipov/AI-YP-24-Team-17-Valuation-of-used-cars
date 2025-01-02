import pandas as pd
import numpy as np
import logging
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
import os
from deployment.backend.app.preprocessing import preproc
from deployment.backend.app.class_model import FullModel
from deployment.backend.app.preprocessing_x import preproc_x

logger = logging.getLogger(__name__)

models = {}
datasets = {}
datasets_prep = {}
learning_curves = {}
loaded_model = None

async def upload_csv_dataset(file):
    try:
        logger.info(f"Uploading dataset: {file.filename}")
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        df = pd.read_csv(temp_file_path)
        datasets["current"] = df
        os.remove(temp_file_path)

        logger.info("Dataset uploaded successfully", extra={"rows": len(df), "columns": len(df.columns)})
        return {"message": "CSV dataset uploaded successfully", "df.isnull": df.isnull().sum().to_dict()}
    except Exception as e:
        logger.error(f"Failed to process CSV file: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")

def perform_eda():
    logger.info("Performing EDA on the dataset")
    if "current" not in datasets:
        logger.error("No dataset uploaded for EDA")
        raise HTTPException(status_code=404, detail="No dataset uploaded")
    df = datasets["current"]
    logger.info("EDA completed", extra={"statistics": df.describe().to_dict()})
    return {"statistics": df.describe().to_dict()}

def preprocessing_data():
    logger.info("Starting dataset preprocessing")
    if "current" not in datasets:
        logger.error("No dataset uploaded for preprocessing")
        raise HTTPException(status_code=404, detail="No dataset uploaded")
    df = datasets["current"]
    train, test = preproc(df)
    datasets_prep["current"] = [train, test]
    logger.info("Dataset preprocessing completed successfully")
    return {"message": "Preprocessing of the dataset was successful.", "train.isnull": train.isnull().sum().to_dict()}

def train_model(config):
    logger.info(f"Training model with ID: {config.id}")
    if config.id in models:
        logger.error(f"Model '{config.id}' already exists")
        raise HTTPException(status_code=400, detail=f"Model '{config.id}' already exists")

    try:
        model = FullModel(config.hyperparameters)
        X_train, y_train, X_test, y_test = model.prepare_data(datasets_prep["current"][0], datasets_prep["current"][1])
        model.build_pipeline(X_train)
        model.train_model(X_train, y_train)
        r2 = model.evaluate_model(X_test, y_test)
        models[config.id] = model
        learning_curves[config.id] = model.learning_curve(X_train, y_train, X_test, y_test)
        logger.info("Model training completed successfully", extra={"model_id": config.id, "r2_score": r2})
        return {"message": f"Model '{config.id}' trained successfully, r2: {round(r2, 4)}"}
    except Exception as e:
        logger.error(f"Error during model training: {e}", extra={"model_id": config.id})
        raise HTTPException(status_code=500, detail="Model training failed")

def load_model_endpoint(request):
    global loaded_model
    logger.info(f"Loading model with ID: {request.id}")
    if request.id not in models:
        logger.error(f"Model '{request.id}' not found")
        raise HTTPException(status_code=404, detail="Model not found")
    loaded_model = models[request.id]
    logger.info("Model loaded successfully", extra={"model_id": request.id})
    return {"message": f"Model '{request.id}' loaded"}

def unload_model_endpoint():
    global loaded_model
    logger.info("Unloading model")
    if not loaded_model:
        logger.error("No model loaded to unload")
        raise HTTPException(status_code=400, detail="No model loaded")
    loaded_model = None
    logger.info("Model unloaded successfully")
    return {"message": "Model unloaded"}

def list_learning_curve(model_id):
    logger.info(f"Retrieving learning curve for model: {model_id}")
    if model_id not in models:
        logger.error(f"Model '{model_id}' not found")
        raise HTTPException(status_code=404, detail="Model not found")
    return {f"learning curve {model_id}": learning_curves[model_id]}

def make_prediction(model_id, data):
    logger.info(f"Making prediction with model: {model_id}")
    if model_id not in models:
        logger.error(f"Model '{model_id}' not found")
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    try:
        input_data = pd.DataFrame([data])
        predictions = models[model_id].predict(preproc_x(input_data))
        logger.info("Prediction completed successfully", extra={"model_id": model_id})
        return {"predictions": predictions.tolist()}
    except Exception as e:
        logger.error(f"Prediction failed: {e}", extra={"model_id": model_id})
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

async def predict_items(file):
    global loaded_model
    logger.info(f"Making predictions for file: {file.filename}")
    if not loaded_model:
        logger.error("No model loaded for prediction")
        raise HTTPException(status_code=400, detail="No model loaded")
    try:
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())
        X = pd.read_csv(temp_file_path)
        os.remove(temp_file_path)
        X['predict'] = pd.Series(loaded_model.predict(preproc_x(X)))
        X.to_csv('predictions.csv', index=False)
        logger.info("Predictions saved to file", extra={"output_file": "predictions.csv"})
        return FileResponse(path='predictions.csv', media_type='text/csv', filename='predictions.csv')
    except Exception as e:
        logger.error(f"Prediction from file failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

def list_models():
    logger.info("Listing all models")
    return {"models": list(models.keys())}

def remove_model(model_id: str):
    logger.info(f"Removing model: {model_id}")
    if model_id not in models:
        logger.error(f"Model '{model_id}' not found")
        raise HTTPException(status_code=404, detail="Model not found")
    del models[model_id]
    logger.info("Model removed successfully", extra={"model_id": model_id})
    return {"message": f"Model '{model_id}' removed"}

def remove_all_models():
    logger.info("Removing all models")
    models.clear()
    logger.info("All models removed successfully")
    return {"message": "All models removed"}
