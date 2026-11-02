# Phase 9 automated curation

This folder contains a reproducible, conservative review candidate set and source research. It does not contain a training dataset approval. No source images, labels, splits, model checkpoints or application code were changed.

## Files

- `curate_phase9.py` — rehashes and Pillow-validates local vegetable inventory images, applies deterministic image-quality flags, excludes conflicting groups and same-label exact-copy extras from the candidate status, preserves original split values, and regenerates local CSV outputs.
- `candidate_manifest.csv` — one row for every one of the 37,762 original vegetable inventory rows, with stable ID, path, category, original label, source, recorded/recomputed hashes, duplicate/conflict group, original split, quality and provenance status, inclusion status, and reason.
- `category_summary.csv` — original and post-curation counts, class distributions, conflicts, duplicates, quality flags, imbalance, and provenance gate.
- `duplicate_exclusion_report.csv` — every exact duplicate group member, retained representative, excluded extra and split-leakage check.
- `conflict_exclusion_detail.csv` — supplemental row-level detail for every excluded conflict member.
- `image_quality_report.csv` — readability, dimensions, format, size, thumbnail metrics and flags for every local vegetable image.
- `external_dataset_research.csv` — research sources, reported versus independently verified counts, label semantics, rights, overlap and suitability decisions. No external dataset files were downloaded.
- `onion_dataset_assessment.md` — Onion-specific source and label analysis.
- `overlap_risk_report.md` — source-overlap risks and later hash-check safeguards.
- `final_readiness_matrix.csv` — six-category decision table using the requested vocabulary.
- `final_report.md` — findings, counts, decisions and limitations.

## Reproduce local checks

From the project root, install Pillow if it is not already present, then run:

```powershell
python -m pip install Pillow
python ml-service/evaluation/phase9_automated_curation/curate_phase9.py
```

The script reads `ml-service/datasets/expansion_15/dataset_inventory.csv` and original image paths. It writes only CSV outputs in this Phase 9 directory.

## Rules and interpretation

The curation statuses are `INCLUDED_CANDIDATE`, `EXCLUDED_CONFLICT`, `EXCLUDED_DUPLICATE`, `FLAGGED_QUALITY`, and `FLAGGED_PROVENANCE`. Current precedence is conflict → duplicate extra → quality flag → provenance flag. Separate fields retain overlapping quality/provenance state. All unique readable rows that pass conflict/duplicate/quality triage are `FLAGGED_PROVENANCE`, because per-image rights for the aggregated Mendeley source are not verified. No row is fully training-approved.

Quality thresholds: file under 1 KiB; image dimension under 64 px; aspect ratio over 5:1; or a 64×64 grayscale thumbnail with standard deviation under 5 and range under 15. Pillow verify/load errors are also flagged. These rules are deterministic triage only, not freshness labels or human judgments. No flagged image is deleted.

Conflict groups are never resolved automatically. Every row of every conflicting exact-hash group is excluded. Same-label exact duplicates are reduced to one deterministic canonical path, while the original files and split assignments remain untouched. Perceptual similarity candidates are not confirmed duplicates.

For external research, `reported` means the publisher/paper says the value; `independently verified` means checked against source files/metadata. Since external downloads were prohibited, most archive-level counts and overlaps remain unverified. Do not infer commercial-use permission from an aggregate record license without rights/provenance review for the constituent images.
