from fastapi import APIRouter, HTTPException, File, UploadFile
import logging
from deployment.backend.app.services import (
    upload_csv_dataset,
    perform_eda,
    preprocessing_data,
    train_model,
    load_model_endpoint,
    unload_model_endpoint,
    list_learning_curve,
    make_prediction,
    predict_items,
    list_models,
    remove_model,
    remove_all_models
)
from deployment.backend.app.models import (
    DatasetUploadRequest,
    FitRequest,
    LoadRequest,
    LoadResponse,
    UnloadResponse,
    PredictionRequest,
    LearningCurveRequest,
    ModelListResponse,
    RemoveResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/dataset/upload")
async def upload_csv_dataset_endpoint(file: UploadFile = File(...)):
    logger.info("Upload dataset endpoint called")
    if not file.filename.endswith(".csv"):
        logger.error("Invalid file format: Only CSV files are supported")
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    response = await upload_csv_dataset(file)
    logger.info("Dataset uploaded successfully", extra={"filename": file.filename})
    return response

@router.get("/dataset/eda")
def perform_eda_endpoint():
    logger.info("EDA endpoint called")
    return perform_eda()

@router.post("/dataset/preprocessing")
def preprocessing_dataset_endpoint():
    logger.info("Preprocessing dataset endpoint called")
    return preprocessing_data()

@router.post("/models/fit")
def train_model_endpoint(request: FitRequest):
    logger.info("Train model endpoint called", extra={"model_id": request.config.id})
    response = train_model(request.config)
    logger.info("Model training completed", extra={"model_id": request.config.id})
    return response

@router.get("/models/list_models", response_model=ModelListResponse)
def list_models_endpoint():
    logger.info("List models endpoint called")
    return list_models()

@router.post("/models/load", response_model=LoadResponse)
def load_model(request: LoadRequest):
    logger.info("Load model endpoint called", extra={"model_id": request.id})
    response = load_model_endpoint(request)
    logger.info("Model loaded successfully", extra={"model_id": request.id})
    return response

@router.post("/models/unload", response_model=UnloadResponse)
def unload_model():
    logger.info("Unload model endpoint called")
    response = unload_model_endpoint()
    logger.info("Model unloaded successfully")
    return response

@router.post("/models/predict_items")
async def make_prediction_items_endpoint(file: UploadFile):
    logger.info("Predict items endpoint called", extra={"filename": file.filename})
    response = await predict_items(file)
    logger.info("Prediction completed for file", extra={"filename": file.filename})
    return response

@router.post("/models/learning_curve")
def learning_curves_endpoint(request: LearningCurveRequest):
    logger.info("Learning curve endpoint called", extra={"model_id": request.id})
    return list_learning_curve(request.id)

@router.post("/models/predict")
def make_prediction_endpoint(request: PredictionRequest):
    logger.info("Predict endpoint called", extra={"model_id": request.id})
    response = make_prediction(request.id, request.data)
    logger.info("Prediction completed", extra={"model_id": request.id})
    return response

@router.delete("/models/remove/{model_id}", response_model=RemoveResponse)
def remove_model_endpoint(model_id: str):
    logger.info("Remove model endpoint called", extra={"model_id": model_id})
    response = remove_model(model_id)
    logger.info("Model removed successfully", extra={"model_id": model_id})
    return response

@router.delete("/models/remove_all", response_model=RemoveResponse)
def remove_all_models_endpoint():
    logger.info("Remove all models endpoint called")
    response = remove_all_models()
    logger.info("All models removed successfully")
    return response
