# FreshGuard AI — Public Dataset Audit and Expansion Plan

**Audit date:** 2026-10-28  
**Scope:** Read-only review of current ML assets and public dataset metadata. No dataset was downloaded, no existing file was changed, and no model was trained.

## Executive summary

FreshGuard currently has two different kinds of coverage that should not be conflated:

- **Detector:** pretrained YOLO11n COCO weights (`models/yolo11n.pt`). The application allowlist returns Apple, Banana, Orange, Carrot, and Broccoli. It is not a detector trained for all 15 requested produce categories.
- **Freshness classifier:** `models/freshness_classifier/best_model.pth`, a MobileNetV2 binary classifier whose output classes are `fresh` and `rotten`. Its training images span eight fruit categories, but its architecture does not predict fruit identity. The current inference pipeline only applies it to Apple, Banana, and Orange crops.

The existing Hugging Face dataset is already present locally and supports freshness labels for Apple, Banana, Grapes (stored as `grape`), Orange, and Strawberry among the target list. It has no boxes. A promising additional candidate, the paper-linked Fruits and Vegetables dataset, reports 12,000 images across ten target types with fresh/rotten labels and YOLOv4/LabelImg annotations. The archive and its current Kaggle license were not inspectable in this audit, so that is a **candidate requiring a rights and archive check**, not an approved training source.

The requested Mendeley and Zenodo datasets are discoverable and their landing-page metadata is accessible, but their archives were not downloaded or unpacked. In particular, the class list for the Zenodo 30-class aggregate and the 21 Mendeley subcategories are not enumerated in the visible metadata. Their category-level contribution therefore remains unverified. **No evidence supports all 15 categories for both tasks today.**

## Current project assets inspected

| Asset | Finding |
| --- | --- |
| `app/prediction_service.py` | Supported detector allowlist is Apple, Banana, Orange, Carrot, Broccoli. The inference policy applies freshness classification only to Apple, Banana, and Orange. |
| `app/model_service.py` | YOLO11n is loaded from `models/yolo11n.pt`. MobileNetV2 is loaded from `models/freshness_classifier/best_model.pth` and checked against its metadata. |
| `models/freshness_classifier/metadata.json` | `torchvision.mobilenet_v2`; classes `fresh` index 0 and `rotten` index 1; 224×224 resize; ImageNet mean/std. It defines no produce identity labels. |
| `scripts/inspect_dataset.py`, `scripts/prepare_dataset.py` | Existing workflow inspects the raw Hugging Face `raw` configuration, validates image bytes and labels, records SHA-256, and writes a manifest. It splits by exact-byte hash group with seed 42 and 70/15/15 stratification. It does not perform perceptual near-duplicate grouping. |
| `scripts/train_freshness_classifier.py` | Trains only the two `fresh`/`rotten` classes from `ImageFolder`; the fruit category is not a model output. It requires the existing 2,240/480/480 split sizes. |
| `scripts/predict_freshness_image.py` | Uses the saved checkpoint class mapping, resize, and normalization; scores are model class scores, not freshness percentages. |
| `datasets/dataset_report.json`, `datasets/prepared/manifest.csv` | The locally inspected raw dataset has 3,200 readable JPEGs, 8 fruit types × 400 each, and 200 Fresh plus 200 Rotten per type. The report records 7 exact-duplicate groups (7 extra rows), with duplicate groups kept within a split and no exact-hash split crossings. Near-duplicates were not checked. |
| `models/freshness_classifier/test_evaluation.json` | Existing held-out test: 480 images, 99.375% accuracy. This is an in-domain result from the prepared dataset split, not evidence of real-world or 15-category generalization. |

Locally, `datasets/prepared` contains 3,200 images plus a manifest and occupies about 2.86 GB. The `datasets/raw` tree occupies about 7.18 GB including caches and model-related files; this is current workspace usage, not an estimate of a new dataset download.

## Candidate source audit

### 1. Existing Hugging Face Fresh Rotten Fruit Classification

Source: [Project-AgML/fresh_rotten_fruit_classification](https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification)

- **Accessible and inspected:** yes. The local pinned raw revision and dataset report were inspected; the Hugging Face page also exposes its raw configuration and schema.
- **Format and size:** Parquet; local audit metadata reports 2,856,370,960 bytes of raw Parquet. The prepared JPEG export is already present locally.
- **Labels/classes:** `fresh` and `rotten`; `fruit_type` is apple, banana, grape, guava, jujube, orange, pomegranate, or strawberry. Exactly 400 original rows per category (200 per condition). The raw source has 3,200 rows; the separate augmented version has 12,335 rows and must not be counted as independent originals.
- **Boxes:** none in the inspected schema (`image`, `label`, `fruit_type`). This is image-level classification data.
- **License:** CC BY 4.0 on the dataset card. Preserve attribution and source citation.
- **Recommendation:** keep using it for freshness classification; it complements, but does not replace, the detector. Do not add the augmented images as separate independent samples.

### 2. Mendeley FoodClass, version 2

Source: [FoodClass: Fruit, Vegetable, Meat, Fish dataset](https://data.mendeley.com/datasets/5fjkkv5xgt/2)

- **Accessible and inspected:** landing-page metadata yes; archive contents no. No archive was downloaded.
- **Format and size:** one `FoodClass2.zip`, reported as 1.24 GB; images are resized to 224×224.
- **Labels/classes:** 85,012 images total, four major category groupings and 21 subcategories, organized as category → subcategory → condition. The page says conditions vary from 2 to 4. It does not list the 21 subcategory names or per-category counts in the visible metadata. **Do not count any of the 15 requested categories as confirmed from this source until the archive and labels are inspected.**
- **Boxes:** no bounding-box format is stated on the landing page; treat as classification-only/unknown until archive inspection.
- **License:** CC BY 4.0 on the Mendeley record. Attribute the dataset and review source provenance as it is described as a merge of images from public repositories.
- **Recommendation:** potential supplementary freshness data only after extracting the class/condition inventory, source-level rights, image counts, and duplicates. Preserve 2–4 condition values separately; do not automatically collapse them into Fresh/Rotten.

### 3. Zenodo multi-class fruit and vegetable detection dataset

Source: [Multi-Class Fruit and Vegetable Detection Dataset for Computer Vision](https://zenodo.org/records/18904638)

- **Accessible and inspected:** record metadata yes; the 1.0 GB `AgricultureDataset.zip` archive no. No archive was downloaded.
- **Format and size:** YOLO-format annotations with train/validation/test splits; 20,216 images and 222,301 annotations across 30 stated fruit/vegetable categories; archive size reported as 1.0 GB.
- **Labels/classes:** the record describes an aggregation of many Roboflow datasets, and names some source projects (including tomato, mango, grape, orange, and apple projects). It does not provide a verified flat 30-class label map or per-class counts in the accessible record text. These source-project names are not sufficient proof that every target label exists in the final archive.
- **Freshness labels:** none stated; detection only.
- **License:** the Zenodo landing page's rights/license field was not populated in the inspected page. A separate institutional listing appears to report CC BY 4.0 but contains a DOI mismatch. Treat the license as **unverified for this exact record** until Zenodo's record metadata and any upstream Roboflow terms are checked.
- **Recommendation:** promising detection candidate after class-map, image/annotation integrity, upstream rights, and split/duplicate audit. Do not merge its pre-made splits blindly with other sources.

### 4. Additional candidate: Fruits and Vegetables freshness dataset (Mukhiddinov et al.)

Source: [Kaggle dataset](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset); [paper and dataset description](https://www.mdpi.com/1424-8220/22/21/8192); [full article text and data availability](https://pmc.ncbi.nlm.nih.gov/articles/PMC9653939/).

- **Accessible and inspected:** the paper and its data-availability link were inspected. Kaggle's public page resolves, but the web inspection did not expose its files, current license, or archive size; the archive itself was not downloaded or inspected.
- **Format and size:** paper reports 12,000 images in 20 condition/type classes, approximately 600 per class, with images resized to 608×608 for the described dataset. Archive download size is unverified.
- **Target classes and condition counts from the paper's table:** Apple Fresh 612 / Rotten 588; Banana 624 / 576; Orange 609 / 591; Strawberry 603 / 596; Mango 605 / 593; Potato 615 / 585; Carrot 620 / 580; Tomato 604 / 596; Cucumber 608 / 593; Bell pepper 611 / 591. These sum to 12,000 paper-reported image records. They are not verified unique originals: the paper says some imagery came from online sources, so exact and near-duplicate checks are required before counting independent samples. For several types the totals differ by one or two because the published table is not exactly balanced.
- **Boxes:** the paper says images were manually rectangle-annotated with LabelImg for YOLOv4. This is promising detection supervision, but the actual archive, annotation files, class encoding, and association of boxes to condition labels were not directly checked. The paper describes single and multiple objects; inspect those cases before deriving crop labels.
- **License:** **unverified for the Kaggle dataset files.** The paper is open access, but its article license does not automatically grant rights to the separately hosted images, some of which were gathered from web repositories. Verify the Kaggle dataset license and third-party material rights before model use or redistribution.
- **Recommendation:** highest-priority candidate for the ten overlapping target categories, subject to a small, non-training archive inspection and license review. It could potentially support both tasks if the YOLO labels are complete and map cleanly. Do not assume this until the annotations are inspected.

### 5. Additional detection lead: PackEat

Source: [PackEat data descriptor](https://www.nature.com/articles/s41597-025-06298-6); [Zenodo record](https://zenodo.org/records/16901177).

The paper reports over 100,000 retail images, 370,000 objects, 34 species, 65 varieties, and about 9,000 manually segmented images. Segmentation annotations are provided in text files; JPEG images, taxonomy, and classification metadata are described. It is a useful candidate for retail-domain detection/segmentation and provides challenging packaging and background conditions. It does **not** establish Fresh/Rotten labels; recorded spoilage-related metadata is not equivalent to a two-class freshness ground truth. Exact per-target classes/counts and the Zenodo archive size/license were not verified in this audit. The paper uses CC BY-NC-ND 4.0 for the article; do not treat that as the dataset license. Confirm the exact Zenodo file license before using or adapting its data.

## Fifteen-category coverage matrix

**Reading the matrix:** “Confirmed data” means a source or local project asset explicitly reports that category and label. “Candidate/partial” is not model support. The Kaggle 12k source reports box annotation for its ten categories, but files were not inspected; counts below are image-level counts from its paper, not counts of boxes. The current deployed freshness pipeline remains limited to Apple, Banana, and Orange.

| Target | Detection data available | Freshness data available | Verified image counts and labels | Sources / license | Remaining gap |
| --- | --- | --- | --- | --- | --- |
| Apple | Yes — current COCO allowlist; candidate YOLO boxes in 12k dataset | Yes | FreshVeg 612 Fresh / 588 Rotten; HF 400 (200/200); counts are source images | COCO pretrained labels; FreshVeg Kaggle license unverified; HF CC BY 4.0 | Inspect source boxes and deduplicate shared images; detector needs target-domain evaluation. Runtime freshness enabled. |
| Banana | Yes — current COCO allowlist; candidate YOLO boxes in 12k dataset | Yes | FreshVeg 624 / 576; HF 400 (200/200) | Same as Apple | Verify source provenance and boxes. Runtime freshness enabled. |
| Orange | Yes — current COCO allowlist; candidate YOLO boxes in 12k dataset | Yes | FreshVeg 609 / 591; HF 400 (200/200) | Same as Apple | Verify cross-source duplicates and domain shift. Runtime freshness enabled. |
| Mango | Partial — FreshVeg paper reports boxes; Zenodo aggregate class not verified; current COCO has no Mango class | Yes | FreshVeg 605 / 593 | FreshVeg Kaggle license unverified | Needs verified detector dataset/class-map and independent object-level freshness validation. Runtime does not support Mango. |
| Grapes | Partial — Zenodo aggregate/source list mentions a Grape project, but final class map/count unverified; no current COCO allowlist | Yes | HF `grape`: 400 (200/200) | HF CC BY 4.0; Zenodo license unresolved | Add verified detector boxes and map singular `grape` to canonical `Grapes`. Runtime does not support Grapes. |
| Strawberry | Partial — Zenodo aggregate labels unverified; no current COCO allowlist | Yes | FreshVeg 603 / 596; HF 400 (200/200) | FreshVeg Kaggle license unverified; HF CC BY 4.0 | Verify source boxes, provenance, and detector data. Runtime does not support Strawberry. |
| Tomato | Partial — Zenodo explicitly names Tomato detection sources; FreshVeg paper reports boxes; current COCO has no Tomato class | Yes | FreshVeg 604 / 596 | FreshVeg Kaggle license unverified; Zenodo license unresolved | Must test unknown-class false positives and avoid treating an Apple prediction as Tomato/vice versa. Runtime does not support Tomato. |
| Potato | Partial — Zenodo aggregate class map unverified; FreshVeg paper reports boxes; current COCO does not support Potato | Yes | FreshVeg 615 / 585 | FreshVeg Kaggle license unverified | Verify class labels and boxes. Runtime does not support Potato. |
| Carrot | Yes — current COCO allowlist; candidate FreshVeg boxes | Yes | FreshVeg 620 / 580 | FreshVeg Kaggle license unverified | No current freshness model support; verify dataset boxes and quality labels. |
| Cucumber | Partial — Zenodo aggregate class map unverified; FreshVeg paper reports boxes; current COCO does not support Cucumber | Yes | FreshVeg 608 / 593 | FreshVeg Kaggle license unverified | Verify class labels and boxes. Runtime does not support Cucumber. |
| Onion | Partial — possible Zenodo/PackEat/Mendeley coverage, but target class presence unverified; no current COCO support | No verified Fresh/Rotten source | No verified per-class count | Candidate source licenses/classes unresolved | Need both class-specific boxes and condition-labeled examples. |
| Bell pepper | Partial — FreshVeg paper reports boxes; Zenodo/PackEat class counts unverified; current COCO has no Bell pepper class | Yes | FreshVeg 611 / 591 | FreshVeg Kaggle license unverified | Verify annotation class mapping and licensing. Runtime does not support Bell pepper. |
| Broccoli | Yes — current COCO allowlist | No verified Fresh/Rotten source | No verified condition-labeled count | Current detector is pretrained COCO; no verified freshness source | Need condition labels and crops. Runtime detection only. |
| Lemon | Partial — possible Zenodo/PackEat/Mendeley coverage, but target class presence unverified; no current COCO support | No verified Fresh/Rotten source | No verified per-class count | Candidate source licenses/classes unresolved | Need both class-specific boxes and condition-labeled examples. |
| Pear | Partial — Zenodo lists a pear-named source project, but final class/count unverified; current COCO has no Pear class | No verified Fresh/Rotten source | No verified per-class freshness count | Zenodo license unresolved | Need verified boxes and freshness labels. |

**Coverage conclusion:** The FreshVeg paper-reported dataset covers ten target types with Fresh/Rotten labels and states that the images have YOLOv4 rectangle annotations. The existing Hugging Face dataset adds Grapes, giving published or locally inspected freshness counts for 11 target categories. Onion, Broccoli, Lemon, and Pear have no verified Fresh/Rotten examples in the sources inspected. The Kaggle FreshVeg archive and its annotations still require direct inspection, and detection remains incomplete in the current deployed model even where candidate data exists.

## Recommended source selection

1. **Retain the existing Hugging Face dataset** as the known, version-pinned freshness source. It covers five requested categories with 400 images each and reproducible source metadata. It has no object boxes, so use it only for image/crop-level freshness data.
2. **Prioritize a limited metadata/archive inspection of the 12k FreshVeg Kaggle dataset.** It may cover ten target categories for both object boxes and freshness. Before approving it, confirm (a) the current license and original-image rights, (b) archive size and layout, (c) YOLO class names/indices, (d) whether every object has a box and condition label, and (e) whether multi-object images can be mapped unambiguously to per-object freshness labels.
3. **Do not ingest the Mendeley 1.24 GB archive yet.** First request/inspect its category-condition inventory and licensing/provenance. Its broad title and 85,012 total do not prove any target-category coverage.
4. **Use Zenodo 18904638 only after a class-map and license gate.** The 1 GB archive has many YOLO annotations, but the visible record does not provide a final class list/count table or a clearly verified record license.
5. **Evaluate PackEat as a retail-domain detection/segmentation benchmark**, especially for image diversity and packaged objects. It does not fill freshness-label gaps by itself. Verify exact species and Zenodo license before use.
6. **Do not merge Fresh, Rotten, semi-fresh, stale, damaged, diseased, or maturity/ripe labels by name.** Build a source-specific label map and retain raw labels until a domain definition and reviewed mapping are approved.

## Preparation plan for the next data phase

1. Freeze the present models, dataset report, prepared files, and checkpoints; create a separate versioned expansion workspace rather than passing `--force` to the current preparation script.
2. Record each source URL, version/revision, access date, file checksums, license text, attribution, third-party source notes, and permission status in a source manifest before extracting images.
3. Create separate canonical vocabularies:
   - detection `produce` label (15 names; normalize variants such as `grape` → `Grapes`, `capsicum`/`pepper` → `Bell pepper` only after semantic review);
   - freshness condition preserving the source label (`fresh`, `rotten`, `stale`, `semi-fresh`, `damaged`, etc.); and
   - annotation geometry plus image-level/object-level scope.
4. Keep detection records (image, boxes/masks, canonical produce, source annotation IDs) separate from freshness records (image or crop, produce, raw condition, mapped condition, label rationale). Do not convert a source with no boxes into detector training labels.
5. Validate image decode, dimensions, color mode, empty annotations, out-of-range boxes, class IDs, and missing labels. Report corrupt files and label conflicts; do not silently skip or relabel them.
6. Deduplicate using SHA-256 exact hashes and a perceptual-hash/embedding review for near duplicates. Use source IDs and image capture/layout/session IDs to group related viewpoints and crops. Keep each group in exactly one split; avoid using pre-split rows from different sources as if independent.
7. Establish stable train/validation/test splits with a published seed and stratification by canonical class × condition × source/domain. Prefer group-level splits (same object/session/shop/source group cannot cross splits). Reserve an untouched, source-held-out test set for generalization.
8. Preserve original images and annotation files as immutable source data; record transformations/augmentations separately. Augmented copies stay linked to their original and never count as new independent examples.
9. Generate separate detection and classifier crop manifests, plus coverage/duplicate reports. Do a manual review sample per category and condition before any training.

## Storage estimate

| Source | Reported downloadable archive/size | Qualification |
| --- | ---: | --- |
| Hugging Face raw Parquet | 2.86 GB | Exact raw Parquet size in the local audit report; already present. Prepared export also occupies about 2.86 GB. |
| Mendeley FoodClass v2 | 1.24 GB | Landing-page ZIP size; extracted size and overlap unknown. |
| Zenodo 18904638 | 1.0 GB | Landing-page ZIP size; extracted size and overlap unknown. |
| FreshVeg Kaggle 12k | Unverified | Paper reports 12,000 images; Kaggle archive size could not be inspected. |
| PackEat | Unverified | 100,000+ images are reported; archive size was not visible in the inspected sources. |

The three sized candidate/source archives total about 5.1 GB before extraction, excluding the already-local Hugging Face cache and all unknown-size sources. Allow at least another archive-sized copy for extraction and room for deduplication/output manifests; actual extracted requirements must be measured from each archive before approval. Do not download the Mendeley, Zenodo, Kaggle, or PackEat archives in bulk until their suitability, rights, and sizes are confirmed.

## Risks and limitations

- The current 99.375% test accuracy is measured on the existing 480-image held-out split from the same 3,200-image source. It does not demonstrate robustness to new cameras, backgrounds, varieties, storage conditions, or any additional category.
- The current classifier predicts only `fresh` or `rotten` and has no produce identity output. Applying it to new categories without representative labeled training and independent evaluation would be unsupported.
- The current COCO detector's allowlist is not a substitute for target-domain detector evaluation. It cannot reliably recognize all requested produce and COCO has no dedicated class for many of them.
- Dataset size alone does not establish independent sample count. The Hugging Face dataset already contains exact duplicate groups; near-duplicates were not assessed. The Mendeley and Zenodo sources aggregate or collect public datasets and may overlap each other or FreshVeg.
- Freshness is a visual label, not a food-safety or edibility judgment. `Rotten` and any multi-stage condition terms need consistent definitions across annotators and datasets.
- A mixed scene can have different conditions per item. Image-level labels cannot be copied to every detected crop unless the source annotations establish the object-to-condition mapping.
- Licenses may cover the article or repository record rather than every image inside a dataset assembled from third-party websites. Verify dataset-file rights and model-training/redistribution permissions before use.

## Recommended next phase

**Phase 11B: Rights-first, small-sample archive inspection and label-map validation.** Do not train yet. First confirm the license and inspect only metadata/representative samples (without extracting a full archive if preview/metadata suffices) for the FreshVeg Kaggle source, Mendeley FoodClass, Zenodo 18904638, and PackEat. Produce a signed-off 15-class inventory with per-source counts, raw condition mappings, annotation formats, checksums, and duplicate estimates. If the FreshVeg dataset's boxes and rights validate, select it as the initial multi-class, multi-condition training candidate for its ten covered categories, combine only eligible HF freshness samples after de-duplication, and collect/identify sources for Onion, Broccoli, Lemon, and Pear before promising full 15-category freshness coverage. Preserve a separate source-held-out test set and plan detection and freshness evaluation as separate tasks.

## Source links

- [Hugging Face dataset card](https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification)
- [Mendeley FoodClass v2](https://data.mendeley.com/datasets/5fjkkv5xgt/2)
- [Zenodo 18904638 detection dataset](https://zenodo.org/records/18904638)
- [FreshVeg paper](https://www.mdpi.com/1424-8220/22/21/8192) and [linked Kaggle dataset](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset)
- [PackEat paper](https://www.nature.com/articles/s41597-025-06298-6) and [Zenodo record](https://zenodo.org/records/16901177)
