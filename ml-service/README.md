# FreshGuard AI ML Service

The FastAPI workflow uses the existing trained **MobileNetV2** classifier directly on the complete uploaded image. The application performs image-level freshness classification, not object detection. It does not identify fruit or verify the user-selected category.

The user selects the fruit category. MobileNetV2 does not identify fruit, verify the selected category, reject non-fruit images, or assess food safety.

## Requirements and setup

- Windows 10/11 and PowerShell
- Python 3.10 or newer (the current environment uses Python 3.12)
- Several GB free disk space for PyTorch and dependencies

From the project root:

```powershell
cd "C:\Users\asus\OneDrive\Desktop\Capstone Project\ml-service"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

CPU inference is supported and does not require CUDA. PyTorch and Torchvision are required by the classifier; no object-detection package is installed by this service.

## Start and check service health

From `ml-service` with the virtual environment active:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The service loads `models/freshness_classifier/best_model.pth` once at startup and reports its actual loading state:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

`/health` returns `status: "ok"` and `model_loaded: true` when MobileNetV2 is available. If the classifier fails to load, health reports `degraded` and `/predict` returns HTTP 503.

Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). For a direct request, provide both the `file` and `fruit` multipart fields:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/predict" `
  -F "fruit=Apple" `
  -F "file=@C:\path\to\apple.jpg"
```

Only JPEG/JPG and PNG are accepted; unreadable images return HTTP 400, uploads above 10 MB return HTTP 413, missing fruit selection is rejected, and unsupported selections return HTTP 400. Images are processed in memory by FastAPI.

## Direct prediction behavior

Supported user-selected categories are:

- Apple
- Banana
- Guava
- Orange
- Pomegranate
- Strawberry

Grape is temporarily excluded; Jujube remains excluded. The selected category is metadata from the user, not a MobileNetV2 prediction.

For each request, FastAPI validates the original image, converts the full image to RGB, resizes it to 224×224, converts it to a tensor, and normalizes it with the checkpoint metadata values:

- Mean: `[0.485, 0.456, 0.406]`
- Standard deviation: `[0.229, 0.224, 0.225]`
- Class order: `fresh=0`, `rotten=1`

Example response shape (scores shown here are illustrative; actual requests return model outputs):

```json
{
  "success": true,
  "mock": false,
  "prediction": {
    "fruit": "Apple",
    "freshness": "Fresh",
    "uncertain": false,
    "uncertainty_reason": null,
    "probabilities": {"fresh": 0.98, "rotten": 0.02},
    "model": "MobileNetV2"
  }
}
```

The default `FRESHGUARD_LOW_CONFIDENCE_THRESHOLD` is `0.60`. If the highest model class score is below the configured threshold, the result is `Uncertain` and includes both scores and a reason. This threshold operates on softmax outputs that have not been calibrated; the scores are not freshness percentages or food-safety probabilities. Configure it in PowerShell before launching Uvicorn (the service does not automatically load `.env` files):

```powershell
$env:FRESHGUARD_LOW_CONFIDENCE_THRESHOLD = "0.65"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Express and frontend flow

The React scanner submits multipart fields `image` and `fruit` to Express `POST /api/scans`. Express forwards the original upload as `file` plus the selected fruit to this service. FastAPI returns direct classification; Express saves the selected category, result, probabilities, model, uncertainty state, upload reference, and timestamp, then returns the existing `{ success, scan, prediction }` wrapper. MongoDB remains optional through the existing in-memory fallback.

The backend forwarding default and `backend/.env.example` use `http://127.0.0.1:8000`. Set `ML_SERVICE_URL` if the FastAPI service is hosted elsewhere. The request timeout remains configurable through `ML_SERVICE_TIMEOUT_MS`.

## Existing checkpoint and category-wise evaluation

The checkpoint is the Part 9 Torchvision MobileNetV2 fine-tuned from pretrained weights. It was trained on 3,200 images from the `raw` configuration of [Project-AgML/fresh_rotten_fruit_classification](https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification), with 2,240 training, 480 validation, and 480 test images. The dataset contains Apple, Banana, Grape, Guava, Jujube, Orange, Pomegranate, and Strawberry with Fresh and Rotten labels. Project cleanup removed the downloaded dataset caches and prepared image splits; the checkpoint, class mapping, preprocessing metadata, and evaluation artifacts remain. The model itself has no fruit identity output.

The read-only category-wise evaluation artifacts are in `evaluation/category_wise_mobilenetv2/`. It evaluated the original test split by direct full-image classification, excluding Jujube and deduplicating two exact duplicate Orange/Fresh file pairs for metrics. Six categories had no errors in these small samples; Grape had one false Fresh error. These results are limited to the same curated dataset and do not establish real-world accuracy. Confirm selected categories on independent real-world images before making broader claims.

No real early-spoilage class, produce identity, edibility, or food-safety outcome is modeled. One fruit per image is the intended use. The binary model will still return a class for unrelated or unsupported images, so do not treat it as an out-of-domain detector.

## Historical training notes

The training script is `scripts/train_freshness_classifier.py`; it is not run by the service. The existing checkpoint must be reused for this workflow. If training is separately approved in a future phase, the original documented command was:

```powershell
python scripts/train_freshness_classifier.py --epochs 5 --batch-size 16 --learning-rate 0.0001 --seed 42 --patience 2 --device cpu
```

Training and validation preprocessing, augmentation, counts, attribution, and evaluation are recorded in the retained dataset/evaluation reports and `models/freshness_classifier/metadata.json`. The source dataset images and prepared train/validation/test image folders were removed during project cleanup; do not expect the training scripts to run until a dataset is separately restored.
