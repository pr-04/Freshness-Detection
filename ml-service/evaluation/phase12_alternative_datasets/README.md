# Phase 12 — Alternative dataset investigation

**Outcome: metadata research completed; no new dataset passed every acquisition gate. No archives or images were downloaded.** The phase12 staging folder contains only a README.

## Deliverables

- `final_report.md` — findings and acquisition/readiness decision.
- `dataset_comparison.csv` — candidate source comparison with reported vs verified details.
- `source_verification.csv` — primary source, version, access, license and provenance findings.
- `label_semantics_report.md` — class names and why labels were not collapsed.
- `onion_assessment.md` — bulb-specific limits and absence of a Fresh/Rotten mapping.
- `category_coverage.csv` — Phase 12 acquisition counts (zero) and separate local inventory counts where present.
- `download_manifest.csv` — explicit no-download records; no fabricated checksums.
- `image_integrity_report.csv` and `duplicate_overlap_report.csv` — NOT RUN for new sources because none were staged.
- `final_readiness_matrix.csv` — category decisions using the requested vocabulary.
- `scripts/hash_images.py` — read-only SHA-256/dHash, exact duplicate grouping, band-indexed dHash near-duplicate candidates, and local exact/near-hash comparison for a future separately approved staged dataset.
- `scripts/check_image_integrity.py` — read-only Pillow validation and basic image-quality triage.

## Re-run checks after an approved acquisition

Install Pillow if necessary, then run from the project root:

```powershell
python -m pip install Pillow
python ml-service/evaluation/phase12_alternative_datasets/scripts/check_image_integrity.py `
  --dataset-root ml-service/datasets/external_staging/phase12/<approved-source>/extracted `
  --output-csv ml-service/evaluation/phase12_alternative_datasets/recheck/image_integrity.csv
python ml-service/evaluation/phase12_alternative_datasets/scripts/hash_images.py `
  --dataset-root ml-service/datasets/external_staging/phase12/<approved-source>/extracted `
  --inventory ml-service/datasets/expansion_15/dataset_inventory.csv `
  --output-dir ml-service/evaluation/phase12_alternative_datasets/recheck/hashes
```

Perceptual-hash matches are candidates for manual review, not confirmed duplicates. Scripts never download, edit, relabel, move, or delete source data.

## Preservation

No existing dataset, label, split, model checkpoint, or application source was modified. Phase 11 reports and staging were preserved.
