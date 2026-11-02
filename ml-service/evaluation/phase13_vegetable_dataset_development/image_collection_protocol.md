# Original vegetable image collection protocol

## Objective and first-wave target

Build a consistent, rights-cleared image collection for one harvested vegetable item per image. First wave priority: **Potato, Bell Pepper/Capsicum, and Cucumber** because the existing local inventory has relatively balanced folder labels and no exact-hash conflicts for those categories. This is a collection priority only; existing local files remain blocked by unresolved provenance. Extend the same protocol to Tomato, Carrot, and Onion after the capture and label process is stable. Onion needs new data because the existing local inventory has none and available external Onion labels are not Fresh/Rotten.

Minimum feasibility target for all six categories:

- 300 distinct physical items labeled Fresh and 300 distinct physical items labeled Rotten per category (600 item IDs/category; 3,600 item IDs total).
- Capture two distinct views per item (for example, opposite sides): **1,200 photos/category; 7,200 photographs total**.
- If starting with the three-category pilot, target 1,800 item IDs and 3,600 photos.
- Treat this as a minimum feasibility experiment, not evidence that the resulting model will generalize. A stronger follow-on target is 500 physical items per condition/category, with the same two-view capture (12,000 photos across six categories).

The split unit is the physical item, not the photograph. With the minimum all-six target, a per-category stratified 70/15/15 item split gives 210 Fresh + 210 Rotten train items, 45 + 45 validation items, and 45 + 45 test items. All views, crops, and repeat captures of an item stay in one split. Where possible, hold out capture sessions/market days in test to measure setting transfer; record that such a holdout requires multiple collection sessions/sites. Do not move or reuse any existing test data.

## Capture method

1. Photograph actual harvested produce, including naturally occurring variation and defects. Do not use leaves, plant-disease imagery, stock/web images, composites, or synthetic images as real produce photos.
2. Use a single target item in each frame. Capture two non-identical views with enough surface area visible; avoid covering or editing defects. Do not artificially damage produce to create a Rotten sample.
3. Use multiple smartphones/cameras, lighting conditions, and backgrounds. Include ordinary household and market settings; do not rely only on pristine supermarket displays or a single black/white backdrop. Keep views clear enough to identify the item.
4. Capture and retain the original camera file. Do not crop, color-correct, denoise, or recompress originals in the collection store. Store derived resize/crops separately and reproducibly later.
5. Record an item once at capture and link all views to it. Record: image ID, item ID, category, condition decision, date/time, collector/photographer, camera/device, capture session/site code, view number, lighting/background notes, storage/time-since-purchase if known, consent/rights record, and label evidence note. Do not record personal data about shoppers or bystanders.
6. Record the photographer and rights holder, permission/consent basis, allowed uses (including research/commercial if explicitly granted), attribution, and any venue restrictions. Keep release records separate from public image manifests.
7. Store raw images read-only and keep a checksum. Use separate manifests for later review and processing. Do not overwrite originals.

## Label workflow and quality checks

Assign one Fresh / Rotten / Uncertain item-level label using the guide in `freshness_labeling_guide.md`; copy that decision to its views without treating views as independent specimens. Keep uncertain cases outside binary candidates. Record annotator, date, rubric version, and concise evidence. A second reviewer may resolve disagreements without deleting or rewriting the initial decision; retain both decisions and final adjudication as separate fields. No exhaustive manual audit of the existing legacy dataset is required by this protocol.

Automate file readability, dimensions, hashes, missing-view checks, duplicate grouping, manifest completeness, and item/split leakage checks. Manually spot-check a small stratified quality-control sample and all disputed/uncertain item labels. These checks do not validate food safety.
