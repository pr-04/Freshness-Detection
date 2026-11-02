# Phase 9 local/external overlap risk report

**Checked:** 2026-10-31. No external dataset archives or images were downloaded; therefore no external image-level hash or perceptual-hash comparisons were possible.

## Local exact-hash results

The reproducible Phase 9 script recalculated SHA-256 from all local vegetable image bytes. It found 20 Fresh/Rotten conflict hashes in the six-category subset, matching Phase 8: 17 Carrot and 3 Tomato. No exact hash occurred under more than one normalized vegetable category. It identified 4,686 same-category/same-label duplicate groups and excluded 5,692 extra rows while retaining one deterministic path per group. **Zero duplicate groups had retained copies assigned across different existing splits** according to the inventory `split` field. No original split was changed; the candidate manifest carries the original value.

## External-source overlap risks (not confirmed duplicates)

| Candidate source | Risk | Evidence and limitation | Later check if acquisition is approved |
|---|---|---|---|
| Five-fruit/five-vegetable Kaggle dataset described by Mukhiddinov et al. | High / plausible | Paper says material came from Kaggle, Google, Bing and mobile capture. Local FoodClass v2 is itself an aggregation from public repositories. No external archive to compare. | Acquire only an approved class-filtered subset; hash and perceptual-hash compare against local files before any split or training; preserve source records. |
| AgriFreshNET Mendeley | Possible | Same platform, but no target class list or images inspected. Shared platform alone does not prove overlap. | Verify class manifest and compare hashes after approved acquisition. |
| Cucumber Good/Bad Mendeley records (`9rs9vmm2bv`, `zncrtr2yhn`) | Possible | Both are Mendeley cucumber image sets, but descriptions suggest different capture setups/authors. Dataset overlap cannot be ruled out from metadata. | Compare canonical file hashes and visually inspect perceptual candidates after approved download. |
| Onion Mendeley v1/v2 (`42bcyncfhy`) and Zenodo record 20254934 | High / likely related record family | Same title/authors and overlapping healthy/unhealthy bulb/leaf description; image identity is not verified. v1/v2 have different reported counts; Zenodo count aligns with Mendeley v2 description. | Ask publishers/authors about version/record relationship; never pool versions without image-level deduplication. |
| Tomato_detection Mendeley | Possible | Multi-source tomato imagery and local Mendeley aggregation may overlap, but no source-level manifest or archive comparison was available. | Compare exact and perceptual hashes, group augmentations with source originals, then split by original image/source. |
| VegQual / fresh-defective produce | Unknown | Metadata and paper identify produce categories and boxes but do not provide image-level list for comparison; label semantics differ. | Verify archive/license first, then compare image hashes before considering any labels. |

## Split and duplicate safeguards

- The local script preserves each `split` field without moving images. If a future external source is approved, perform overlap checks before assigning any split.
- Group exact duplicates by recomputed SHA-256 and near-duplicate candidates by a documented perceptual method. Treat perceptual hashes as triage, not proof.
- Keep all views/augmentations of one source image, and repeated views of one physical onion, within one split.
- Preserve the current untouched test split; any future combined experiment needs a new, source-aware holdout rather than modifying existing split files.
- Exclude every row from a known conflicting exact-hash group until human review. Never choose a label by majority vote.
