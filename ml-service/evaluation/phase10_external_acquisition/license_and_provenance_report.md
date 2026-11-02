# Phase 10 license and provenance review

**Checked:** 2026-10-31. This is a source-record review, not a legal opinion. No external archive was downloaded.

## Standard for this phase

A dataset-level license can apply only to material the licensor has authority to license. Creative Commons CC BY 4.0 permits sharing/adaptation, including commercial use, when the material is actually covered by the license and attribution, license-link, and change-notice conditions are met. The CC deed also cautions that other rights may apply. See the [official CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/). This project did not independently verify every constituent image right or attribution. Accordingly, most aggregate dataset image-level permissions remain **UNKNOWN / NOT VERIFIED**, even where a dataset record states CC BY 4.0.

## Dataset-specific findings

| Source | Record license / reported use | Attribution evidence | Provenance and commercial-use status |
|---|---|---|---|
| Paper-linked five-vegetable Kaggle dataset | The paper is open access, but the current Kaggle dataset archive license was not visible/verified. Do not transfer the article license to dataset images. | Paper authors and Kaggle account are identifiable; individual photo sources/credits are not. | Paper describes aggregation from Kaggle, Google, Bing and phone images. Per-image license and commercial-use permission UNKNOWN; no download. |
| AgriFreshNET | Mendeley record states CC BY 4.0. | Record lists authors and DOI `10.17632/42m5tb7yv9.1`; cite that record if later used. | Publisher says smartphone RGB photos from real-world settings, but class list, file metadata, per-image provenance and original-author rights were not inspected. Record-level commercial permission only; per-image rights unverified. |
| Cucumber 9rs9vmm2bv and zncrtr2yhn | Both Mendeley records state CC BY 4.0. | Cite record authors/title/DOI, link license and indicate changes. | Records describe captured cucumber images, but no original archives or per-image metadata inspected. Commercial reuse of images is not independently cleared beyond record claim. |
| Onion Mendeley 42bcyncfhy v1/v2 | Both version metadata state CC BY 4.0. v1 archive is reported 2.25 GB; v2 about 1.5 GB. | Cite the exact version, contributors, DOI, license and changes. | Description suggests author-collected bulb/leaf images, but individual rights and fresh/rotten semantics remain unverified. v1 is over the 2 GB cap; v2 fails the label gate. |
| Onion Zenodo 20254934 | Zenodo Rights section displayed no license value. | Cite record authors and DOI if discussing; permission remains unknown. | Claimed market-captured bulbs/leaves, but terms and per-image rights unknown. No archive downloaded. |
| Freshness44 Kaggle composite | Current Kaggle archive license unknown. A later Mendeley cleaned/split derivative record reports CC BY 4.0, but it does not establish rights for all five underlying collections. | Paper and records are citable; the merged dataset’s source-level attribution ledger was not verified. | Composite merges five public datasets and reports 53,616 images. Original source licenses, per-image attribution, commercial-use rights, archive contents/size and transformations remain unverified. No download. |
| Malaysian Food Freshness Zenodo 20843858 | Secondary NLM catalog reports CC BY 4.0; original Zenodo record/API could not be opened. | Secondary catalog names Lim, Chia Shen and DOI; official record and citation requirements not verified. | Treat license, exact contents, source, image counts and commercial-use permission as unverified until the original publisher record can be inspected. No download. |
| Tomato_detection v1 | Mendeley record says CC BY 4.0 and references a Roboflow export. | Record authors/title/DOI and referenced Roboflow Universe source are available. | Record says images were collected from various sources; original source rights/attribution are not itemized. The count/augmentation description is ambiguous. Per-image commercial permission is unverified. No download. |
| Freshness44 cleaned/split Mendeley derivative | Record states CC BY 4.0. | Cite contributor, title and DOI `10.17632/ns74rx364w.1`; retain change notice. | It is explicitly a modified version of a multi-source composite. The record does not resolve rights in the underlying images; exact cleanup/counts/archive size were unavailable. |

## Attribution and acquisition gate

If a source later passes review, retain at minimum its original publisher, canonical URL/DOI, exact version, record license, authors, any source-image identifiers/URLs/license/credit, download date, archive checksum, transformations, and exclusion rationale. Credit authors and original creators where supplied, link the applicable license, and state changes. Keep all original archive files and extracted material in a distinct staging directory.

No dataset in this phase passed all label, source, license/provenance and archive-verification requirements. Therefore no download occurred and no archive checksum exists. The empty acquisition status is recorded in `download_manifest.csv` rather than fabricated.
