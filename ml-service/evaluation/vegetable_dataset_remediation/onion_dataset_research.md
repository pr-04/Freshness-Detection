# Onion dataset research

**Research date:** 2026-10-31. No dataset was downloaded.

## Finding

A credible **candidate source of real onion bulbs** was found, but **no candidate is cleared as a FreshGuard Fresh/Rotten dataset**. The most directly relevant public record is Zenodo's [Image Dataset of Red and White Onion Bulbs and Leaves](https://zenodo.org/records/20254934). The record describes 16,300 images: 12,260 bulb images and 4,040 leaf images, stratified by red/white variety, “healthy/unhealthy” status and single/multiple arrangement. Its metadata spreadsheet and a 1.6 GB archive are listed. The Rights section displayed no license value during this review. The record does not expose counts for health labels or a confirmed mapping from “healthy/unhealthy” to Fresh/Rotten. **Do not use its leaves, and do not map health labels to freshness without reviewer-defined criteria.**

A smaller alternative is the [ONIONVISION onion quality assessment repository](https://github.com/nachiket-mr360/onion-quality-assessment). It reports 293 paired images from 92 physical onion groups, with classes HEALTHY 123, DAMAGED 45, ROTTEN 75, and SPROUTED 50 across splits. It is an onion-bulb inspection prototype, and its visible README separates rot from damage and sprouting. The repository does not make a clear reusable image-dataset license or original photo provenance evident; its class totals are small and not representative. This is a lead for rights and metadata inquiry, not an approved source.

A further lead is [VegQual](https://github.com/tarekrahamn/VegQual), whose paper reports fresh/defective produce detection for onion and other vegetables. It covers several vegetables, but “defective” is broader than rotten, category counts and license need confirmation, and it is a detection dataset. It cannot serve as direct image-level freshness labels without annotation review.

## Candidate comparison

| Candidate | Actual bulb images? | Label semantics | Counts verified from public page | License/provenance | Decision |
|---|---|---|---|---|---|
| Zenodo red/white onion bulbs and leaves | Yes; 12,260 bulbs and 4,040 leaves | Healthy/unhealthy, not explicitly Fresh/Rotten | Total bulb/leaf counts only; condition counts not shown | License blank in record UI; market photos; image provenance detail needs audit | Most promising onion image source, but **not approved** |
| ONIONVISION | Yes, onion quality inspection | HEALTHY, DAMAGED, ROTTEN, SPROUTED | 293 paired images / 92 physical groups; class totals in README | Reuse terms and photo provenance unclear | Small review candidate; rights clarification required |
| VegQual / fresh-defective vegetables | Onion among seven vegetables | Fresh/defective; defect is not equivalent to rot | 2,032 images and 4,736 annotated instances overall; category counts not verified | License/source details incomplete in checked public metadata | Detection research lead only |
| Mendeley FoodClass v2 already in project | No onion rows in prepared inventory | — | 0 Fresh / 0 Rotten | Dataset record CC BY 4.0, but source image provenance unresolved | No usable Onion examples currently present |

## Recommended next steps

1. Before any transfer, obtain permission/license clarification and the metadata schema for the Zenodo bulb images; filter bulb images from leaf images using explicit metadata, not filenames alone.
2. Confirm what “unhealthy” means and whether each image’s label corresponds to visible post-harvest spoilage. Ask the dataset authors for a rubric and class counts.
3. For ONIONVISION, request the image-level source/permission and a copy of its dataset terms. Keep DAMAGED and SPROUTED as separate labels pending a FreshGuard rubric.
4. Require reviewers to define whether cosmetic damage, sprouting, dehydration, and internal rot map to Fresh, Rotten, or Uncertain. Avoid equating plant health, crop disease, and food freshness.
5. If approved, create a separate onion review manifest and group all views of the same bulb together before a new train/validation/test split.

## Access and limitations

All pages were checked on 2026-10-31. External pages were read-only. No archive, metadata workbook, image, API result, or model was downloaded. Counts and licenses above are limited to what the public landing pages and repository README reported; per-image labels, file content, actual readability, uniqueness and rights have not been independently verified.
