# Label semantics review

## Rules applied

FreshGuard's binary task is visual Fresh versus Rotten for one produce item per image. A label was not mapped to either class unless the source defines it in those terms. `Mild`, `Semi-Fresh`, `Good`, `Bad`, `Healthy`, and `Unhealthy` remain distinct source labels.

| Source | Original label semantics | Fresh/Rotten mapping decision |
|---|---|---|
| FruQ-DB | Fresh / Mild / Rotten, time-lapse frame dataset. | Preserve all three; no binary collapse. Could only support separate exploratory three-class work if license/video rights, crop/category validity, and video-aware split are resolved. |
| FoodClass v2 | Record says 2–4 conditions but does not enumerate all labels in accessible listing. Local subset records normalized Fresh/Rotten folders for nine produce categories. | Do not assume the full dataset's folder names or source labels establish independent freshness truth. Audit local labels and rights; existing conflicts remain unresolved. |
| Onion bulbs/leaves | Healthy / Unhealthy, with variety and single/multiple arrangement. | Not equivalent to Fresh / Rotten. Unhealthy may refer to defects, disease, physical damage, or quality; source does not establish rot. Keep as distinct exploratory labels. |
| AgriFreshNET | Fresh / Semi-Fresh / Rotten. | Preserve all three. Semi-Fresh cannot be merged into Fresh or Rotten without explicit source rubric and a separately approved policy. |
| Tomato_detection | YOLO boxes use Fresh and Rotten classes; reported original images manually boxed. | Label words align with the task, but this is an object-detection export with unspecified upstream image sources and augmented copies. Need rights/source IDs, crop review, and split leakage analysis before classifier use. |
| Good/Bad carrot | Good is smooth/firm, uniform and free of visible defects. Bad includes cracks, bruises, mold, discoloration, deformity, wilting and shriveling. | Do not map Good=Fresh or Bad=Rotten. Bad combines spoilage with non-spoilage quality/shape defects. |
| 2022 ten-produce paper dataset | Fresh / Rotten categories, approximately 600 images per category. | Semantically direct in paper; image files are gathered from mixed web/mobile sources and sometimes show multiple items. Rights, image-level labels, actual files and source overlap remain unresolved. |
| Freshness44 | Paper reports Fresh / Rotten after merging five sources. | Paper labels are not archive-verified; source-level semantics and image provenance may vary. No Phase 12 acquisition. |

## Local conflicts and duplicates

The Phase 9 local curation report records exact-hash Fresh/Rotten conflicts in Carrot (17 groups/35 rows) and Tomato (3 groups/6 rows). These are unresolved; neither label is selected. Phase 9 also flags 4,686 same-category/same-label exact duplicate groups and 5,692 duplicate extra rows. Perceptual matches remain candidates only. Phase 12 did not rehash or alter the local dataset.
