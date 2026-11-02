# VegQual assessment

## Publisher record and accessible metadata

Primary data record: [Figshare, VegQual: A Multiclass Dataset for Real-Time Fresh and Defective Vegetables](https://figshare.com/articles/dataset/A_Multiclass_Dataset_for_Real-Time_Fresh_and_Defective_Vegetables/30596084), DOI `10.6084/m9.figshare.30596084.v4`, version 4 dated 2026-03-29. The public page reports a 183.48 MB download and CC BY 4.0. The record describes 2,032 raw images of seven vegetables and 4,736 annotated instances across 14 fresh/defective object classes. The paper page at Nature redirected to an identity provider in this review; the Figshare record was accessible. The matching author repository provides a class summary and methodology, but the repository is not a substitute for the actual archive.

The Figshare page's download link resolved to file ID `62799448`, but the research browser returned HTTP 403 on the file request; the shell could not resolve `api.figshare.com`. No file was downloaded. The actual archive filename, archive members, per-file sizes/checksums, class-ID order, and actual YOLO rows therefore remain unverified. The one-file displayed size is within a typical small research download, but the content gate is incomplete.

## Categories and reported counts

The record and author repository name the seven vegetables and 14 paired classes: Tomato Fresh/Defective, Potato Fresh/Defective, Bitter Gourd Fresh/Defective, Pointed Gourd Fresh/Defective, Onion Fresh/Defective, Capsicum Fresh/Defective, and Brinjal Fresh/Defective. The author repository reports these per-class values as “Defective Images / Fresh Images”:

| Category | Defective (reported) | Fresh (reported) |
|---|---:|---:|
| Tomato | 190 | 167 |
| Potato | 105 | 442 |
| Onion | 518 | 245 |
| Capsicum | 295 | 569 |

The four named target categories are present by name. These values are **not verified unique-image counts**: the Figshare record reports 2,032 images and 4,736 annotated instances, whereas the author README calls 4,736 “annotated images” and its class table sums to 4,736. Treat the table as author-reported class counts with an unclear denominator (instances versus images), not as verified per-class image totals. Exact class-ID-to-name mapping is not available without the archive's YAML/label metadata.

## Task and label limitations

This is an object-detection dataset, not a direct image-level classification set. The record reports YOLO TXT labels with normalized boxes and 70/20/10 image splits (1,422 train, 406 validation, 204 test), resized to 640×640 with EXIF orientation correction. It says 4,736 object instances across 2,032 raw images; some images therefore contain multiple annotated objects on average. No file-level annotation or bbox quality check was performed.

The classes are Fresh and Defective. The accessible description mentions freshness, texture, color variation, and physical defects, but does not define a reproducible defect rubric or establish that every defective instance is decomposed/rotten. Bruising, mechanical damage, shape defects, disease, and cosmetic changes are not equivalent to Rotten. **Do not map Defective to Rotten.** Preserve the source label exactly.

YOLO boxes could support a separate produce localization or defect-detection study. Cropping each box would create object crops, not validated Fresh/Rotten labels; a whole image may contain multiple items/classes. Deriving a single-item classifier dataset would require class-ID verification, annotation validation, and label semantics that the public page does not provide. This phase did not make crops or alter labels.

## Source, license, overlap, and decision

The Figshare record displays CC BY 4.0 and attributes the dataset to the listed contributors. The author repository says images were captured with multiple smartphones in daylight and indoor light; the article abstract describes local-market collection. These support an author-reported original capture method, but individual creator/rights-holder status and any third-party image contributions were not independently checked. Preserve attribution and modifications if the data is used; do not infer more than the published license and description establish.

Exact overlap with the local Mendeley FoodClass inventory was **not tested** because the VegQual file was inaccessible and no image hashes were available. There is no evidence of overlap or non-overlap. Supplied split leakage by item or capture session is also unknown; the reported image-level split alone does not show whether multiple views of the same specimen cross splits.

**Decision:** useful candidate for future, separate object localization / fresh-versus-defective detection research, subject to access and archive validation. **Not usable as a Fresh/Rotten classifier dataset on current evidence.** No download or image-by-image review was performed.
