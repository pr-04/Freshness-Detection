# FreshGuard AI — Phase 10 External Dataset Verification & Controlled Acquisition

**Review date:** 2026-10-31  
**Outcome:** Metadata/paper research completed; **no external dataset passed all acquisition gates and no archive was downloaded**. The staging area is intentionally empty. No training, model, app, or local dataset changes were made.

## Executive findings

- Freshness44 has the strongest reported coverage: its paper lists **53,616 images across 22 produce types**, with Fresh/Rotten counts for the six currently supported fruits and five of the six target vegetables. Onion is absent. The table counts are paper-reported, not verified from archive files. The Kaggle page title resolves, but current files/version/license are not readable in this review. The dataset merges five public sources; image-level rights and overlap are unresolved. No download.
- The five-fruit/five-vegetable paper-linked Kaggle source also reports roughly 600 images per class for Potato, Carrot, Tomato, Cucumber and Bell Pepper and says about 70% of the 12,000 source images are single-object. These are paper-reported figures only. The current Kaggle archive and license were not verifiable. No download.
- AgriFreshNET’s publisher record reports 14,500 images, 24 classes, three freshness stages, and CC BY 4.0, but does not expose the exact class list, target-category counts, archive details, or label rubric in reviewed metadata. No download.
- Cucumber sources use Good/Bad. Their descriptions include damage, disease, bruising, irregularity and rot; those labels cannot be silently converted to Fresh/Rotten. No download.
- Onion sources contain harvested bulb images, but use Healthy/Unhealthy or otherwise lack explicit Fresh/Rotten classes. The Zenodo Onion record has no license visible. No suitable Onion Fresh/Rotten source was verified.
- The Malaysian Food Freshness Zenodo DOI could not be opened at the original Zenodo record/API. A secondary NLM catalog reports Apple, Banana, Mango, Potato, Tomato and Bread with CC BY 4.0, but this is insufficient for download approval.
- **Downloads: 0; archives staged: 0; extracted images: 0.** No archive checksums or image-level overlap counts are claimed.

## Source verification summary

All source pages were checked read-only on 2026-10-31. `source_verification.csv` contains exact URLs/DOIs, reported counts, label names, accessibility, license status, overlap risk and acquisition outcome.

| Source | What could be confirmed | What remains unverified | Decision |
|---|---|---|---|
| Five-vegetable dataset linked to 2022 paper | Paper reports Fresh/Rotten categories, counts, 12,000 total original images, manual YOLO annotation and ~70% single-object photos | Current Kaggle version/files, dataset license, class totals against files, individual photo sources, overlap | **PROMISING – VERIFY BEFORE DOWNLOAD** |
| AgriFreshNET | Publisher record reports 14,500, 24 classes, Fresh/Semi-Fresh/Rotten, CC BY 4.0 and original RGB data | Exact 24 classes, target categories/counts, archive size/integrity, duplicates, object count and rubric | **INSUFFICIENT INFORMATION** |
| Cucumber 9rs9vmm2bv | Record reports 500 Good/500 Bad and CC BY 4.0; market/storage description | Archive contents; text does not clearly explain how `Bad` relates to spoilage | **CONDITIONAL – LABEL SEMANTICS UNCLEAR** |
| Cucumber zncrtr2yhn | Record reports over 500 balanced Good/Bad images, CC BY 4.0, black-background daylight capture | Exact counts; Bad combines rot with disease, damage, bruises and irregular shape | **CONDITIONAL – LABEL SEMANTICS UNCLEAR** |
| Onion Mendeley v1 | 24,000 images and 2.25 GB reported; CC BY 4.0; bulb and leaf images, Healthy/Unhealthy | Exceeds the 2 GB archive cap; no Fresh/Rotten semantics | **CONDITIONAL – LABEL SEMANTICS UNCLEAR** |
| Onion Mendeley v2 | 16,300 images and about 1.5 GB reported; CC BY 4.0; raw bulb/leaf photos, Healthy/Unhealthy | No Fresh/Rotten mapping, class counts, or per-image rights inspection | **CONDITIONAL – LABEL SEMANTICS UNCLEAR** |
| Onion Zenodo 20254934 | Record reports 16,300 images (12,260 bulbs, 4,040 leaves), archive 1.6 GB | Rights field blank; no Fresh/Rotten labels; possible relation to Mendeley versions not file-verified | **PROVENANCE OR LICENSE UNVERIFIED** |
| Freshness44 Kaggle | Paper reports 53,616 images, 22 produce types, binary Fresh/Rotten counts; Kaggle title page resolves | Current archive/version/size/license, exact file counts, image rights, duplicates and overlap | **PROMISING – VERIFY BEFORE DOWNLOAD** |
| Freshness44 Mendeley cleaned/split derivative | Record says it removes redundant data and creates train/test splits; record states CC BY 4.0 | Archive contents/size and rights for its five underlying source collections | **PROVENANCE OR LICENSE UNVERIFIED** |
| Malaysian Food Freshness Zenodo 20843858 | NLM catalog reports CC BY 4.0 and Apple/Banana/Mango/Potato/Tomato/Bread | Original Zenodo record/API inaccessible; no verified files/counts/size/license | **INACCESSIBLE** |
| Tomato_detection | Mendeley record reports Fresh/Rotten boxes, CC BY 4.0, 800 base images and 1,600 export | Source rights, exact label counts, archive contents and ambiguous augmentation arithmetic | **PROVENANCE OR LICENSE UNVERIFIED** |

### Freshness44 paper-reported counts

Counts are **reported by the paper**, not verified from the Kaggle archive. Target fruits are Apple 3,468/4,263; Banana 3,513/3,605; Guava 1,352/1,329; Orange 3,164/3,443; Pomegranate 6,140/1,387; Strawberry 803/795. Target vegetables are Potato 602/562; Tomato 1,905/2,504; Carrot 605/507; Cucumber 833/692; Bell Pepper 1,634/2,108. Onion is not listed. Order is Fresh/Rotten. The paper describes Freshness44 as a merge of five public datasets and discusses mixed/multiple-item images; one-produce-per-image compliance is not confirmed.

The paper’s source table also notes the five-vegetable dataset counts: Potato 615/585, Carrot 620/580, Tomato 604/596, Cucumber 608/593, Bell Pepper 611/591. These are not downloaded counts and are not independently confirmed.

## Licenses, attribution and provenance

Dataset-record CC BY 4.0 statements were recorded where visible. CC BY 4.0 permits commercial reuse of material covered by the license with attribution and other terms, but it does not prove that all images in an aggregated set were authorized by their original rights holders. The paper-linked Kaggle and Freshness44 archives lack a verified dataset/image license in this review. Onion Zenodo’s Rights field was blank; Malaysian Zenodo’s original record was inaccessible. See [license and provenance report](license_and_provenance_report.md) and the [official CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/).

## Overlap, staging and integrity

External image-level overlap was **not checked** because no external archive was acquired. Metadata indicates high/possible overlap risks: Freshness44 merges public datasets; the paper-linked dataset is sourced from online repositories and may overlap the local FoodClass aggregation; Onion Mendeley/Zenodo records appear related; Tomato_detection also uses multi-source imagery. These are risks, not confirmed duplicates. `duplicate_and_overlap_report.csv` records each risk explicitly.

The staging path `ml-service/datasets/external_staging/phase10/` contains empty `archives/` and `extracted/` directories plus a README. `download_manifest.csv` records no acquisition. `image_integrity_report.csv` records that no external images were available to test. The reproducible script is `scripts/verify_staged_data.py`; it can calculate archive hashes, validate image files/dimensions, and check exact/perceptual overlaps if a future phase approves and stages data.

## Category-level readiness

`category_coverage.csv` and `final_readiness_matrix.csv` distinguish paper/record reports from verified archive counts. The six fruits and five vegetables have promising **reported** Fresh/Rotten coverage in Freshness44; none is cleared for acquisition because archive licensing/provenance and image contents remain unverified. Onion remains **LABEL SEMANTICS UNCLEAR** and needs explicitly labelled, rights-cleared onion bulbs. No vegetable has data approved for training.

## Acquisition decision and controls

No dataset met all initial source, label, license/provenance and archive-metadata checks. Therefore no download was attempted. Known Onion v1 archive size exceeds the 2 GB per-archive cap; no other archive size was sufficiently verified to schedule a download. Total archive downloads were 0 bytes. The 5 GB phase budget was not used. A free-space check was not performed because no dataset passed the gates and no download was scheduled.

## Files and checks

Created in `ml-service/evaluation/phase10_external_acquisition/`: comparison, verification, category, license, download, image integrity, overlap and readiness reports; reproducible script; README; this report. Created empty staging directories and staging README.

Checks performed: reviewed official Mendeley/Zenodo/Kaggle records where accessible; checked the 2022 and Freshness44 papers; inspected source labels/licenses/access status; compared reported category counts; verified project Phase 9 local candidate counts from its existing summary; confirmed no external archives were downloaded. No application files, checkpoints, local source images, labels or splits were modified.

## Sources checked

- [Five-vegetable Fresh/Rotten paper](https://www.mdpi.com/1424-8220/22/21/8192) and [Kaggle page](https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset)
- [AgriFreshNET Mendeley record](https://data.mendeley.com/datasets/42m5tb7yv9/1)
- [Cucumber 9rs9vmm2bv](https://data.mendeley.com/datasets/9rs9vmm2bv/1) and [zncrtr2yhn](https://data.mendeley.com/datasets/zncrtr2yhn/1)
- [Onion Mendeley v1](https://data.mendeley.com/datasets/42bcyncfhy/1), [v2](https://data.mendeley.com/datasets/42bcyncfhy/2), and [Zenodo 20254934](https://zenodo.org/records/20254934)
- [Freshness44 paper](https://www.mdpi.com/1424-8220/25/19/5955), [Kaggle page](https://www.kaggle.com/datasets/siavash93/freshness44), and [Mendeley cleaned/split derivative](https://data.mendeley.com/datasets/ns74rx364w/1)
- [Malaysian Food Freshness Zenodo DOI](https://doi.org/10.5281/zenodo.20843858) and [NLM catalog metadata](https://datasetcatalog.nlm.nih.gov/dataset?q=0003004379)
- [Tomato_detection Mendeley record](https://data.mendeley.com/datasets/vy5y8p2kdb/1)
