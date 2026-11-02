# FreshGuard AI — Phase 12 Alternative Dataset Investigation and Acquisition

**Review date:** 2026-10-31  
**Outcome:** **NO-GO for new acquisition.** No candidate passed source, label semantics, provenance/rights, and archive metadata gates together.  
**New dataset downloads:** 0. **Model training/integration:** not performed.

## Decision summary

Alternative records were investigated for produce-level Fresh/Rotten data. The most directly matched sources have one or more blockers: the FruQ-DB record has no displayed license and contains YouTube time-lapse frames; FoodClass is already represented in the local inventory but is aggregated from unspecified public repositories; the Onion collection labels bulbs Healthy/Unhealthy and leaves license rights blank on Zenodo; the Kaggle Freshness44 page provides no readable metadata and Kaggle CLI/authentication was unavailable; and other Mendeley sources either use broader/ambiguous condition labels or omit underlying image provenance.

No archives were downloaded. The Phase 12 staging location contains only a README. Disk space was checked (about 124.1 GB free on C:); capacity was not the blocker. A dataset that fits the size cap still must pass the content, label, and rights checks.

## Sources investigated

| Source | What the publisher/source reports | Main blocker | Outcome |
|---|---|---|---|
| [FruQ-DB, Zenodo 7224690](https://zenodo.org/records/7224690) | 5,647 frames; 11 named fruit/produce varieties; Fresh 2,182, Mild 1,364, Rotten 2,101; `FruQ-DB.zip` 241.1 MB and `FruQ-multi.zip` 4.7 GB. Record links YouTube time-lapse videos. | Zenodo Rights/License fields are blank; video-source use rights/attribution are not resolved. Adjacent-frame leakage is likely to require investigation; no split/video manifest visible. The multi archive exceeds the 2 GB per-archive cap. Pepper is ambiguous. | **EXPLORATORY ONLY**; no download. Preserve Fresh/Mild/Rotten separately. |
| [FoodClass v2, Mendeley 5fjkkv5xgt](https://data.mendeley.com/datasets/5fjkkv5xgt/2) | 85,012 images; 21 subcategories; 2–4 conditions; 224×224; record CC BY 4.0. | Page says images were collected from public repositories but gives no underlying source list. Exact full subcategory/condition list and archive files/sizes are not exposed. The same v2 Mendeley source is already the source for 69,661 rows in the local inventory. | **DO NOT RE-ACQUIRE**; use existing local files for audits after provenance/label review. |
| [Onion bulbs/leaves, Zenodo 20254934](https://zenodo.org/records/20254934) and [Mendeley v2](https://data.mendeley.com/datasets/42bcyncfhy/2) | Zenodo describes 12,260 bulbs plus 4,040 leaves, Healthy/Unhealthy, red/white, single/multiple; ZIP 1.6 GB and metadata workbook 1.3 MB. Mendeley v2 says 16,300 images and CC BY 4.0. | Zenodo Rights/License is blank; exact bulb condition counts not exposed; no documented mapping from unhealthy to spoilage. | **EXPLORATORY ONLY** for bulb imagery; not Fresh/Rotten training data. No download. |
| [Freshness44 Kaggle](https://www.kaggle.com/datasets/siavash93/freshness44) and cleaned Mendeley derivative | Paper reports categories/counts; cleaned record says redundant data were removed and train/test splits added. | Kaggle web page has no readable metadata; Kaggle CLI is not installed and no Kaggle credential file is present. Cleaned derivative file listing/sizes remain inaccessible from the prior review; constituent source rights unresolved. | **PROVENANCE UNVERIFIED**; no download. |
| [AgriFreshNET, Mendeley 42m5tb7yv9](https://data.mendeley.com/datasets/42m5tb7yv9/1) | 14,500 RGB images, 24 classes, Fresh/Semi-Fresh/Rotten; real-world contexts; CC BY 4.0 at record level. | Exact target classes/counts, file sizes and source/rights chain are not available; Semi-Fresh cannot be collapsed into either binary class. | **LABEL SEMANTICS UNCLEAR**; no download. |
| [Tomato_detection, Mendeley vy5y8p2kdb](https://data.mendeley.com/datasets/vy5y8p2kdb/1) | 1,600 exported examples, Fresh/Rotten box labels, 640×640; ZIP listed as 42 MB; CC BY 4.0 at record level. 800 base images reported, with augmented training variants. | Source images are said to come from “various sources” without a rights manifest. Augmentations and split membership need source-ID verification to rule out leakage. It is a box-labeled detection export rather than a verified one-object image classification set. | **PROVENANCE UNVERIFIED**; no download. |
| [Good/Bad carrot, Mendeley ww83r63rtr](https://data.mendeley.com/datasets/ww83r63rtr/1) | Over 500 author-described smartphone images; Good/Bad criteria; record CC BY 4.0. | Bad includes cracks, bruises, mold, discoloration, deformity, wilting and shriveling. “Bad” is broader than Rotten; exact counts and file sizes are not visible. | **LABEL SEMANTICS UNCLEAR**; no download. |
| 2022 ten-produce Fresh/Rotten paper-linked dataset | Paper reports 12,000 images, roughly 600 per class, including Potato, Carrot, Tomato, Cucumber, Bell Pepper. | Paper describes sources including Google/Bing/Kaggle/mobile photos and multiple-produce/background examples. Paper license does not license image files; current Kaggle archive not verified. | **PROVENANCE UNVERIFIED**; no download. |

The FruQ-DB record lists nine distinct YouTube video IDs (the Strawberry entry reuses the Cucumber link), but this is only a count of linked references, not a verified count of source videos used in the archive. The list includes an Avocado link, which is not among the 11 stated varieties, while Grape is named but has no explicit linked video in the record. Per-category video mapping and the actual source-video count remain unknown. Adjacent frames are likely to be visually similar, but no near-duplicate pair is confirmed without the archive.

Additional public search results included derivative/community copies and plant-disease or generic produce collections. They were not treated as suitable sources without identifiable primary publisher, condition semantics, and rights evidence. Plant leaves/disease images and synthetic or unlabelled images are excluded by scope.

## Category readiness

The local FoodClass v2 inventory contains 69,661 rows and is the same cited Mendeley v2 source already present in the project. Read-only grouping of its recorded SHA-256 values found 336 exact-hash Fresh/Rotten conflict groups (673 rows): 316 Orange groups/632 rows, 17 Carrot groups/35 rows, and 3 Tomato groups/6 rows. The Phase 9 vegetable-only report covered the latter 20 groups; the broader total also includes Orange. The existing Phase 9 report identifies 4,686 same-label duplicate groups in the six vegetable subset. These local findings are not external overlap checks; no labels or split files were changed. Onion has zero rows in the local vegetable inventory. See `category_coverage.csv` and `final_readiness_matrix.csv`.

No category is marked `VERIFIED FOR NEXT PREPARATION STAGE`. The exact category decisions are:

- **Potato — PROVENANCE UNVERIFIED.** Local rows exist, but source rights and label verification remain open.
- **Tomato — LABEL SEMANTICS UNCLEAR.** Local conflicts remain unresolved, plus external Tomato_detection is box-labeled and its image provenance is unspecified.
- **Onion — LABEL SEMANTICS UNCLEAR.** Onion bulb imagery exists externally, but only Healthy/Unhealthy labels are documented, not Fresh/Rotten.
- **Carrot — LABEL SEMANTICS UNCLEAR.** Local conflicts remain unresolved; external Good/Bad includes defects beyond spoilage.
- **Cucumber — PROVENANCE UNVERIFIED.** Local rows exist; external Good/Bad and FruQ frame labels do not establish binary Fresh/Rotten semantics and rights.
- **Bell Pepper / Capsicum — PROVENANCE UNVERIFIED.** Local rows exist, but source rights remain open; FruQ “pepper” is not specific enough to assert Bell Pepper.

## Duplicates, overlap, and splits

No new external images were staged, so image-level exact hashes, dHashes, category counts, object multiplicity, image quality, and external/local overlap are **NOT RUN**. No no-overlap result is claimed. FoodClass is confirmed to be the same Mendeley dataset/version already referenced by local inventory records (source-level overlap); exact remote-archive matching is not claimed because no second archive was retrieved.

The existing Phase 9 local audit reports 4,686 same-label exact-duplicate groups (5,692 extra rows removed from its candidate view), 20 conflicting hash groups/41 rows (17 Carrot groups and 3 Tomato groups), and zero duplicate groups crossing recorded local splits. Those are findings from the existing local inventory only; no Phase 12 source was compared against those hashes. Existing conflict ledgers and split assignments were not changed.

## Onion answer

No suitable public Onion Fresh/Rotten dataset was verified. The investigated bulb dataset could be useful for a separately labeled Healthy/Unhealthy visual-quality exploration after rights review, but it must not be relabeled as Fresh/Rotten. Onion still needs an explicitly labeled, rights-cleared source or a separately designed collection and annotation study.

## Remaining actions

1. Obtain written rights/provenance clarification for FoodClass's underlying repositories before using the existing local rows for training.
2. Complete individual manual review of all unresolved exact-hash conflict groups; do not majority-vote or modify source labels.
3. For new sources, require original source/license/attribution details plus an inspectable archive manifest, class folders, and split IDs before download.
4. Keep FruQ’s Mild category separate and source-video groups together if it is later approved for a distinct three-class exploratory experiment.
5. Find an explicitly Fresh/Rotten Onion-bulb dataset or plan a rights-cleared collection.
6. Only after approvals and source gates, download within the 2 GB/archive and 5 GB total limits, checksum archives, and run the included integrity/hash scripts before any future split or training decision.

## Preservation and checks

The Kaggle CLI was not installed and the standard Kaggle credential file was absent (contents were not read). The Kaggle page returned no readable lines through the research browser. Free disk space was approximately 124.1 GB. No archive download, extraction, image hashing, image integrity scan, model operation, application change, or local split/label edit was performed. CSVs and scripts were syntax/structure checked after creation.
