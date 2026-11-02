# Onion dataset assessment — Phase 9

**Checked:** 2026-10-31. **No files downloaded.**

## Conclusion

No Onion data exists in the local FreshGuard vegetable inventory. External sources contain actual onion bulbs, but their condition labels do not establish FreshGuard Fresh/Rotten labels. Onion should remain excluded from a training candidate until both label semantics and rights are verified.

## Mendeley Data, version history

The user-provided [v1 record](https://data.mendeley.com/datasets/42bcyncfhy/1) is superseded by [v2](https://data.mendeley.com/datasets/42bcyncfhy/2), DOI `10.17632/42bcyncfhy.2`. Mendeley metadata reports v1 at 24,000 images and 2.25 GB; v2 reports 16,300 images and about 1.5 GB. The v2 description covers red and white onion bulbs and leaves, groups bulbs by healthy/unhealthy and single/multiple, and says images are raw with serial identifiers. The record reports CC BY 4.0. No archive was downloaded, so neither count nor folder-to-image mapping was independently verified.

These are actual harvested bulb images by the record description, with leaves also included. The record does **not** state Fresh and Rotten as class names, give class counts, or define whether “unhealthy” means spoilage rather than damage, disease, dehydration, or sprouting. CC BY 4.0 is a permissive record license, but per-image rights/provenance and attribution were not checked. Keep the bulb subset separate from leaf images and do not map unhealthy to Rotten automatically.

## Zenodo record

The [Zenodo record 20254934](https://zenodo.org/records/20254934) reports 16,300 images: 12,260 bulbs and 4,040 leaves, classified by red/white variety, healthy/unhealthy condition, and single/multiple arrangement. It lists a 1.6 GB ZIP and 1.3 MB metadata workbook. The Rights section showed no license value when checked; image-level counts and labels were not downloaded/verified. Author names and title align with the Mendeley record family, so cross-record overlap is **likely**, but not confirmed without hashes. Do not combine versions as independent data.

## FreshGuard decision and next checks

- **Explicit Fresh/Rotten labels:** not verified in either record.
- **Healthy/unhealthy equivalence:** not established.
- **Actual harvested bulbs:** yes, claimed by both records; exclude leaves for this task.
- **Commercial reuse:** Mendeley v2 lists CC BY 4.0 at record level; Zenodo v1 license was not displayed. Per-image/source rights still require confirmation.
- **Current suitability:** conditional visual-data source only; not suitable as direct binary training data yet.
- **Next steps:** clarify Mendeley v1/v2 and Zenodo relationships, obtain condition definitions and per-class counts, preserve bulb IDs, verify provenance/attribution, review single vs multiple bulb images, then compare hashes only after separate approval to download.

Healthy means the source’s own condition terminology; it is not assumed to equal FreshGuard “Fresh.” Do not use onion foliage or plant-disease images as produce freshness data.
