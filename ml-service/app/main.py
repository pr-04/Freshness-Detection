import logging
import os
from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from app.model_service import (
    CLASSIFIER_NAME,
    get_classifier_error,
    get_freshness_classifier,
    load_freshness_classifier,
)
from app.prediction_service import canonical_fruit, predict_freshness

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}

try:
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv("FRESHGUARD_LOW_CONFIDENCE_THRESHOLD", "0.60"))
except ValueError as error:
    raise RuntimeError("FRESHGUARD_LOW_CONFIDENCE_THRESHOLD must be a number from 0.5 to 1.") from error

if not 0.5 <= LOW_CONFIDENCE_THRESHOLD <= 1:
    raise RuntimeError("FRESHGUARD_LOW_CONFIDENCE_THRESHOLD must be between 0.5 and 1.")

app = FastAPI(
    title="FreshGuard AI ML Service",
    description="Direct full-image Fresh/Rotten classification with MobileNetV2.",
    version="0.4.0",
)


@app.on_event("startup")
def initialize_models():
    """Load MobileNetV2 once when this service process starts."""
    if not load_freshness_classifier():
        logger.error("ML service started without %s; /predict will return HTTP 503", CLASSIFIER_NAME)


@app.get("/health")
async def health_check():
    """Report the MobileNetV2 loading state."""
    classifier_loaded = get_freshness_classifier() is not None
    response = {
        "status": "ok" if classifier_loaded else "degraded",
        "service": "FreshGuard AI ML Service",
        "model_loaded": classifier_loaded,
        "models": {"classifier": {"name": CLASSIFIER_NAME, "loaded": classifier_loaded}},
    }
    if not classifier_loaded and get_classifier_error():
        response["models"]["classifier"]["error"] = get_classifier_error()
    return response


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    fruit: str = Form(...),
):
    """Validate an uploaded image, then classify its complete image with MobileNetV2."""
    try:
        selected_fruit = canonical_fruit(fruit)
        if selected_fruit is None:
            raise HTTPException(
                status_code=400,
                detail="Unsupported fruit selection. Choose Apple, Banana, Guava, Orange, Pomegranate, or Strawberry.",
            )

        content_type = (file.content_type or "").split(";")[0].strip().lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image type. Please upload a JPEG, JPG, or PNG image.",
            )

        # Read at most one byte over the limit to reject oversized uploads early.
        contents = await file.read(MAX_FILE_SIZE + 1)
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Image is too large. The maximum upload size is 10 MB.")

        try:
            # Decode the original complete image in memory; no box or crop is made.
            with Image.open(BytesIO(contents)) as opened_image:
                opened_image.load()
                if opened_image.format not in ALLOWED_IMAGE_FORMATS:
                    raise HTTPException(
                        status_code=400,
                        detail="Unsupported image type. Please upload a JPEG, JPG, or PNG image.",
                    )
                image = opened_image.copy()
        except HTTPException:
            raise
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid readable image or is corrupted.",
            )

        if get_freshness_classifier() is None:
            raise HTTPException(
                status_code=503,
                detail=f"{CLASSIFIER_NAME} is unavailable. Check /health and the service log.",
            )

        try:
            result = await run_in_threadpool(
                predict_freshness,
                image,
                selected_fruit,
                LOW_CONFIDENCE_THRESHOLD,
            )
            return {"success": True, "mock": False, "prediction": result}
        except Exception as error:
            logger.exception("Direct MobileNetV2 inference failed")
            raise HTTPException(
                status_code=500,
                detail="MobileNetV2 classification failed. See the ML service log for details.",
            ) from error
        finally:
            image.close()
    finally:
        # Uploaded bytes are handled in memory and the request file is closed.
        await file.close()
