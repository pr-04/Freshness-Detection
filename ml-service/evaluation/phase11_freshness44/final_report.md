# FreshGuard AI — Phase 11 Freshness44 Acquisition, Verification and Dataset Integration Assessment

**Review date:** 2026-10-31  
**Decision:** **NO-GO for acquisition; no dataset acquired.**  
**Training/integration:** Not performed.

## Summary

The cleaned Freshness44 Mendeley record is accessible as a landing page, but its actual downloadable files, names, sizes, README, directory structure, categories, labels, image counts, and split manifests could not be inspected. The shell could not resolve the Mendeley web or API hosts. The record declares CC BY 4.0, but Freshness44 is described as a merge of five public datasets and the accessible record does not resolve the constituent images' source licenses or attribution requirements. The user's pre-download checks therefore did not pass; no archive download was attempted.

**Actual archive/image counts:** zero acquired for all categories. All paper figures are kept in separate `paper_*_reported` columns in `category_counts.csv` and must not be interpreted as counts in the cleaned derivative.

## Category readiness

| Category | Acquired | Paper Fresh / Rotten reference | Decision |
|---|---:|---:|---|
| Apple | 0 | 3,468 / 4,263 | PROVENANCE UNVERIFIED |
| Banana | 0 | 3,513 / 3,605 | PROVENANCE UNVERIFIED |
| Guava | 0 | 1,352 / 1,329 | PROVENANCE UNVERIFIED |
| Orange | 0 | 3,164 / 3,443 | PROVENANCE UNVERIFIED |
| Pomegranate | 0 | 6,140 / 1,387 | PROVENANCE UNVERIFIED |
| Strawberry | 0 | 803 / 795 | PROVENANCE UNVERIFIED |
| Potato | 0 | 602 / 562 | PROVENANCE UNVERIFIED |
| Tomato | 0 | 1,905 / 2,504 | PROVENANCE UNVERIFIED |
| Carrot | 0 | 605 / 507 | PROVENANCE UNVERIFIED |
| Cucumber | 0 | 833 / 692 | PROVENANCE UNVERIFIED |
| Bell Pepper / Capsicum | 0 | 1,634 / 2,108 | PROVENANCE UNVERIFIED |
| Onion | 0 | Not reported | NOT AVAILABLE |

The eleven pairs above are the Freshness44 paper's reported counts, as recorded during Phase 10. They are not independently verified against either Kaggle or the cleaned Mendeley archive. The cleaned derivative's exact category coverage remains unknown. Onion is not reported in the paper's category table or the derivative description; it remains a separate missing-data category.

No category is verified for the next preparation stage. If source files become accessible and rights are resolved, image-level inspection may support a later preparation decision; successful download alone would still not imply training readiness.

## Verification results

- **Landing page:** accessible through research browser; publisher, title, contributor, date, version, DOI, record-level license, derivative description, and Kaggle related link were confirmed.
- **Actual file metadata/content:** not accessible; names, sizes, archive checksum, README, class counts, image counts, and split counts remain unknown.
- **Connectivity:** shell requests to `data.mendeley.com` and `api.data.mendeley.com` failed with host DNS resolution errors. The network issue is limited to that shell's current resolution; it is not evidence that the source is globally unavailable.
- **Free space:** approximately 124.6 GB reported on the C: drive. No download was scheduled.
- **Image integrity / exact duplicates / near duplicates:** not run; no Freshness44 files acquired.
- **Local overlap:** not run at image level; no external image hashes exist. Metadata suggests possible overlap due to the five-source aggregation. The existing local Phase 9 audit is not evidence of overlap or non-overlap with Freshness44.
- **Split leakage:** not evaluated. The record's claim of train/test splitting is not enough to establish image/source grouping or leakage status.
- **License/provenance:** insufficient to approve acquisition under this task's gates. The record shows CC BY 4.0, while rights and attribution for the five upstream image sources are undocumented in the accessible page.
- **Preservation:** no archive/data/image/label/split/checkpoint/application files were modified; no training or model integration occurred.

## Blockers and next steps

1. Obtain access to the publisher's actual file list and archive metadata (filename, bytes, checksum, README, and directory listing) through the official Mendeley UI/API. Resolve shell DNS/network access or provide those publisher-downloaded metadata files for review.
2. Ask the contributor to identify the five upstream datasets and document their licenses, attribution requirements, and per-image provenance/rights. Do not infer coverage from the derivative record license alone.
3. Inspect README, category definitions, Fresh/Rotten rubric, counts, original-versus-augmented status, duplicate-removal method, and split manifests before approving any archive download.
4. Recheck per-archive and total size limits and available disk space immediately before any later approved download.
5. If and only if those gates pass, obtain explicit approval for acquisition; preserve the original archive, checksum, source metadata, and attribution; then run the included integrity/hash script and compare against local inventories before considering a new group-aware split.
6. Keep Onion separate and acquire an independently verified Onion Fresh/Rotten source in a later phase.

## Deliverables and checks

Created the requested reports/manifests in this evaluation directory and a separate, empty staging location with a rationale README. Actual downloaded archives: 0. Integrity checks run on Freshness44 images: none. See `source_verification.md`, `category_counts.csv`, `archive_manifest.csv`, `image_integrity_report.csv`, `duplicate_report.csv`, `overlap_report.csv`, and `split_integrity_report.md` for explicit details.
