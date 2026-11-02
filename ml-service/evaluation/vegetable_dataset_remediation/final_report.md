# FreshGuard AI — Phase 7 Dataset Remediation & Missing-Data Research

**Review date:** 2026-10-31  
**Decision:** No training or application integration is approved by this audit. Keep all source labels, current manifests, splits, and the six-fruit checkpoint unchanged.

## Findings at a glance

- The prepared inventory contains **37,762 vegetable rows across the six requested category keys**: Potato 2,538; Tomato 17,695; Carrot 12,318; Cucumber 2,118; Bell Pepper 3,093; Onion 0. The five populated categories are all from Mendeley FoodClass v2. All 37,762 rows are marked valid readable JPEGs in the inventory; this is a recorded file validation result, not a new independent re-decode in this phase.
- Category Fresh/Rotten counts and exact hashes are listed below and in `existing_dataset_reassessment.csv`.
- The known contradictory exact-image groups in the full inventory are **336 groups / 673 rows overall**. Among these vegetables, there are **17 Carrot groups (35 rows) and 3 Tomato groups (6 rows)**. Each group has byte-identical images carrying both Fresh and Rotten labels. The conflict ledger includes all 20 groups, every involved path, label, source, and SHA-256.
- A human spot review already recorded by Phase 11B covered one Fresh and one Rotten image per populated category. Potato and Tomato samples appeared plausible; Carrot and Cucumber Rotten samples were ambiguous; the Bell Pepper Rotten sample appeared intact. This is only 10 vegetable samples and does not validate categories.
- Mendeley FoodClass v2 reports CC BY 4.0 at the dataset-record level, but describes an aggregation from public repositories. Per-image original source, rights and attribution are unresolved. The existing audit explicitly cautions that the aggregate record license does not answer every embedded image’s provenance.
- **Onion:** no images in the prepared inventory. External onion-bulb sources exist, but the ones found do not yet provide verified Fresh/Rotten labels with clear image reuse rights.

## Stage A — Existing vegetable data reassessment

| Category | Fresh / Rotten rows | Readable | Unique exact hashes | Repeated hash groups / excess rows | Conflicting label groups | Review result |
|---|---:|---:|---:|---:|---:|---|
| Potato | 1,151 / 1,387 | 2,538 | 2,497 | 39 / 41 | 0 | Promising for manual approval; prior samples plausible; limited evaluation volume |
| Tomato | 13,681 / 4,014 | 17,695 | 13,507 | 3,423 / 4,188 | 3 (6 rows) | Needs conflict adjudication, imbalance and repeated-source review |
| Onion | 0 / 0 | 0 | 0 | 0 / 0 | 0 | No project data |
| Carrot | 9,899 / 2,419 | 12,318 | 11,222 | 973 / 1,096 | 17 (35 rows) | Needs conflict and Rotten-label review; strongly Fresh-skewed |
| Cucumber | 1,104 / 1,014 | 2,118 | 1,785 | 220 / 333 | 0 | Promising counts, but prior Rotten crop ambiguous and repeat count substantial |
| Bell Pepper / Capsicum | 1,601 / 1,492 | 3,093 | 3,038 | 51 / 55 | 0 | Needs Rotten-label review; reviewed Rotten sample appeared intact |

“Repeated hash group” means an exact SHA-256 appears in multiple inventory rows. “Excess rows” counts copies beyond one per hash. These counts do not confirm how many are duplicates across original source items, and do not include perceptual candidates. Conflicting groups are not resolved or excluded from the source inventory.

### Provenance and image type

- Vegetable source rows identify **Mendeley FoodClass v2**, with `source_url` to the Mendeley record and CC BY 4.0 recorded as the dataset record license. The publisher describes 85,012 images collected from publicly available repositories. The prepared folders are produce categories with Fresh/Rotten directories, not leaf-disease labels. No exhaustive visual review was made in Phase 7.
- The original directory labels are explicit, not inferred by this project. However, the source does not provide a written freshness rubric in the inspected local audit materials; explicit folder names are not proof that each image is correctly labelled.
- No bounding boxes were found in the prepared freshness inventory. Do not turn freshness folders into detection boxes or mix detection annotations into this image-level task.

### Near-duplicate concerns already documented

The existing dHash system used a 64-bit grayscale difference hash with Hamming distance ≤4 and capped large buckets. Its report calls these **candidate pairs**, not confirmed duplicates. The Phase 11B sample review records a Tomato Fresh/Rotten candidate pair (P05) for label inspection, a Carrot pair (P09) that looked like near-identical clipart, and Cucumber/Potato and other pairs that appeared to be false positives from shape/background similarity. No new near-duplicate computation was run for Phase 7. Review candidates visually; do not resolve labels from dHash.

## Stage B — Manual review preparation

Created:

- `conflicting_label_review.csv`: 20 group IDs and 41 image rows; includes paths, original normalized labels, category, source and URL, record license, attribution field, source identifier, exact SHA-256 and existing split. All have `Pending` review status.
- `manual_review_manifest.csv`: 81 unique image paths consisting of all 41 conflict rows, prior Phase 11B vegetable spot-review images, and a deterministic small review sample of three hashes per label for each populated vegetable. Each row has the unchanged source label, review reason, source, duplicate group if applicable, and `Pending` status.
- `manual_review_gallery.html`: local gallery with embedded thumbnails for those 81 rows. The source files remain unmodified. Gallery cards show current label, path, hash, source and reason.

Review procedure: compare every member of a `CONFLICT-###` group together; inspect actual appearance and source records; apply a written Fresh/Rotten/Uncertain rubric; capture reviewer, date, rationale and uncertainty in a separate copy. Do not use model predictions or majority vote. For near-duplicate pairs, distinguish identical objects/copies from similar vegetables or backgrounds.

## Stages C and D — External dataset research

External pages were checked read-only on **2026-10-31**. No data or metadata archive was downloaded. `external_dataset_research.csv` lists candidates, category/count evidence, label semantics, source, license, provenance, access and caveats.

### Most useful leads

1. **Five-vegetable balanced dataset described in a 2022 Sensors paper.** The paper reports Potato 615/585, Carrot 620/580, Tomato 604/596, Cucumber 608/593 and Bell Pepper 611/591 (Fresh/Rotten), 12,000 images total across five vegetables and five fruits. It says images were collected from Kaggle, Google, Bing and mobile cameras, and images were manually annotated for YOLOv4. The paper links a Kaggle dataset. This is the strongest broad lead for all five non-Onion vegetables, but not pre-approved: exact current archive version, dataset-specific license, per-image provenance, duplicates/overlap with FoodClass, and whether the box labels support a clean image-level dataset remain to be checked. The article’s CC BY license covers the paper; it does not automatically establish the rights to each included image. [Paper and reported counts](https://www.mdpi.com/1424-8220/22/21/8192), [linked Kaggle source](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset).
2. **AgriFreshNET Mendeley.** Its record reports 14,500 RGB images across 24 fruit/vegetable classes and Fresh, Semi-Fresh and Rotten states under CC BY 4.0. It describes diverse capture environments. The landing metadata checked did not expose the target vegetable class list or per-category counts. It merits metadata-only follow-up; do not collapse Semi-Fresh into either binary class without an approved rubric. [Mendeley record](https://data.mendeley.com/datasets/42m5tb7yv9/1).
3. **Tomato_detection Mendeley.** Record reports 1,600 images, two Fresh/Rotten detection classes, CC BY 4.0, and a 42 MB archive. Its process describes 800 base images plus augmented training variants. This could supplement tomato only after source overlap, original-image grouping, class semantics, rights and annotation structure are checked. [Mendeley record](https://data.mendeley.com/datasets/vy5y8p2kdb/1).
4. **Cucumber Good/Bad Mendeley.** Record states 500 “good” and 500 “bad” cucumber images and CC BY 4.0. “Bad” is not verified as Rotten; use only as a manual-review lead unless a documented rubric establishes the meaning. [Mendeley record](https://data.mendeley.com/datasets/9rs9vmm2bv/1).
5. **VegNet quality dataset.** Bell Pepper and Tomato are included among four vegetables and five folders (Unripe, Ripe, Old, Dried, Damaged), 6,850 total; record reports CC BY 4.0. These categories are not Fresh/Rotten labels. This is a condition-boundary research lead, not direct training data. [Mendeley record](https://data.mendeley.com/datasets/6nxnjbn9w6/1).
6. **VegQual / Fresh and Defective Vegetables.** The associated 2026 paper reports 2,032 images and 4,736 annotated instances for fresh and defective classes over seven vegetables, including Tomato, Potato, Onion and Capsicum. “Defective” is broader than Rotten; license and category-wise image counts were not verified. It is a detection research lead only. [Paper](https://www.nature.com/articles/s41597-026-08167-2), [repository](https://github.com/tarekrahamn/VegQual).

PlantVillage and plant-leaf disease datasets were deliberately excluded as FreshGuard produce-freshness sources. General produce classification sets without condition labels were also not counted as freshness data. No external image or archive has been added to the project.

## Stage C — Onion conclusion

**No credible Onion Fresh/Rotten training source was verified.** A promising image source is Zenodo’s Red and White Onion Bulbs and Leaves record: 16,300 total images, including 12,260 bulbs and 4,040 leaves, with “healthy/unhealthy” attributes. Its public record showed no license value in the Rights section checked, and no Fresh/Rotten count or label equivalence was exposed. Its 1.6 GB archive was not downloaded. [Zenodo record](https://zenodo.org/records/20254934).

A small [ONIONVISION prototype repository](https://github.com/nachiket-mr360/onion-quality-assessment) reports 293 paired images from 92 onion groups: HEALTHY 123, DAMAGED 45, ROTTEN 75, SPROUTED 50. It separates rotten from damage/sprouting, which is useful for rubric design, but reuse rights and original image provenance are unclear and the sample is small. VegQual also includes Onion among fresh/defective detection classes, but that label is not Rotten and its license is unverified. Therefore Onion remains **NEEDS MORE DATA** until a bulb-only, rights-cleared dataset has defensible Fresh/Rotten/Uncertain annotations.

## Stage E — Final readiness matrix

| Vegetable | Existing data | Label quality | Provenance/license | Additional data needed | Final decision |
|---|---|---|---|---|---|
| Potato | 1,151 Fresh / 1,387 Rotten; moderate exact copies | Two prior examples plausible; broader review needed | Per-image rights unresolved | Review candidate set; verify rights and source overlap | **READY FOR MANUAL APPROVAL** |
| Tomato | 13,681 / 4,014 | 3 contradictory exact-hash groups; imbalanced | Per-image rights unresolved | Adjudicate 3 groups; dedupe/source audit; manual review | **NEEDS LABEL REVIEW** |
| Onion | 0 / 0 | No existing labels; external labels do not yet equal Fresh/Rotten | Candidate rights unresolved | Obtain bulb photos with explicit, rubric-consistent labels and clear rights | **NEEDS MORE DATA** |
| Carrot | 9,899 / 2,419 | 17 conflicts; ambiguous Rotten spot sample; imbalanced | Per-image rights unresolved | Adjudicate 17 groups and audit Rotten examples | **NEEDS LABEL REVIEW** |
| Cucumber | 1,104 / 1,014 | No exact conflicts, but Rotten spot sample ambiguous | Per-image rights unresolved | Expanded human review and provenance/duplicate audit | **NEEDS LABEL REVIEW** |
| Capsicum / Bell Pepper | 1,601 / 1,492 | Reviewed Rotten sample appeared intact | Per-image rights unresolved | Broader Rotten-label review and alias/path mapping check | **NEEDS LABEL REVIEW** |

“READY FOR MANUAL APPROVAL” means a reviewer may decide whether to proceed with separate preparation; it does **not** mean ready for training or UI support. No vegetable is approved for training by this report.

## Recommended next actions

1. Human-review the 20 exact conflict groups (41 images), especially every Carrot and Tomato group; preserve originals and record adjudication separately.
2. Complete the 81-image manual review manifest and gallery. Expand sample size using a written rubric, with priority on Carrot/Tomato/Cucumber/Bell Pepper Rotten examples.
3. Obtain image-level rights/provenance clarification for Mendeley FoodClass v2. Exclude unresolved images from any future approved subset rather than relying only on dataset-level CC BY metadata.
4. Before acquiring an external source, verify its actual archive, current version, label mapping, unique original images, image-level terms, overlaps, download size, and holdout/grouping scheme. Do not download large archives in this phase.
5. For Onion, request Zenodo metadata/license clarification and condition semantics; request ONIONVISION image licensing/source information. Keep bulbs separate from leaves and keep damaged/sprouted distinct until the FreshGuard rubric explicitly maps them.
6. Only after review approval, create a new source-aware, physical-item-aware, duplicate-group-aware dataset manifest and untouched test set. The present fruit model checkpoint and all existing splits remain unchanged.

## Files and checks

**Local files inspected:** Phase 6 `ml-service/evaluation/vegetable_dataset_audit/final_report.md` and `vegetable_category_summary.csv`; Phase 11B `preparation_report.md`, `category_coverage.md`, `README.md`, `dataset_inventory.csv`, `license_attribution.md`, `download_manifest.json`, `review_11b_final/final_review_report.md`, `visual_sample_review.csv`, `dhash_pair_sample.csv`; Phase 11C preparation `conflict_investigation_report.md` and `freshness_label_conflicts.csv`; Project-AgML local dataset card and label mapping.

**Checks performed:** Recomputed category rows, Fresh/Rotten rows, SHA-256 unique/repeated counts and conflicting condition groups from the full inventory; checked validation status, JPEG format and dimensions; generated conflict ledger and manual-review manifest; embedded thumbnails for gallery; browsed the cited public dataset records, repository, and paper. No external data was downloaded; no image was relabeled; no model, code, source image, existing report, or split was modified.

**New files:** `final_report.md`, `existing_dataset_reassessment.csv`, `conflicting_label_review.csv`, `manual_review_manifest.csv`, `manual_review_gallery.html`, `external_dataset_research.csv`, `onion_dataset_research.md`, `final_readiness_matrix.csv`, and `README.md` in this folder.

**Limitations:** Existing “readable” counts were taken from prior inventory validation rather than rerunning a full decode. Visual findings use the prior tiny spot-review sample; no additional image-level human decisions were made. External dataset counts, license and label descriptions are claims from source pages and have not been confirmed against downloaded files. Rights concerns are unresolved research questions, not legal conclusions.

## Sources

External pages and source records below were accessed on 2026-10-31:

- [Mendeley FoodClass v2](https://data.mendeley.com/datasets/5fjkkv5xgt/2)
- [Project-AgML freshness fruit card](https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification)
- [Improved Classification Approach, Sensors 2022](https://www.mdpi.com/1424-8220/22/21/8192) and [Kaggle dataset linked by the paper](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset)
- [AgriFreshNET](https://data.mendeley.com/datasets/42m5tb7yv9/1)
- [Tomato_detection](https://data.mendeley.com/datasets/vy5y8p2kdb/1)
- [Good and Bad cucumber dataset](https://data.mendeley.com/datasets/9rs9vmm2bv/1)
- [VegNet quality dataset](https://data.mendeley.com/datasets/6nxnjbn9w6/1)
- [Zenodo onion bulb/leaf dataset](https://zenodo.org/records/20254934)
- [ONIONVISION repository](https://github.com/nachiket-mr360/onion-quality-assessment)
- [VegQual repository](https://github.com/tarekrahamn/VegQual) and [associated Scientific Data paper](https://www.nature.com/articles/s41597-026-08167-2)
