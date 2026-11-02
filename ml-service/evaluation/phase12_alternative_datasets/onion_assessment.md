# Onion source assessment

## Records reviewed

- [Zenodo: Image Dataset of Red and White Onion Bulbs and Leaves](https://zenodo.org/records/20254934), DOI `10.5281/zenodo.20254934`, v1 published 17 May 2026. The record describes 16,300 images collected in local markets in Pune from July 2025 to February 2026: 12,260 bulb images and 4,040 leaf images. It describes red/white varieties, healthy/unhealthy status, and single/multiple arrangements. The listed files are `All Metadata.xlsx` (1.3 MB) and `Onion Image Dataset.zip` (1.6 GB). The Zenodo Rights/License field is blank.
- [Mendeley Data v2](https://data.mendeley.com/datasets/42bcyncfhy/2), DOI `10.17632/42bcyncfhy.2`, published 9 February 2026. Its description covers 16,300 red and white onion bulb/leaf images and healthy/unhealthy grouping; record displays CC BY 4.0. Its file listing did not expose downloadable file metadata in the reviewed page. The two record versions appear related by matching title, authors, categories, and counts; exact archive identity was not checked.

## Suitability

The source distinguishes bulb images from leaf images at a top level in Zenodo's description, but the accessible metadata does not show exact healthy/unhealthy counts for bulb-only images or link each record to an independently auditable row. The healthy/unhealthy categories do not establish freshness: unhealthy could include disease, mechanical damage, discoloration, sprouting, or other defects, and the source does not define those labels as Rotten. Do not map healthy to Fresh or unhealthy to Rotten.

The authors describe their own smartphone collection from local markets. This supports a claimed first-party collection method, but the Zenodo record does not display a license and does not provide per-image contributor/source metadata in the reviewed page. Mendeley v2 displays CC BY 4.0, but its archive/file list was not inspectable and it is unclear whether it is byte-for-byte the same release. Rights and attribution therefore remain insufficiently reconciled for acquisition under this phase's gate.

## Decision

**Exploratory Onion bulb imagery only; not suitable for Fresh/Rotten classifier labels as documented.** No onion archive or metadata workbook was downloaded. Onion remains a missing Fresh/Rotten data category and needs explicitly defined spoilage labels with rights-cleared bulb images.
