# Реализует бизнес-логику (например, обучение моделей, предсказания)

import pandas as pd
import numpy as np
import csv
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
import os
from deployment.backend.app.preprocessing import *
from deployment.backend.app.class_model import FullModel

TEMP_PATH = "temp"

# In-memory storage for models and data
models = {}
datasets = {}
datasets_prep = {}
learning_curves = {}
loaded_model = None


async def upload_csv_dataset(file):
    try:
        # Save uploaded file temporarily
        content = file.file.read()
        temp_file_path = os.path.join(TEMP_PATH, file.filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        # Load the CSV into a DataFrame
        # Зададим типы данных в колонках.
        dtypes_of_data = {
            'url_car': str,
            'car_make': str,
            'car_model': str,
            'car_gen': str,
            'car_type': str,
            'car_compl': str,
            'ann_id': str,
            'car_price': float,
            'ann_city': str,
            'link_cpl': str,
            'avail': str,
            'year': int,
            'mileage': int,
            'color': str,
            'eng_size': float,
            'eng_power': float,
            'eng_power_kw': float,
            'eng_type': str,
            'pow_resrv': str,
            'options': str,
            'transmission': str,
            'drive': str,
            'st_wheel': str,
            'condition': str,
            'count_owner': str,
            'original_pts': str,
            'customs': str,
            'url_compl': str,
            'state_mark': str,
            'class_auto': str,
            'door_count': float,  # могут быть пропуски
            'seat_count': str,  # могут быть значения с диапазоном, пропуски
            'long': float,
            'width': float,
            'height': float,
            'clearence': str,  # могут быть значения с диапазоном
            'v_bag': str,  # могут быть значения с диапазоном, пропуски
            'v_tank': float,
            'curb_weight': float,
            'gross_weight': float,
            'front_brakes': str,
            'rear_brakes': str,
            'max_speed': float,
            'acceleration': float,
            'fuel_cons': float,
            'fuel_brand': str,
            'engine_loc1': str,
            'engine_loc2': str,
            'turbocharg': str,
            'max_torq': float,
            'cyl_count': float  # Могут быть пропуски
        }
        df = pd.read_csv(temp_file_path, dtype=dtypes_of_data, parse_dates=['ann_date'])
        datasets["current"] = df
        os.remove(temp_file_path)

        return {"message": "CSV dataset uploaded successfully", "df.isnull": df.isnull().sum().to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")
    finally:
        file.file.close()

def perform_eda():
    if "current" not in datasets:
        raise HTTPException(status_code=404, detail="No dataset uploaded")
    df = datasets["current"]
    return {
        "statistics": df.describe().to_dict(),
    }

def preprocessing_data():
    if "current" not in datasets:
        raise HTTPException(status_code=404, detail="No dataset uploaded")
    df = datasets["current"]
    train, test = preproc(df)
    datasets_prep["current"] = [train, test]
    return {"message": "Preprocessing of the dataset was successful.", "train.isnull": train.isnull().sum().to_dict()}

def train_model(config):
    if config.id in models:
        raise HTTPException(status_code=400, detail=f"Model '{config.id}' already exists")
    if config.ml_model_type == "full":
        model = FullModel(config.hyperparameters)
        # Подготовка данных
        X_train, y_train, X_test, y_test = model.prepare_data(datasets_prep["current"][0], datasets_prep["current"][1])
        # Построение пайплайна
        model.build_pipeline(X_train)
        # Обучение модели
        model.train_model(X_train, y_train)
        # Оценка модели
        r2 = model.evaluate_model(X_test, y_test)
        # Предсказание
        predictions = model.predict(X_test)
        models[config.id] = model
        learning_curves[config.id] = model.learning_curve(X_train, y_train, X_test, y_test)
    elif config.ml_model_type == "poly":
        model = FullModel(config.hyperparameters)
        # Подготовка данных
        X_train, y_train, X_test, y_test = model.prepare_data(datasets_prep["current"][0], datasets_prep["current"][1])
        # Убираем логарифмирование целевой переменной
        y_train = np.exp(y_train)
        y_test = np.exp(y_test)
        # Построение пайплайна
        model.build_pipeline(X_train)
        # Обучение модели
        model.train_model(X_train, y_train)
        # Оценка модели
        r2 = model.evaluate_model(X_test, y_test)
        # Предсказание
        predictions = model.predict(X_test)
        models[config.id] = model
        learning_curves[config.id] = model.learning_curve(X_train, y_train, X_test, y_test)
    elif config.ml_model_type == "ohe":
        model = FullModel(config.hyperparameters)
        # Подготовка данных
        X_train, y_train, X_test, y_test = model.prepare_data(datasets_prep["current"][0], datasets_prep["current"][1])
        # Убираем логарифмирование целевой переменной
        y_train = np.exp(y_train)
        y_test = np.exp(y_test)
        # Построение пайплайна без полиномиальных признаков
        model.build_pipeline_cat(X_train)
        # Обучение модели
        model.train_model(X_train, y_train)
        # Оценка модели
        r2 = model.evaluate_model(X_test, y_test)
        # Предсказание
        predictions = model.predict(X_test)
        models[config.id] = model
        learning_curves[config.id] = model.learning_curve(X_train, y_train, X_test, y_test)
    else:
        raise HTTPException(status_code=400, detail="Unsupported model type")
    return {"message": f"Model '{config.id}' trained successfully, r2: {round(r2, 4)}"}

def load_model_endpoint(request):
    global loaded_model
    model_id = request.id

    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found.")

    loaded_model = models[model_id]
    return {"message": f"Model '{model_id}' loaded"}

def unload_model_endpoint():
    global loaded_model
    if not loaded_model:
        raise HTTPException(status_code=400, detail="No model loaded.")

    loaded_model = None
    return {"message": "Model unloaded"}

def list_learning_curve(model_id):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found.")
    return {f"learning curve {model_id}": learning_curves[model_id]}

def make_prediction(model_id, data):
    if model_id not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    model = models[model_id]

    try:
        input_data = pd.DataFrame([data])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {e}")
    try:
        predictions = model.predict(preproc_x(input_data))
        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

async def predict_items(file):
    global loaded_model
    if not loaded_model:
        raise HTTPException(status_code=400, detail="No model loaded.")
    # Save uploaded file temporarily
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())
    # Load the CSV into a DataFrame
    X = pd.read_csv(temp_file_path)
    os.remove(temp_file_path)

    output = X

    X['predict'] = pd.Series(loaded_model.predict(preproc_x(X)))
    output['predict'] = X['predict']
    output.to_csv('predictions.csv', index=False)
    response = FileResponse(path='predictions.csv',
                            media_type='text/csv', filename='predictions.csv')
    return response

def list_models():
    return {"models": list(models.keys())}

def remove_model(model_id: str):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found.")

    del models[model_id]
    return {"message": f"Model '{model_id}' removed"}

def remove_all_models():
    models.clear()
    return {"message": "All models removed"}