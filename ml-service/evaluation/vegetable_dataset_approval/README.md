# Phase 8 vegetable review and validation

This folder contains a separate manual decision workflow and read-only validation results. The existing dataset, Phase 7 artifacts, model, application, labels and splits are unchanged.

## Files

- `review_decisions.csv` — one row per image in the Phase 7 81-image manifest. All decisions start `PENDING`; date and note are blank until a human records an individual decision. Allowed decision values: `APPROVED`, `REJECTED`, `UNCERTAIN`, `PENDING`.
- `conflict_review.csv` — each image row in all exact-hash Fresh/Rotten conflict groups for these vegetables, with category, original label, hash, path, source, attribution fields and a non-decisional visual observation. All rows are unresolved.
- `category_validation.csv` — category counts, directly verified readable/missing/unreadable totals, exact duplicates, conflicts and review-manifest counts.
- `provenance_status.csv` — source-level publisher, dataset URL, record license, commercial-use status, attribution needs and verification state. Unknown per-image rights are explicitly marked UNKNOWN.
- `final_report.md` — findings and remaining pending work.

## Recording a decision

1. Review the specified image and its matching gallery card. For a conflict, compare all paths with the same `conflict_group_id` and SHA-256 together.
2. Write only an individual decision in a copy or controlled edit of `review_decisions.csv`: `APPROVED`, `REJECTED`, `UNCERTAIN`, or `PENDING`. Add a short evidence-based reviewer note and review date. Never infer a decision from the overall impression, a model output, or majority vote.
3. Keep the original label in `original_label`. A review decision documents human assessment; it does not rewrite source data. Preserve an audit trail of reviewer and prior values.
4. Keep conflicts unresolved until an explicit group/member decision is entered. If uncertain, use `UNCERTAIN`; do not force Fresh or Rotten.
5. Track licensing separately. Visual approval does not establish rights, provenance, or commercial-use permission.

## Recorded overall assessment

The user’s statement, “Most images appear correctly labelled during initial visual inspection,” is an overall observation recorded in `final_report.md`. It is not applied to any individual item; all 81 individual statuses remain `PENDING`.

## Reproducibility

Source data: `ml-service/datasets/expansion_15/dataset_inventory.csv` and Phase 7 `manual_review_manifest.csv`. Validation performed on 2026-10-31 with Python and Pillow. One representative image per exact-byte conflict group (20 unique images, covering all 41 conflict rows) was visually inspected at contact-sheet scale; observations are recorded but did not change the pending decisions. The validator checked existence and Pillow verify/load for every vegetable row, recomputed exact SHA-256 groups and contradictory normalized conditions, and checked manifest path/status consistency.
