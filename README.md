# FreshGuard AI

FreshGuard AI uses a React/Vite frontend, Express API, MongoDB scan history (with an in-memory fallback), and a FastAPI ML service. The current scan flow sends the complete uploaded image directly to the existing MobileNetV2 classifier. The user selects the fruit category; the model does not identify or verify it.

## Development services

The consumer website has three pages: Home (with the scanner), How It Works, and History. Older `/scanner` links redirect to the Home scanner, and `/dashboard` redirects to History.

| Service | Default address | Configuration |
| --- | --- | --- |
| React/Vite frontend | `http://localhost:5173` | `VITE_API_URL` in the project-root `.env` |
| Express API | `http://localhost:5000` | `PORT`, `MONGODB_URI`, and `ML_SERVICE_URL` in `backend/.env` |
| FastAPI ML service | `http://127.0.0.1:8000` | Uvicorn default port; backend URL uses `ML_SERVICE_URL` |

The checked-in examples and current backend `.env` point to port 8000. Express also defaults to `http://127.0.0.1:8000` when `ML_SERVICE_URL` is unset. Keep local credentials in ignored `.env` files.

## Install

Prerequisites: Python 3.10+, Node.js 18+, npm, and MongoDB if persistent scan storage is desired.

From the project root:

```powershell
npm install
npm --prefix backend install
cd ml-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Inference uses the MobileNetV2 classifier directly. No object detector is part of the application.

## Run all three services

Start each in a separate PowerShell window.

**FastAPI ML service:**

```powershell
cd ml-service
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The service loads `models/freshness_classifier/best_model.pth` once on startup. `GET http://127.0.0.1:8000/health` reports whether MobileNetV2 loaded.

**Express API:**

```powershell
cd backend
npm --prefix backend run dev
```

Check `http://localhost:5000/api/health`.

**React/Vite frontend:**

```powershell
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Select Apple, Banana, Guava, Orange, Pomegranate, or Strawberry, then upload or capture one fruit image. Grape and Jujube are excluded. React calls Express only; Express forwards the image and selected fruit to FastAPI.

## Scan API

`POST /api/scans` accepts multipart fields `image` and `fruit`. Express preserves its existing upload validation and forwards `file` plus `fruit` to FastAPI `POST /predict`. FastAPI validates JPEG/JPG/PNG and a 10 MB maximum, converts the complete image to RGB, applies the saved 224×224 resize and ImageNet normalization, and runs MobileNetV2 directly. It creates no boxes or crops.

Example FastAPI request:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/predict" `
  -F "fruit=Apple" `
  -F "file=@C:\path\to\apple.jpg"
```

The response contains the user-selected fruit, a Fresh/Rotten/Uncertain result, Fresh and Rotten model scores, and the MobileNetV2 name. These scores are not freshness percentages, calibrated safety probabilities, or food-safety assessments. A configurable top-score threshold defaults to `0.60`; set `FRESHGUARD_LOW_CONFIDENCE_THRESHOLD` in the shell before starting Uvicorn to change it. The model always predicts one of its two classes internally and cannot recognize unsupported fruit or non-fruit images.

Express returns the existing `{ success, scan, prediction }` wrapper. Scan metadata is saved to MongoDB when connected; the existing memory fallback is used otherwise. Uploaded files continue to use the existing Express uploads folder. New scan records store the selected category, status, class scores, model, uncertainty information, image reference, and timestamp. Legacy database documents are not deleted; detection-specific fields are no longer included in API responses or the UI.

The History page displays direct-classification scans and basic older records. It offers Fresh, Rotten, and Uncertain filters; uncertain results do not add to Fresh or Rotten totals. Older records without direct classifier scores remain in history with result details marked unavailable.

## Model and evaluation

The existing Torchvision MobileNetV2 checkpoint was trained on the `raw` Project-AgML fresh/rotten fruit dataset. It has two classes (`fresh=0`, `rotten=1`) and training examples across eight fruit categories. The current prototype enables six user-selected categories: Apple, Banana, Guava, Orange, Pomegranate, and Strawberry. Grape is temporarily excluded after one false Fresh result in its category-wise test sample; Jujube remains excluded by product scope.

See [ml-service/README.md](ml-service/README.md) for model, dataset, evaluation, limitations, and API details. The category-wise evaluation artifacts are in `ml-service/evaluation/category_wise_mobilenetv2/`. The held-out metrics are limited to this dataset and do not establish real-world reliability.

## ML architecture and retained artifacts

```text
Image upload or camera capture
  -> Express POST /api/scans
  -> FastAPI POST /predict
  -> MobileNetV2 full-image Fresh/Rotten classification
  -> Fresh, Rotten, or Uncertain response
  -> Express scan history and React result view
```

The ML service performs image-level classification. It has no object localization stage, boxes, crops, or produce detector. Trained model artifacts and evaluation reports are retained under `ml-service/models/freshness_classifier/` and `ml-service/evaluation/`. Downloaded training images, archives, and detector weights were removed; the per-file pre-deletion audit is in [CLEANUP_AUDIT.md](CLEANUP_AUDIT.md) and [cleanup_deletion_inventory.csv](cleanup_deletion_inventory.csv). Historical dataset research documents remain under `ml-service/evaluation/` and `ml-service/datasets/` where they are useful as audit records.
