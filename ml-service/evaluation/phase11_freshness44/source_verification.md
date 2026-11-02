# Source verification

**Review date:** 2026-10-31  
**Primary source:** [Mendeley Data, Cleaned and Split Version of Freshness44 Dataset](https://data.mendeley.com/datasets/ns74rx364w/1)  
**DOI:** [10.17632/ns74rx364w.1](https://doi.org/10.17632/ns74rx364w.1)

## Cleaned Mendeley version

The publisher page was readable in the research browser. It names the dataset “Cleaned and Split Version of Freshness44 Dataset,” contributor Kevin Reynald, Version 1, publication date 24 August 2026, and DOI 10.17632/ns74rx364w.1. Its description says it is a modified version of Siavash93's original Freshness44, with redundant data removed and training/testing splits added. The record displays CC BY 4.0 and links to the original Kaggle dataset.

The page’s Files section contains no visible file rows, filenames, file sizes, README contents, or directory listing in the accessible page representation. The page instructs users to download a README first, but that README could not be accessed or inspected. The dataset page can be visited, but the available evidence does not establish which archives are downloadable, their sizes, their contents, or whether the record’s file endpoint is accessible without authentication.

The official Mendeley Data API documentation describes public dataset and file metadata endpoints, including dataset files and zip metadata. Attempts from the project shell to retrieve the Mendeley page and API endpoints failed with `No such host is known` for `data.mendeley.com` and `api.data.mendeley.com`. This is a shell DNS/connectivity limitation; it does not prove that Mendeley is unavailable to the user or browser. The web research browser could render the landing page, but not its file metadata. No further shell retries were made.

### Verification checklist

| Question | Finding |
|---|---|
| Record accessible? | Yes, publisher landing page readable in research browser. |
| Publisher/version/date? | Mendeley Data; Version 1; published 24 Aug 2026; contributor Kevin Reynald. |
| Actual downloadable files, names, sizes? | Not exposed in accessible page/API responses; unverified. |
| README/directory structure? | Not accessible; unverified. |
| Exact categories and Fresh/Rotten definitions? | Not verified from derivative archive. Paper reports 22 produce types and binary Fresh/Rotten, but this does not prove derivative contents. |
| Original vs augmented counts? | Not verified from archive. |
| Train/test/validation counts? | Record description asserts train/test split; no manifest or counts accessible. Validation split not established. |
| Duplicate removal method? | Record asserts redundant data removal; method, thresholds, and results unavailable. |
| Split unit/group leakage? | Unknown; no evidence whether split is image-level or source/group-level. |
| Record license/attribution? | Record displays CC BY 4.0. Cite contributor Kevin Reynald and DOI, preserve license text and changes if used. |
| Inherited rights for constituent images? | Unresolved. Record license alone does not document the five source datasets' rights or image-level attribution. |

## Original Freshness44 comparison

The Mendeley page states it modifies Siavash93’s original Freshness44 and links to [the original Kaggle page](https://www.kaggle.com/datasets/siavash93/freshness44). It does not give a file-level manifest or describe how many files were removed, renamed, relabeled, or reassigned. Thus the cleaned version cannot be confirmed as equivalent to the paper’s 53,616-image dataset or as retaining all its target categories.

The [2025 Sensors article](https://www.mdpi.com/1424-8220/25/19/5955) reports Fresh/Rotten counts in its category table. Phase 10 transcribed those counts into `ml-service/evaluation/phase10_external_acquisition/external_dataset_comparison.csv`; they are paper-reported reference values only. The paper/article’s open-access license does not by itself establish rights to the image files. No claim is made here that the Mendeley derivative counts equal the paper values.

No original Kaggle archive was downloaded. Whether it is a separate or equivalent archive, and which images/categories differ, remains unverified.

## Rights and attribution decision

The Mendeley record's CC BY 4.0 declaration is a record-level statement. Freshness44 is described as merged from five public source datasets. The record does not identify those five sources or provide per-image source URLs, licenses, authors, or attribution requirements in the accessible metadata. Consequently, the right to reuse each constituent image—including for commercial use or model training—cannot be verified from the material reviewed. This is an unresolved provenance issue, not a legal conclusion.

If a later review obtains the archive, retain its original attribution and source metadata; separately document each image's source and applicable license where available. Exclude images whose rights cannot be verified under the project's chosen policy. Request the contributor's written clarification identifying all upstream datasets and their rights/attribution terms before treating record-level CC BY as sufficient.

## Acquisition gate

**NO-GO.** Do not download until the actual file list, archive byte sizes, README, directory/class/split manifests and the upstream source/license chain can be inspected, and the image rights are sufficiently documented. The record page alone is not enough to satisfy the user's explicit pre-download checks. Disk free space was approximately 124.6 GB at review time, but disk capacity does not cure these source/rights blockers. No authentication credentials were requested or used.

## Sources

- [Mendeley cleaned derivative record](https://data.mendeley.com/datasets/ns74rx364w/1)
- [Mendeley Data API documentation](https://data.mendeley.com/api/docs/)
- [Original Freshness44 Kaggle page](https://www.kaggle.com/datasets/siavash93/freshness44)
- [Freshness44 research article](https://www.mdpi.com/1424-8220/25/19/5955)
- [Creative Commons Attribution 4.0 deed](https://creativecommons.org/licenses/by/4.0/)
