# Phase 11 Freshness44 acquisition and verification assessment

**Outcome: NO-GO for acquisition in this phase.** The publisher page is reachable through the research browser, but its file listing and archive sizes are not exposed. The Mendeley public API and web host did not resolve from the project shell. The record-level CC BY 4.0 declaration does not resolve rights and attribution obligations for images inherited from five source datasets. Phase 11 therefore stopped before downloading, as required by the acquisition gate.

The records in this directory distinguish actual acquired counts (zero; no archive was acquired) from paper-reported Fresh/Rotten counts. They do not claim that paper counts are the cleaned derivative's counts.

## Files

- `final_report.md` — decision and summary.
- `source_verification.md` — publisher record, API, paper/original comparison, rights and access findings.
- `archive_manifest.csv` — no archive acquired; no fabricated checksum.
- `category_counts.csv` — acquired count (zero) and paper-reported original counts in separate columns.
- `image_integrity_report.csv` — not run because there are no acquired images.
- `duplicate_report.csv` — not run because there are no acquired images.
- `overlap_report.csv` — local source status and overlap limits; no external comparison claimed.
- `split_integrity_report.md` — source split assertions and why leakage could not be evaluated.
- `final_readiness_matrix.csv` — category decisions based on actual acquisition and provenance evidence.
- `scripts/hash_images.py` — reproducible file hashing, Pillow readability/dimension checks, perceptual-hash candidate generation and local exact-hash comparison for a future separately approved archive.
- `scripts/check_image_integrity.py` — separate read-only Pillow image integrity/dimension scan.

## Re-run after a future approved acquisition

Install Pillow if needed, then run from the project root:

```powershell
python -m pip install Pillow
python ml-service/evaluation/phase11_freshness44/scripts/hash_images.py `
  --dataset-root ml-service/datasets/external_staging/phase11/freshness44_cleaned/extracted `
  --inventory ml-service/datasets/expansion_15/dataset_inventory.csv `
  --output-dir ml-service/evaluation/phase11_freshness44/recheck
python ml-service/evaluation/phase11_freshness44/scripts/check_image_integrity.py `
  --dataset-root ml-service/datasets/external_staging/phase11/freshness44_cleaned/extracted `
  --output-csv ml-service/evaluation/phase11_freshness44/recheck/image_integrity_report.csv
```

The script reads the selected extracted directory and the existing inventory. It writes only into the requested output directory. Perceptual-hash matches are candidates for review, not confirmed duplicates. It does not alter images, labels, splits, or source manifests. Phase 11 did not run it because the dataset was not acquired.

## Preservation

No archive was downloaded or extracted. No existing dataset, image, label, split, checkpoint, or application code was changed. The separate staging location contains only a README documenting the decision.
