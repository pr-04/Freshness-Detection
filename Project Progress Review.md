# FreshGuard AI — Project Progress Review

**Review date:** 2 November 2026  
**Scope:** Current source tree following the MobileNetV2-only cleanup. Historical dataset and detector research is retained in evaluation reports; it does not describe the active application architecture.

## Executive summary

FreshGuard AI has a React scanner connected through an Express API to a Python FastAPI inference service. The active ML service runs the trained MobileNetV2 binary freshness classifier directly on the complete uploaded image and returns Fresh, Rotten, or Uncertain. No object detector is used by the active application.

The user selects one of six categories: Apple, Banana, Guava, Orange, Pomegranate, or Strawberry. MobileNetV2 predicts only Fresh/Rotten and cannot identify or validate that selected category. Dataset caches and prepared training images have been removed; the existing classifier checkpoint, metadata, and evaluation reports remain. No vegetable data is connected to the running model.

## Work completed

### Frontend and scan experience

- React 19/Vite app with React Router, Tailwind styling, shared layout, navigation, landing page, and scanner page.
- Scanner supports JPEG/JPG/PNG upload, drag/drop, preview, replace/remove, client-side size/type checks, loading, result, error, and reset states.
- Camera capture is implemented using browser media APIs. Camera access starts only on user action; users can capture, retake, and choose whether to submit the image.
- Scanner calls the Express API rather than the Python service directly.
- Dashboard reads saved scan records and summarizes scans plus supported Fresh/Rotten results. History, inventory, and analytics routes remain placeholders.

### Express API and persistence

- Express scan routes accept image uploads and forward the uploaded bytes to FastAPI using the configured `ML_SERVICE_URL` (default `http://127.0.0.1:8013`).
- The API validates the ML response contract (`mock: false`, success, selected category, classifier, scores, and uncertainty) before saving scan metadata.
- New scan records contain direct classification fields. MongoDB is used when connected; an in-memory fallback is used otherwise. Existing database documents are not deleted; detector-specific fields are no longer exposed by the API or rendered in the application.
- The service exposes health and scan create/list/read/delete routes. Upload files are served from the backend uploads directory; retention/cleanup still needs product-level policy.

### ML service and model work (Parts 6–10)

- FastAPI service has `/health` and `/predict`, upload validation, supported-image checks, 10 MB size limit, and in-memory image handling.
- The initial mock prediction was replaced by real MobileNetV2 inference. The classifier is loaded once and reused; CPU inference is supported, and inference errors do not fall back to mock results.
- The service validates the upload and runs the classifier on the complete image using the saved resize and normalization metadata.
- Freshness outputs are dataset labels (`fresh` or `rotten`) and classifier class scores. They are not freshness percentages, food-safety assessments, or edibility guarantees.
- The classifier was trained from the existing Hugging Face dataset preparation workflow. The audit records 3,200 readable source images across eight fruits, with 200 Fresh and 200 Rotten per fruit. Existing evaluation was 99.375% on its 480-image held-out split; this is an in-domain result and does not establish generalization to new sources or produce types.

### Historical Phase 11 dataset preparation

- Phase 11A/11B audited multiple public sources and prepared a freshness inventory. The image payloads, archives, and training splits were subsequently removed during project cleanup; retained reports and manifests are historical records, not active model inputs.
- The historical inventory recorded 71,661 valid image rows before cleanup, from Hugging Face and Mendeley sources. Its category counts, source notes, and split audit remain documented in the retained reports. No vegetable data was used to train the current checkpoint.
- Zenodo's public metadata reported CC BY 4.0 and an archive under 2 GB, but download failed because the runtime could not resolve `zenodo.org`. Kaggle's public metadata reported CC0 and a 920,890,427-byte archive, but the documented download endpoint returned HTTP 404 and no Kaggle CLI credentials were configured. Neither archive is included.
- An exact hash audit found 58,710 unique SHA-256 hashes. A perceptual dHash audit found 304,603 likely pairs in 4,000 connected groups; 2,210 groups crossed the initial split boundaries and were reassigned together. Final exact-hash crossings and candidate-pair split crossings are both zero. The 70/15/15 target shifted to 56,316/7,791/7,554 (about 78.6/10.9/10.5) to keep detected near-duplicate groups together. Similarity pairs are candidates for human review, not confirmed duplicate identities.
- No model training, replacement, or application integration occurred in Phase 11B.

## Current supported behavior and limitations

| Capability | Current status |
|---|---|
| Produce identity | Selected by the user; not predicted or verified by the model |
| Freshness label | `fresh` / `rotten`, with an `Uncertain` result below the configured confidence threshold |
| Dataset scope | The checkpoint was trained on eight fruit categories; the application currently permits six user-selected categories |
| Image input | Whole image is resized and classified; no object crop or bounding box is created |
| Food safety | Not assessed; model output is visual classification only |
| Data readiness | Suitable for review; not ready for detector training and not cleared for classifier training until image provenance, labels, and samples receive review |

## Verification performed and evidence

### Previously recorded verification

- Earlier Part 10A smoke records document the historical detector pipeline; those results do not describe the current application.
- The retained classifier evaluation report records 99.375% accuracy on the original 480-image test split. That historical result was not rerun during cleanup.

### Historical Phase 11B checks

- Mendeley archive download completed; the downloaded byte count and SHA-256 matched source metadata.
- Mendeley archive layout and file types were inspected; all selected target images were decoded with Pillow and hashed. No selected image was rejected.
- The final inventory and split manifests contained 71,661 rows at the time they were audited. Dataset image paths no longer exist after cleanup.
- Independent manifest check: 58,710 unique exact hashes; zero exact-hash groups cross splits; zero dHash candidate pairs cross splits after reassignment.
- Python syntax compilation passed for `prepare_expansion.py`, `audit_near_duplicates.py`, and `finalize_manifests.py`. Required output files and JSON artifacts were checked.
- Zenodo acquisition did not pass; Kaggle acquisition was not completed. No end-to-end frontend/API/model runtime test was run during this Phase 11B preparation turn.

## Remaining work

1. Run a fresh end-to-end walkthrough of React → Express → FastAPI with the classifier loaded before any release claim. Review upload retention, persistence, and production configuration.
2. Any future model training requires a newly approved dataset acquisition, rights review, label-quality checks, and source-aware splits because the prior training image payloads were removed.
3. Treat historical per-image audit outputs as reports only; their referenced local image files are no longer present.

## Key project documents

- [ML service guide](ml-service/README.md)
- [Phase 11A dataset audit](ml-service/datasets/expansion_audit.md)
- [Phase 11B preparation report](ml-service/datasets/expansion_15/preparation_report.md)
- [Phase 11B coverage table](ml-service/datasets/expansion_15/category_coverage.md)
- [Phase 11B reproducibility instructions](ml-service/datasets/expansion_15/README.md)

This review summarizes current code, retained reports, and the completed cleanup. It does not certify model accuracy outside its original test set, confirm third-party image rights beyond source metadata, or establish food safety.
