# FreshGuard AI — Phase 9 Automated Dataset Curation & External Dataset Verification

**Audit date:** 2026-10-31  
**Scope:** Separate, conservative candidate-manifest preparation and source research. No model training, external downloads, label changes, image moves, split changes, application edits, or checkpoint changes.

## Executive summary

- Recomputed SHA-256 values directly from **37,762 local vegetable image rows**; no recorded inventory hash mismatched and no vegetable row lacked a hash.
- All **20 known Fresh/Rotten exact-image conflict groups (41 rows)** were excluded in full from the non-conflict candidate subset. Every conflict row is `EXCLUDED_CONFLICT`; all group details are in `conflict_exclusion_detail.csv` and duplicated in the candidate manifest. They remain unresolved, not relabelled.
- Identified **4,686 same-category/same-label exact-duplicate groups** and excluded **5,692 extra rows**, retaining a deterministic representative row for each group. No duplicate group had retained rows assigned across different existing splits.
- Pillow verified and fully loaded all **37,762 files**. There were **0 missing, unreadable, or invalid-size images**. Deterministic triage flagged **3 low-contrast Carrot Rotten images**. These remain present and marked `FLAGGED_QUALITY`.
- After conflict exclusion, same-label duplicate reduction, and quality flags, **32,026 unique label-consistent, readable rows remain for further review**: Potato 2,497; Tomato 13,504; Carrot 11,202; Cucumber 1,785; Bell Pepper 3,038; Onion 0. Every one is `FLAGGED_PROVENANCE` because per-image provenance/rights for the Mendeley aggregation remain unverified. There are **0 `INCLUDED_CANDIDATE` rows** and no claim of training readiness.
- No external dataset was downloaded. Reported external counts remain publisher/paper claims unless explicitly marked independently verified.

## Stage A — Automated local curation

### Status totals

| Curation status | Rows | Meaning |
|---|---:|---|
| `EXCLUDED_CONFLICT` | 41 | All image rows in 20 exact-byte groups whose original labels conflict |
| `EXCLUDED_DUPLICATE` | 5,692 | Extra same-category/same-label exact copies; one deterministic path retained |
| `FLAGGED_QUALITY` | 3 | Readable Carrot images with low-contrast thumbnails; human inspection needed |
| `FLAGGED_PROVENANCE` | 32,026 | Unique, readable, label-consistent candidates awaiting per-image source/rights verification |
| `INCLUDED_CANDIDATE` | 0 | No image passed the provenance gate |

No image was deleted. `candidate_manifest.csv` retains one row for every original inventory row and provides the original image path, original Fresh/Rotten label, source identifier, recorded and recomputed hashes, duplicate/conflict group ID, existing `split` value, quality fields, status, and reason. Original split assignments were copied, not changed. `existing_split` is blank in the source inventory; the populated `split` column was preserved.

### Category summary

“Candidate after filters” means the remaining unique rows after conflicts, duplicate extras, and the three quality flags are removed from the clean subset. These rows remain provenance-flagged and are not training-approved.

| Category | Original rows (Fresh / Rotten) | Unique exact hashes | Conflict groups / rows excluded | Same-label duplicate rows excluded | Quality flags | Remaining candidate Fresh / Rotten | Fresh:Rotten ratio after filters |
|---|---:|---:|---:|---:|---:|---:|---:|
| Potato | 2,538 (1,151 / 1,387) | 2,497 | 0 / 0 | 41 | 0 | 1,146 / 1,351 | 0.848:1 |
| Tomato | 17,695 (13,681 / 4,014) | 13,507 | 3 / 6 | 4,185 | 0 | 10,882 / 2,622 | 4.150:1 |
| Onion | 0 (0 / 0) | 0 | 0 / 0 | 0 | 0 | 0 / 0 | n/a |
| Carrot | 12,318 (9,899 / 2,419) | 11,222 | 17 / 35 | 1,078 | 3 | 9,225 / 1,977 | 4.666:1 |
| Cucumber | 2,118 (1,104 / 1,014) | 1,785 | 0 / 0 | 333 | 0 | 818 / 967 | 0.846:1 |
| Bell Pepper | 3,093 (1,601 / 1,492) | 3,038 | 0 / 0 | 55 | 0 | 1,590 / 1,448 | 1.098:1 |

Original rows are inventory records; unique hashes collapse byte-identical content. No phase 9 augmentation was added. The inventory does not provide a reliable independent-original-versus-augmented distinction for the upstream aggregated source, so do not treat repeated files as independent photos.

### Quality rules and result

The script verifies then loads each image with Pillow, records dimensions/format/file size, and computes grayscale standard deviation/range on a 64×64 thumbnail. It flags files under 1 KiB, either dimension under 64 px, aspect ratio above 5:1, unreadable files, or near-uniform thumbnails (`stddev < 5` and range `< 15`). These deterministic thresholds only identify images for human inspection; they do not assess freshness.

The three flags were all Carrot Rotten images, 224×224 JPEGs, due to near-uniform thumbnails. Paths are listed in `image_quality_report.csv` and statuses in `candidate_manifest.csv`. No undersized, missing, or unreadable files were found. Low contrast is a review signal, not proof an image is blank.

## Conflict and duplicate verification

- The script recomputed all vegetable file hashes and found **20 label-conflict SHA-256 groups**, all matching known Phase 8 conflicts: 17 Carrot and 3 Tomato. All 41 group rows are excluded; every row has `known_phase8_conflict=True` in `conflict_exclusion_detail.csv`.
- No same SHA-256 was shared across different normalized vegetable categories.
- Same-label duplicates: 4,686 groups; 5,692 duplicate extra rows excluded. The duplicate report records all group members, the retained canonical path, source split and whether a repeated group spanned splits. **0 groups spanned existing splits.**
- Hash-based duplicate identity is byte-exact. Previously reported dHash pairs remain candidates only; no new perceptual duplicate claim is made.

## Stage C — External dataset verification

`external_dataset_research.csv` records source, URL/DOI, access date, reported and independently verified counts, labels, original/augmented status, licenses, commercial-use status, attribution, provenance, overlap risk, and a decision from the requested vocabulary.

Highlights checked on 2026-10-31:

1. **Five-fruit/five-vegetable Kaggle lead:** the Kaggle landing URL returned the dataset title, but detailed current file/version/license metadata was not readable through the research interface. Downloadable status and current-version match remain unverified. The 2022 paper reports 12,000 original images across ten types and roughly 70% single-object photos; vegetable Fresh/Rotten counts in the paper are Potato 615/585, Carrot 620/580, Tomato 604/596, Cucumber 608/593, Bell Pepper 611/591. These counts were not verified against the current archive. The paper says sources included Kaggle, Google, Bing and phone capture, creating overlap and rights questions. Decision: **PROMISING – VERIFY BEFORE DOWNLOAD**. [Paper and reported counts](https://www.mdpi.com/1424-8220/22/21/8192), [Kaggle page](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset).
2. **Cucumber 9rs9vmm2bv:** Mendeley record reports exactly 1,000 images, 500 Good and 500 Bad, CC BY 4.0, collected in local markets and observed during storage. Its narrative mentions removing damaged/spoiled samples and then tracking storage deterioration; how that maps to Good/Bad is unclear. Decision: **CONDITIONAL – LABEL SEMANTICS UNCLEAR**. [Mendeley record](https://data.mendeley.com/datasets/9rs9vmm2bv/1).
3. **Cucumber zncrtr2yhn:** record says over 500 images, balanced Good/Bad, black background/daylight capture; Bad includes damage, disease, bruises, irregular shape, discoloration or rot. Exact counts and Fresh/Rotten mapping are unverified. Decision: **CONDITIONAL – LABEL SEMANTICS UNCLEAR**. [Mendeley record](https://data.mendeley.com/datasets/zncrtr2yhn/1).
4. **Onion Mendeley 42bcyncfhy:** latest v2 metadata reports 16,300 bulb-and-leaf images and CC BY 4.0; the user-linked v1 reported 24,000. Labels are healthy/unhealthy, not Fresh/Rotten. No archive was downloaded. Decision: **CONDITIONAL – LABEL SEMANTICS UNCLEAR**. [Mendeley v2 record](https://data.mendeley.com/datasets/42bcyncfhy/2).
5. **Onion Zenodo 20254934:** record reports 16,300 images (12,260 bulbs, 4,040 leaves) and healthy/unhealthy organization, but no license value was displayed. It likely belongs to the same author/title record family as the Mendeley dataset; identity/overlap is unverified. Decision: **CONDITIONAL – LABEL SEMANTICS UNCLEAR**. [Zenodo record](https://zenodo.org/records/20254934).
6. **AgriFreshNET:** Mendeley record reports 14,500 images, 24 classes, Fresh/Semi-Fresh/Rotten, and CC BY 4.0, but the target vegetable class names/counts were not visible. Do not collapse Semi-Fresh automatically. Decision: **INSUFFICIENT INFORMATION**. [Mendeley record](https://data.mendeley.com/datasets/42m5tb7yv9/1).
7. **Tomato_detection:** record reports 800 base images and a 1,600-image YOLO export with Fresh/Rotten boxes and CC BY 4.0. The description says 400 originals were expanded to 1,200 training samples, but does not make clear whether these are total augmented training samples or additional variants. Per-class counts, rights chain and overlap remain unverified. Decision: **PROMISING – VERIFY BEFORE DOWNLOAD**. [Mendeley record](https://data.mendeley.com/datasets/vy5y8p2kdb/1).

These license statements are record-level only. CC BY 4.0 permits commercial sharing/adaptation of material actually covered by the license subject to attribution and other terms; it does not establish that every image in an aggregated dataset was authorized. See [CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/). No external archive was downloaded, and no external image-level duplicate comparison was possible.

## Stage D — Overlap risk

No external images were available locally, so the report makes no image-level overlap claims. The local Mendeley FoodClass source is itself described as aggregated from public repositories, making overlap with the Kaggle/paper dataset and other online sources possible. The Onion Mendeley versions and Zenodo record share authors/title and should be treated as a likely related record family, not independent data. See `overlap_risk_report.md` for source-specific risks and a later approved hash-comparison plan.

## Stage E — Readiness

`final_readiness_matrix.csv` uses only the allowed decisions. Current decisions:

- **Potato — PROVENANCE UNVERIFIED.** Best internal candidate for further human review, but no image clears the provenance gate.
- **Tomato — LABEL SEMANTICS UNCLEAR.** Exclude all 3 conflict groups; substantial Fresh skew remains.
- **Onion — NEEDS MORE DATA.** No local data; external sources do not verify Fresh/Rotten labels.
- **Carrot — LABEL SEMANTICS UNCLEAR.** Exclude all 17 conflicts; substantial Fresh skew and 3 low-contrast flags remain.
- **Cucumber — LABEL SEMANTICS UNCLEAR.** External Good/Bad is broader than Fresh/Rotten and prior local Rotten review was ambiguous.
- **Bell Pepper — LABEL SEMANTICS UNCLEAR.** Prior Rotten sample was questionable; no item-level approval.

Potato may proceed to a **non-training validation stage** focused on provenance and manual review. None of the six categories is cleared for training or application integration.

## Verification and preservation

- Candidate manifest rows: 37,762; status counts reconcile to 41 + 5,692 + 3 + 32,026 = 37,762.
- Every `EXCLUDED_CONFLICT` row belongs to one of 20 known Phase 8 conflict hashes; no known conflict group remains as `FLAGGED_PROVENANCE` or `INCLUDED_CANDIDATE`.
- Duplicate report: 4,686 groups, 5,692 excluded extra rows, zero split-spanning groups.
- Candidate rows preserve the inventory `split` assignment. No original split files were edited or images moved.
- File check: 37,762 present and Pillow-readable; recomputed hashes had 0 mismatches and 0 missing hashes.
- No external data was downloaded; no training/model inference was performed.
- Only new artifacts were written under `ml-service/evaluation/phase9_automated_curation/`. Phase 6–8 artifacts, original inventory/images, model, application and split files were not modified.

## Files in this phase

`final_report.md`; `candidate_manifest.csv`; `category_summary.csv`; `duplicate_exclusion_report.csv`; `image_quality_report.csv`; `external_dataset_research.csv`; `onion_dataset_assessment.md`; `overlap_risk_report.md`; `final_readiness_matrix.csv`; `curate_phase9.py`; `README.md`; and the supplementary `conflict_exclusion_detail.csv`.
