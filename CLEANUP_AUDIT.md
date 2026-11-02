# FreshGuard AI cleanup audit and deletion inventory

Audit date: 2026-11-02

## Git and safety findings

- Git reports the project files as untracked; there is no tracked baseline. Existing workspace contents are treated as user-owned.
- MobileNetV2 checkpoint `ml-service/models/freshness_classifier/best_model.pth` (9,148,043 bytes) is separate from YOLO weights `ml-service/models/yolo11n.pt` (5,613,764 bytes). Classifier metadata/evaluation artifacts are excluded.
- `ml-service/app/model_service.py` loads MobileNetV2 only. The prediction service processes the full uploaded image and returns Fresh/Rotten/Uncertain and probabilities. Backend/frontend consume that contract.
- Evaluation reports, dataset audit documents, manifests/research metadata, environment configuration, and app data are excluded.
- YOLO has no active runtime import/call. The detector-only `ultralytics` dependency was removed from `ml-service/requirements.txt`.

## Proposed deletion inventory

`cleanup_deletion_inventory.csv` lists each candidate file and byte size. It covers raw downloaded/cache data, prepared split images, acquired/extracted data, Open Images images/labels, the Mendeley archive/extraction, temporary Open Images staging images, and YOLO weights. Files: 74,528. Listed bytes: 12,691,062,406 (11.82 GiB).

Candidate roots:
- `ml-service/models/yolo11n.pt`
- `ml-service/datasets/raw`
- `ml-service/datasets/prepared/train`
- `ml-service/datasets/prepared/val`
- `ml-service/datasets/prepared/test`
- `ml-service/datasets/external_staging/phase10/archives`
- `ml-service/datasets/external_staging/phase10/extracted`
- `ml-service/datasets/external_staging/phase11/freshness44_cleaned`
- `ml-service/datasets/expansion_15/detection_open_images/images`
- `ml-service/datasets/expansion_15/detection_open_images/labels`
- `ml-service/datasets/expansion_15/sources/mendeley_foodclass_v2/FoodClass2.zip`
- `ml-service/datasets/expansion_15/sources/mendeley_foodclass_v2/extracted`
- `ml-service/datasets/expansion_15/preparation_open_images/image_staging`

## Preserved

- `ml-service/models/freshness_classifier/` (checkpoint, class mapping, preprocessing metadata, metrics and evaluation artifacts).
- Classifier architecture, preprocessing/inference/API code, backend, frontend, camera and upload flow, scan history and MongoDB integration.
- `ml-service/evaluation/`, reports, audit documents, manifests and dataset metadata not listed above.
- `ml-service/datasets/prepared/manifest.csv`, `.venv`, environment configuration and all unlisted files.

This pre-deletion audit limits cleanup to the exact file list in the CSV; ambiguous or unlisted files remain preserved.

## Cleanup completion and verification

- Removed every file listed in `cleanup_deletion_inventory.csv`; post-cleanup path check found 0 of 74,528 entries remaining. Listed file sizes total 12,691,062,406 bytes (11.82 GiB / 12.69 GB decimal).
- No archive or model-weight files remain under `ml-service/datasets/`. The YOLO checkpoint is gone. The MobileNetV2 checkpoint remains at 9,148,043 bytes. `ultralytics` is absent from `ml-service/requirements.txt` and is not installed in the project virtual environment.
- Active application code scan found no YOLO import, detector call, or detection response field. Historical YOLO/object-detection mentions remain in preserved dataset research and evaluation records; they describe prior audit work. Two backend regression assertions intentionally check that `detections` and `bbox` fields are absent.
- Passed: MobileNetV2 prediction-service tests (5/5), frontend tests (5/5), backend tests (9/9), and Vite production build. A direct checkpoint load returned success and actual inference on a generated JPEG returned `Fresh` with scores summing to 1.
- The full FastAPI TestClient run did not complete in this environment, and a live loopback request to Uvicorn was blocked by the sandbox socket policy. Therefore the `/health` HTTP endpoint and live Express-to-FastAPI network path are not reported as verified.
- The generated-image fixture in `ml-service/tests/test_main_api.py` removes the deleted training-image dependency from the API regression tests.
