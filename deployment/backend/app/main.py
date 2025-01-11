import logging
from logging.handlers import SocketHandler
from pythonjsonlogger import jsonlogger
from fastapi import FastAPI
import uvicorn


LOGSTASH_HOST = "logstash"
LOGSTASH_PORT = 5000


logger = logging.getLogger("backend_logger")
logger.setLevel(logging.INFO)

logstash_handler = SocketHandler(LOGSTASH_HOST, LOGSTASH_PORT)
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(service)s %(module)s")
logstash_handler.setFormatter(formatter)
logger.addHandler(logstash_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


app = FastAPI(
    title="ML Model Management API",
    docs_url="/api/openapi",
    version="1.0"
)

@app.get("/", tags=["Health Check"])
def read_root():
    logger.info(
        "Health check endpoint was called",
        extra={"service": "backend", "module": "health_check"}
    )
    return {"message": "ML API is running!"}

@app.get("/log", tags=["Logging"])
def test_logging():
    logger.info(
        "Test logging endpoint was called",
        extra={"service": "backend", "module": "test_logging"}
    )
    return {"message": "Log sent to Logstash!"}

if __name__ == "__main__":
    logger.info(
        "Starting FastAPI service",
        extra={"service": "backend", "module": "startup"}
    )
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
