# FreshGuard AI cleanup audit

**Audit status:** Pre-cleanup inventory completed. The project source tree is entirely untracked in Git, so there is no tracked baseline or clean commit to restore from. The user's requested preservation boundaries were checked against current imports and references before removals.

## Current inference architecture

`ml-service/app/main.py`, `model_service.py`, and `prediction_service.py` already implement direct full-image MobileNetV2 Fresh/Rotten/Uncertain classification. No detector is initialized or imported in the active FastAPI path. Express forwards the uploaded image and selected fruit; the scan controller stores direct prediction fields. The frontend scanner and history support direct results, with legacy object-detection compatibility still present in response shaping, the Mongo schema, and history rendering.

## Protected files and dependencies

- Classifier checkpoint: `ml-service/models/freshness_classifier/best_model.pth` (9,148,043 bytes at audit time).
- Classifier metadata/mapping and preprocessing: `ml-service/models/freshness_classifier/metadata.json` (1,298 bytes).
- Classifier evaluation/training metrics: `test_evaluation.json`, `test_evaluation.txt`, and `training_metrics.csv` in the same directory.
- Active inference requires `fastapi`, `uvicorn`, `python-multipart`, `Pillow`, `torch`, and `torchvision`. `torch` and `torchvision` are required by current inference code and must remain.
- `datasets` is imported by `scripts/inspect_dataset.py`; it is not a runtime inference dependency. Keep it in the development requirements while that utility remains.
- MongoDB data, application environment files, upload data, frontend assets, and Node dependencies are outside the deletion scope.

## Proposed deletions

| Path | Reason | References checked |
|---|---|---|
| `ml-service/models/yolo11n.pt` and `ml-service/models/.gitkeep` | YOLO checkpoint and its detector-only placeholder | No active code imports or references the detector; it is not shared with MobileNetV2. |
| `ml-service/datasets/raw/c/` | Hugging Face Arrow/parquet image dataset cache; 7,169,255,614 bytes observed across its contents | Used by prior data preparation, not inference; classifier checkpoint is separate. |
| `ml-service/datasets/prepared/` | 3,200 prepared Fresh/Rotten training images plus manifest; 2,856,661,967 bytes observed | Training/evaluation data only; no active application imports. |
| `ml-service/datasets/expansion_15/sources/` | Downloaded Mendeley/Zenodo archives and extracted dataset images | Audit reports remain elsewhere; source images are no longer needed by the application. |
| `ml-service/datasets/expansion_15/detection_open_images/images/` and `labels/` | Downloaded Open Images images and YOLO-format label files | No active application references. Preserve acquisition/validation reports and license-attribution record. |
| `ml-service/datasets/expansion_15/detection_open_images/data.yaml`, `annotation_manifest.csv`, and `download_manifest.csv` | Detector training configuration and manifests | Detector-only; not consumed by runtime or classifier. |
| `ml-service/datasets/expansion_15/preparation_open_images/` | Dataset downloader, image staging, downloaded metadata and bundled downloader dependencies | Preparation-only and detector-specific; no active application references. |
| `ml-service/app/detection_service.py`, if present | Detector-only inference implementation | No active imports; verify immediately before deletion. |

The raw cache and prepared image folder alone account for **10,025,917,581 bytes** before counting the Mendeley/Zenodo/Open Images files and temporary image staging. Exact recovered space will be measured from paths actually removed.

## Files to preserve

- Entire `ml-service/models/freshness_classifier/` directory, especially the checkpoint, metadata, mapping, and metrics.
- `ml-service/app/model_service.py`, `prediction_service.py`, and direct inference in `main.py`.
- Useful evaluation and dataset audit reports under `ml-service/evaluation/` and `ml-service/datasets/expansion_15/review_*`.
- Existing API, frontend, dashboard/history, camera, uploads, MongoDB data, environment files, and package dependencies unrelated to YOLO.
- Dataset acquisition/validation reports and source attribution records where they retain audit value, even if the image payloads are removed.

## Planned code/documentation cleanup

- Remove only the `ultralytics` dependency; retain PyTorch and Torchvision.
- Remove detection-only fields from new scan records and API responses. Do not delete or rewrite existing MongoDB documents; legacy stored fields will simply no longer be emitted by the API.
- Remove the old history display path that expects bounding boxes or per-object detections. Older records without direct classifier scores will remain visible as historical records with unavailable result details.
- Update current architecture documentation and progress summary to state image-level MobileNetV2 classification and its selected-fruit limitation.
- Keep historical evaluation and dataset-audit reports intact; historical detector references inside those records will be identified as historical.

## Risks and limits

- Removing training images and cache makes future retraining/evaluation against those datasets impossible unless the data is reacquired. The trained MobileNetV2 checkpoint and its inference metadata are retained.
- Git cannot provide rollback because all repository files currently show as untracked. Deletion scope is restricted to the explicitly listed dataset/detector payloads and targeted detector compatibility code.
- This report records the proposed cleanup before destructive actions. A completion section will be appended with actual paths removed, measured bytes, verification, and remaining historical references.
