# FreshGuard AI — Phase 6 Vegetable Freshness Dataset Audit

**Audit date:** 2026-10-31  
**Scope:** Read-only review of the prepared expansion inventory and prior dataset audits. No images, manifests, splits, checkpoints, or application code were changed. No dataset was downloaded and no training was run.

## Executive recommendation

**Do not add any vegetable to the live application or train the shared classifier yet.** The prepared inventory offers useful image-level examples for five vegetables, but every vegetable row comes from one aggregated source whose per-image provenance remains unresolved. Folder names provide explicit Fresh/Rotten labels, but the previous spot audit found questionable/ambiguous examples, and exact-byte label contradictions remain for Tomato and Carrot.

For the next *data preparation and review* step, prioritize **Potato and Cucumber**: both have roughly balanced raw class counts and no exact-hash condition conflicts. This is a conditional review priority, not approval for training. Cucumber's sampled Rotten image was ambiguous, so expand its manual audit before inclusion. **Tomato and Carrot** need conflict adjudication and label-balance/source review first. **Capsicum/Bell Pepper** needs a broader Rotten-label review because its one reviewed Rotten sample appeared intact. **Onion** has no examples and is insufficient.

## Vegetable availability and quality

Counts below are inventory rows, not independently verified unique physical specimens. The additional exact-copy columns count SHA-256-identical content within each category; they are not perceptual-duplicate estimates. “Repeated hash groups” counts hashes appearing more than once; “excess rows” is the number of rows beyond one per hash. The category CSV provides the detailed values. Its label-specific hash columns include hashes involved in a contradictory group; the unambiguous columns exclude those conflict groups.

| Vegetable | Fresh / Rotten rows | Exact-image summary | Conflict groups | Readiness |
|---|---:|---|---:|---|
| Potato | 1,151 / 1,387 | 2,497 unique hashes; 39 repeated groups / 41 excess rows | 0 | **Ready for further preparation**, conditional on rights and expanded label review |
| Tomato | 13,681 / 4,014 | 13,507 unique hashes; 3,423 repeated groups / 4,188 excess rows | 3 (6 rows) | **Needs manual review** |
| Onion | 0 / 0 | No images | 0 | **Insufficient data** |
| Carrot | 9,899 / 2,419 | 11,222 unique hashes; 973 repeated groups / 1,096 excess rows | 17 (35 rows) | **Needs manual review** |
| Cucumber | 1,104 / 1,014 | 1,785 unique hashes; 220 repeated groups / 333 excess rows | 0 | **Ready for further preparation**, conditional on expanded Rotten-label review |
| Capsicum (Bell Pepper) | 1,601 / 1,492 | 3,038 unique hashes; 51 repeated groups / 55 excess rows | 0 | **Needs manual review** |

All six categories have **0 rows from Project-AgML** in the prepared inventory. All populated vegetable records are Mendeley rows labelled through their original `Fresh` or `Rotten` folder condition and normalized in the inventory; there are no inferred condition labels in this prepared set. Mendeley folders say nothing about a documented, consistent freshness rubric, so explicit directory labels should not be equated with verified ground truth.

Every populated row in these six categories is marked `valid`, has JPEG format and nonzero width/height in the inventory. The preparation report says the included Mendeley images were decoded with Pillow and that all 71,661 inventory paths existed at audit time. These checks establish basic file readability, not photographic suitability, consistent framing, single-item content, or label correctness.

## Duplicate and conflict analysis

- Exact duplicate counts were recomputed from `dataset_inventory.csv` using SHA-256, restricted to each normalized vegetable category. These duplicates may be repeated copies or source variants; counts alone do not establish the image's provenance.
- The Mendeley portion contains **336 exact-hash groups / 673 rows** with conflicting Fresh/Rotten labels overall: 316 Orange, **17 Carrot (35 rows)**, and **3 Tomato (6 rows)**. They are all from Mendeley; no cross-source conflict group was reported. The two vegetable categories with conflicts therefore contain identical bytes labelled both ways. The audit cannot determine the correct label automatically.
- No exact-hash Fresh/Rotten conflicts were found for Potato, Cucumber, or Bell Pepper. This does not rule out incorrect labels or visually similar duplicates.
- Existing dHash analysis is only candidate-pair triage. The prior review explicitly did not call perceptual-similarity candidates confirmed duplicates. No new dHash report was generated for this phase.

## Existing human image review

The prior Phase 11B visual review inspected one Fresh and one Rotten image per populated category (22 images total across the 11 populated categories); it did not inspect Onion, which has no images. Vegetable observations were:

- **Potato:** reviewed Fresh sample looked intact; Rotten sample showed a split/visible decay. Both looked plausible in this small spot check.
- **Tomato:** reviewed Fresh sample appeared to show a red tomato without severe spoilage; Rotten sample appeared moldy/decomposed. Both looked plausible, but three contradictory exact-hash groups remain.
- **Carrot:** Fresh sample appeared intact; Rotten sample had white patches/discoloration and was ambiguous between spoilage and surface damage/aging. 17 contradictory exact-hash groups remain.
- **Cucumber:** Fresh sample looked intact; Rotten sample was tightly cropped and ambiguous without broader context.
- **Bell Pepper:** reviewed Rotten sample appeared intact/shiny, raising a label question. One sample cannot estimate category-wide error.
- **Onion:** no sample was available.

These are inherited sample-review notes, not a new image-by-image review in this phase. One example per condition is not enough to validate labels or image quality for a category.

## Source, license, and provenance

The vegetable examples come from **FoodClass: Fruit, Vegetable, Meat, Fish dataset v2**, Mendeley Data DOI `10.17632/5fjkkv5xgt.2`. The local preparation report states that the publisher-listed archive checksum matched and the targeted vegetable folders were extracted. The Mendeley record describes 85,012 images collected from publicly available repositories and reports **CC BY 4.0**. The record-level license is useful attribution metadata but does not establish the original creator, source URL, license, or attribution obligation for each constituent image. Treat per-image rights/provenance as unresolved; this is not a legal conclusion.

Project-AgML's local dataset card identifies its fruit classification export as CC BY 4.0, but it contains fruit examples, not these vegetables. It therefore contributes **zero** vegetable images to these counts. Do not use Open Images bounding-box data as freshness data: bounding-box category annotations do not supply Fresh/Rotten condition labels.

Before retaining a training subset, preserve the source record, archive checksum, original path/condition, image hash, and available attribution. Seek image-level provenance/rights review for the Mendeley aggregation and maintain any exclusions in a new, separate manifest.

## Per-category disposition

- **Potato — Ready for further preparation.** Counts are moderate and near balanced; no exact label conflicts; the previous two samples looked plausible. Proceed only to a broader label audit and provenance clearance. Its small untouched test count (182 rows in existing coverage) limits evaluation precision. Do not change current splits.
- **Tomato — Needs manual review.** It has the most data, but a 3.41:1 raw Fresh-to-Rotten ratio and three exact-byte condition conflicts (six rows), plus 4,188 excess exact-copy inventory rows. First reconcile all conflicting groups, audit the repeated content/source patterns, define labels consistently, and plan balance-aware evaluation. Existing test split is 1,672 rows; keep it untouched.
- **Onion — Insufficient data.** No Fresh or Rotten images were found. Source a separately licensed dataset with explicit condition labels, or defer support. Do not substitute detection-only onion images.
- **Carrot — Needs manual review.** Raw Fresh-to-Rotten ratio is 4.09:1; 17 exact-byte conflict groups (35 rows), 1,096 excess exact-copy rows, and an ambiguous Rotten sample. Reconcile conflicts and review Rotten examples before considering preparation.
- **Cucumber — Ready for further preparation.** Raw counts are near balanced and no exact-hash label conflicts were found, but 333 excess exact-copy rows and an ambiguous reviewed Rotten example warrant broader stratified inspection. Existing test split is only 117 rows. Treat as a candidate for a later, carefully reviewed pilot, not as currently training-ready.
- **Capsicum/Bell Pepper — Needs manual review.** Counts are near balanced and no exact-hash conflicts were found, but the reviewed Rotten sample looked intact. Audit the original `Capsicum`/`Bellpepper` folder mapping and inspect a larger Rotten sample before inclusion.

## Can these vegetables share one MobileNetV2 Fresh/Rotten model with fruit?

**Technically yes, after data remediation and a new experiment; not with the current artifacts as-is.** A shared binary classifier can use the common Fresh/Rotten target across produce categories, while category selection is supplied by the application or handled by a separate category-aware evaluation layer. However:

1. The existing checkpoint was trained on fruit data and must remain untouched. A combined experiment requires a separately named checkpoint and new, documented training run after approval.
2. Mendeley rights/provenance and label quality must be addressed before a combined training subset is approved.
3. Use the same written operational Fresh/Rotten rubric across fruits and vegetables; distinguish normal ripeness, cosmetic damage, bruising, mold, and actual spoilage.
4. Rebuild a new source-aware, exact-duplicate-group-aware split. Preserve current manifests and keep the current test partition untouched; create a separate untouched test set for the new combined experiment.
5. Report Fresh/Rotten precision, recall, calibration/uncertainty behavior, and per-category results. Aggregate accuracy can hide a weak vegetable category or source shortcut.
6. Consider category-conditioned thresholds or a category-specific abstention policy only after validation; do not present the output as a food-safety judgment.

## Minimum next actions

1. Resolve provenance and image-level attribution for any Mendeley examples proposed for use; record unresolved/excluded IDs explicitly.
2. Write a shared labeling rubric and have reviewers adjudicate all 20 Carrot/Tomato conflict groups (17 + 3) without majority-vote automation.
3. Conduct a stratified human review by category, condition, and source path, prioritizing Carrot Rotten, Tomato Rotten, Cucumber Rotten, and Bell Pepper Rotten. Record reviewer decisions and uncertainty separately; do not overwrite the source labels.
4. Inspect exact-copy groups, especially the large Tomato and Carrot repeat counts, and verify whether their copies are same-source derivatives. Do not count repeated rows as independent examples.
5. Defer Onion until a suitable, rights-reviewed, explicitly labelled dataset is identified.
6. Only after review approval, create a new clean manifest and source-aware split for an experiment; leave current data, splits, and checkpoint unchanged.

## Files and checks

**Files inspected:** `Project Progress Review.md`; Phase 11B `preparation_report.md`, `category_coverage.md`, `README.md`, `dataset_inventory.csv`, `license_attribution.md`, `download_manifest.json`, `review_11b_final/final_review_report.md`, `review_11b_final/visual_sample_review.csv`, and Phase 11C prep `freshness_label_conflicts.csv` and `conflict_investigation_report.md`; local Project-AgML dataset card and label mapping.

**Checks performed:** Recomputed six vegetable Fresh/Rotten row counts, SHA-256 unique hashes, repeated-hash groups, excess duplicate rows, and exact-hash conflicting-condition groups from the inventory. Checked validation status, image format, and nonzero dimensions for populated categories. Reviewed prior visual spot-check observations and prior conflict/provenance findings. No new image sampling, downloads, tests, or training were performed.

**New files:** `final_report.md` and `vegetable_category_summary.csv` in this review folder. Existing files and model/application artifacts were not changed.

**Limitations:** No independent relabeling; only one previously reviewed image per condition/category; Mendeley per-image rights/source provenance unresolved; exact copies do not capture perceptual duplicates; no new image viewing or model evaluation was performed in this phase.

## Source references

- [Mendeley FoodClass v2 dataset record](https://data.mendeley.com/datasets/5fjkkv5xgt/2) — record describes the merged public-repository dataset and CC BY 4.0.
- [Project-AgML Fresh Rotten Fruit Classification dataset card](https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification) — CC BY 4.0 fruit dataset; not a vegetable source for this inventory.
- Local provenance notes: `ml-service/datasets/expansion_15/license_attribution.md`.
- Local counts, validation, splits, and conflicts: `ml-service/datasets/expansion_15/category_coverage.md`, `preparation_report.md`, and `review_11b_final/final_review_report.md`.

