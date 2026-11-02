# Phase 8 — Manual Review Recording and Dataset Validation

**Date:** 2026-10-31  
**Scope:** Read-only validation of the existing vegetable inventory plus separate review-decision artifacts. No source labels or images changed. No model training, downloads, or application edits.

## Human assessment captured separately

User-provided overall statement: **“Most images appear correctly labelled during initial visual inspection.”** It is recorded as an overall impression only. It is not an individual image decision and did not change any image status.

The 81 individual entries in `review_decisions.csv` are all **PENDING**. Each row has a blank review date and reviewer note until a specific decision is made. No image was automatically approved.

## Dataset integrity validation

The full vegetable subset of the existing inventory was checked directly from disk. For every inventory path, the check tested file existence and used Pillow to verify and fully load the image. Results: **37,762 rows checked; 0 missing files; 0 unreadable images; 0 invalid/empty dimensions reported by Pillow.** These are current checks performed on 2026-10-31. They do not establish label correctness or image-level licensing. One representative image for each of the 20 exact-byte conflict groups was also visually inspected at contact-sheet scale; because rows within a group have identical bytes, this covered all 20 unique images and all 41 conflict rows at the image-content level. Visual observations are recorded in `conflict_review.csv`; they are not approvals or resolutions.

| Category | Fresh | Rotten | Total/readable | Unique SHA-256 | Repeated exact-hash groups / excess rows | Conflicting label groups / rows | Review items pending |
|---|---:|---:|---:|---:|---:|---:|---:|
| Potato | 1,151 | 1,387 | 2,538 | 2,497 | 39 / 41 | 0 / 0 | 8 |
| Tomato | 13,681 | 4,014 | 17,695 | 13,507 | 3,423 / 4,188 | 3 / 6 | 14 |
| Onion | 0 | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| Carrot | 9,899 | 2,419 | 12,318 | 11,222 | 973 / 1,096 | 17 / 35 | 43 |
| Cucumber | 1,104 | 1,014 | 2,118 | 1,785 | 220 / 333 | 0 / 0 | 8 |
| Bell Pepper / Capsicum | 1,601 | 1,492 | 3,093 | 3,038 | 51 / 55 | 0 / 0 | 8 |

The category-specific percentages, counts, duplicates, and review manifest totals are in `category_validation.csv`. All vegetable inventory rows are from Mendeley FoodClass v2. Exact duplicate counts mean identical SHA-256 byte content; repeated groups are not necessarily independent images. No near-duplicate re-analysis was run. The prior dHash report contains candidates, not confirmed duplicates.

### Manifest consistency

- Phase 7 `manual_review_manifest.csv`: 81 rows, 81 unique paths; every path is present in the vegetable inventory and exists on disk.
- `review_decisions.csv`: 81 matching image paths; all 81 decision values are PENDING.
- `conflict_review.csv`: 41 rows representing all 20 groups; each group contains identical SHA-256 and both original labels. All remain unresolved.
- Category totals reconcile to Fresh + Rotten rows. Onion has no manifest images because it has no existing inventory records.

## Conflicting exact-image groups

The vegetable subset contains **20 unresolved groups: 17 Carrot groups (35 rows) and 3 Tomato groups (6 rows)**. The conflict CSV lists every path, original category/condition, normalized label, hash, source, source identifier, source URL, license field, attribution and split. Each is marked unresolved pending a specific human decision. No majority-vote or automatic resolution was applied. At contact-sheet scale, the carrot representatives generally appeared intact with no unmistakable spoilage; the tomato representatives showed differing surface markings/discoloration. This may indicate label inconsistency, but no individual/group decision is assigned. The broader Phase 11B report records 336 conflicting groups / 673 rows across all categories; Phase 8’s conflict file is scoped to the six vegetables.

## Provenance and license status

The one source contributing vegetable examples is the [Mendeley FoodClass v2 record](https://data.mendeley.com/datasets/5fjkkv5xgt/2), which reports CC BY 4.0 and describes a merged set collected from public repositories. The local Phase 11B report notes its archive checksum matched the publisher listing.

The [CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/) permits sharing and adaptation for commercial purposes for material actually licensed under it, with attribution, license link, and change indication. **This does not verify that each aggregated image was licensed by its rights holder.** For each image, original creator/source and whether the record license covers it remain UNKNOWN. Accordingly, provenance verification is PARTIAL and image-level commercial permission is UNKNOWN / NOT VERIFIED. `provenance_status.csv` records the detail.

## Items still pending

- **Individual decisions:** all 81 review-manifest images remain PENDING (Potato 8; Tomato 14; Carrot 43; Cucumber 8; Bell Pepper 8; Onion 0). None was individually approved, rejected or marked uncertain. Exact paths, hashes, original labels and source fields are in `review_decisions.csv`; the overall assessment remains separate.
- **Conflict groups:** all 20 groups / 41 rows remain unresolved: `VEG-CONFLICT-001` through `VEG-CONFLICT-020` (17 Carrot, 3 Tomato). See `conflict_review.csv` for exact membership.
- **Provenance:** all 37,762 vegetable image rows have unverified per-image original provenance and rights beyond the Mendeley record-level CC BY 4.0 statement.
- **Labels:** no written, independently adjudicated Fresh/Rotten label ground truth was created. The prior spot review is limited to a few samples.
- **External source readiness:** not assessed/downloaded in this phase; no external dataset added.

## Readiness decision

This phase validates files and records review status; it does **not** establish training readiness. Do not train or integrate a vegetable model based on these checks. Before a future training decision, adjudicate individual review items and conflict groups, complete a written category-consistent freshness rubric, resolve or explicitly exclude unresolved rights/provenance, and design a new source/duplicate-aware split while preserving existing data and the untouched test set.

## Files created and checks performed

Created in this directory: `review_decisions.csv`, `conflict_review.csv`, `category_validation.csv`, `provenance_status.csv`, `final_report.md`, and `README.md`.

Checks performed: full file-existence check and Pillow verify/load for 37,762 rows; visual inspection of one image per exact-hash conflict group (20 unique images representing 41 rows); exact SHA-256 grouping and conflict recomputation; category count reconciliation; review-manifest path/status reconciliation. No application tests or model inference were run because this is a dataset audit. No source images, labels, manifests, splits, reports or checkpoints were changed.
