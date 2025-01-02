# Главный файл для запуска FastAPI-сервиса.
import uvicorn
from fastapi import FastAPI
from deployment.backend.app.routers import api
from deployment.backend.app.utils import setup_logging


logger = setup_logging()

app = FastAPI(title="ML Model Management API",
              docs_url="/api/openapi",
              version="1.0")

# Include API router
app.include_router(api.router, prefix="/api/v1", tags=["ML API"])

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

@app.get("/", tags=["Health Check"])
def read_root():
    logger.info("Health check endpoint called")
    return {"message": "ML API is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
