# Phase 13 — Reliable vegetable dataset development

**Scope:** read-only source audit and data-collection planning. No model training, checkpoint changes, application changes, external downloads, relabeling, or split changes were performed.

## Contents

- `final_report.md` — consolidated findings and recommendations.
- `vegqual_assessment.md` — VegQual source, labels, annotations, provenance, and limits.
- `agrifreshnet_assessment.md` — exact metadata blockers and possible three-class use.
- `local_source_recovery.csv` — one row per existing local FoodClass inventory row; source/conflict status only, not a training manifest.
- `image_collection_protocol.md` — proposed original capture process and image targets.
- `freshness_labeling_guide.md` — Fresh / Rotten / Uncertain criteria.
- `combined_manifest_schema.csv` — header-only future schema; it contains no images or split assignments.
- `category_development_plan.csv` — existing row counts and per-category next steps.
- `final_readiness_matrix.csv` — current readiness decisions.

## How to read the counts

FoodClass counts are existing inventory rows with the folder-derived `Fresh`/`Rotten` label names. They are not independently verified ground truth and do not clear rights. The archive reports 85,012 images; the local inventory records 69,661 relevant produce rows. VegQual and AgriFreshNET numbers are publisher/author-reported unless stated otherwise. No new external images were downloaded, so acquired count is zero.

`local_source_recovery.csv` preserves existing split values solely as read-only reference. `EXCLUDED_CONFLICT` marks rows from known exact-hash label conflicts. Every other row remains `PENDING_SOURCE_VERIFICATION`; absence of a conflict does not mean training approval.

Future manifest status values are `CANDIDATE`, `EXCLUDED_CONFLICT`, `EXCLUDED_DUPLICATE`, `EXCLUDED_UNVERIFIED_SOURCE`, `EXCLUDED_UNCLEAR_LABEL`, and `PENDING_SOURCE_VERIFICATION`. The combined manifest CSV is header-only; no candidate rows or new splits were created.

## Preservation

No original files or reports were overwritten. The existing six-fruit checkpoint, application code, datasets, labels, and split manifests were not modified.
