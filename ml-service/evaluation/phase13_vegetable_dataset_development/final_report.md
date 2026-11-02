# FreshGuard AI — Phase 13 Reliable Vegetable Dataset Development

**Review date:** 2026-10-31  
**Recommendation:** proceed with a small, original, rights-documented three-category collection pilot (Potato, Bell Pepper/Capsicum, Cucumber), while completing a separate source/label review of local FoodClass. No category is training-ready. No external data was downloaded, and no model or application code was changed.

## Findings

### VegQual

VegQual is accessible as a Figshare record (version 4; 183.48 MB displayed; CC BY 4.0) and its author repository lists Fresh/Defective paired classes for Tomato, Potato, Onion, Capsicum, and three additional vegetables. The Figshare record reports 2,032 raw images and 4,736 YOLO-box instances, 70/20/10 image splits, and 640×640 preprocessing. The author README's per-class “image” counts sum to 4,736, which matches the record's instance count rather than its raw-image count; the count unit is therefore ambiguous. The file request returned HTTP 403 through the research browser, and shell API access failed DNS resolution, so file names, class-ID mapping, actual labels/boxes, image quality, and overlap could not be inspected. Its `Defective` label is not documented as equivalent to Rotten. **Useful for a separate object-detection/defect study; not suitable as Fresh/Rotten classification data without new evidence.** [Figshare record](https://figshare.com/articles/dataset/A_Multiclass_Dataset_for_Real-Time_Fresh_and_Defective_Vegetables/30596084), [author repository README](https://github.com/tarekrahamn/VegQual/blob/main/README.md).

### AgriFreshNET

The Mendeley page reports 14,500 RGB images, 24 classes, Fresh/Semi-Fresh/Rotten labels, and record-level CC BY 4.0. Its page mentions raw and processed ZIPs, but not their sizes or exact class names/counts. The target vegetable coverage, label rubric, image-level source attribution, and original/augmentation lineage remain unverified. **Promising three-class research lead only; no target category can proceed on the current metadata.** Preserve Semi-Fresh as its own label. [Mendeley record](https://data.mendeley.com/datasets/42m5tb7yv9/1).

### Local FoodClass source recovery

The local inventory contains **69,661 FoodClass v2 rows**. The existing `FoodClass2.zip` was inspected read-only: it has 85,083 ZIP members, including 85,012 image files and one `duplicate_report.txt`. That text only reports 85,012 files scanned, 85,012 unique filenames, and zero duplicate filenames; it does not provide original source URLs, publisher IDs, authorship, or image-level rights. The archive contains no README, license file, source manifest, or metadata sidecars. The inventory gives the Mendeley v2 record URL/DOI and folder-relative identifiers only. Folder paths supply `Fresh`/`Rotten` directory labels, but their original labeling method/rubric is undocumented. A small EXIF check across category/condition samples found no EXIF fields; this is only a sample, not proof about every file.

Read-only grouping by category and SHA-256 found the existing **336 exact-image Fresh/Rotten conflict groups across Orange, Carrot, and Tomato (673 rows)**: 316 Orange groups/632 rows, 17 Carrot/35 rows, and 3 Tomato/6 rows. The Phase 9 vegetable-only report covers 20 groups (Carrot and Tomato); Orange accounts for the rest. These groups are marked `EXCLUDED_CONFLICT` in `local_source_recovery.csv`. All other inventory rows remain `PENDING_SOURCE_VERIFICATION`; none is cleared for training merely because it has no conflict. The group-level review recovers only the Mendeley record, not the upstream image source.

### Best first path by category

- **Potato, Bell Pepper/Capsicum, Cucumber:** strongest first-wave collection candidates. Their existing local folder-label counts are comparatively balanced and no exact-hash conflict groups were found. Source rights and labels remain unresolved, so this is not training approval.
- **Tomato:** substantial local volume, but 3 conflict groups/6 rows and a strong Fresh skew (13,681 Fresh vs 4,014 Rotten in the local inventory). New balanced originals are preferable while the conflicts remain excluded.
- **Carrot:** local volume is substantial but skewed (9,899 Fresh vs 2,419 Rotten), with 17 conflict groups/35 rows. External Good/Bad labels include defects beyond spoilage. Obtain original balanced samples and keep conflicts excluded.
- **Onion:** no local inventory rows. The onion imagery found elsewhere uses Healthy/Unhealthy, and VegQual uses Fresh/Defective; neither supports a Fresh/Rotten mapping. Original Onion bulb collection is needed.

Local counts are inventory rows, not independently validated item counts; repeated views and duplicates are not independent physical specimens. See `category_development_plan.csv` and `final_readiness_matrix.csv`.

## First collection experiment

For a balanced initial feasibility set, target **300 distinct physical items per condition per vegetable** (300 Fresh + 300 Rotten for each category), with two views per item. That is 600 item IDs/1,200 photos per category, 3,600 items/7,200 photos across six vegetables. A smaller three-category first wave (Potato, Bell Pepper, Cucumber) is 1,800 items/3,600 photos. A stronger later target is 500 items per condition/category. These are planning targets, not established performance guarantees.

Use item-level Fresh/Rotten/Uncertain labels, preserve the original captures and rights records, and keep all views/crops of each item in one future split. The collection protocol and visual rubric are in `image_collection_protocol.md` and `freshness_labeling_guide.md`. Uncertain images stay outside binary candidates. Visual classifications are not food-safety assessments.

## Final status and preservation

- VegQual: **conditionally useful for detection/defect research**, not Fresh/Rotten classification.
- AgriFreshNET: **conditional three-class lead**, target category and archive details unverified.
- FoodClass: upstream original source URLs/publisher IDs **not recovered** from the local archive, inventory, README/license notes, or sample EXIF; all rows need source verification, with known conflicts excluded.
- Freshness44 and other previous phase reports were not overwritten. No image was modified, relabeled, moved, or deleted; no split was changed. No model was trained; the six-fruit checkpoint and application remain untouched.
- No external data was acquired. All publisher-reported counts are labeled as reported and kept distinct from local inventory counts.
