# AgriFreshNET assessment

Source: [AgriFreshNET Freshness and Shelf-Life Image Dataset, Mendeley Data](https://data.mendeley.com/datasets/42m5tb7yv9/1), DOI `10.17632/42m5tb7yv9.1`, version 1, published 2026-07-30.

## Publisher-reported details

The record reports 14,500 RGB images across 24 classes, with Fresh, Semi-Fresh, and Rotten stages. It describes smartphone images from markets, supermarkets, households, farms, and storage facilities, plus approximate shelf-life annotations. The record lists CC BY 4.0. Reproduction instructions refer to `Raw Data.zip` and `Processed_Data.zip` and describe class/freshness organization.

## Unverified requirements

The accessible record does not enumerate the 24 class names or per-category counts, define the class/stage boundaries, provide archive file sizes or checksums, or identify per-image source/creator/licensing metadata. It does not establish whether the target vegetables Potato, Tomato, Onion, Carrot, Cucumber, and Capsicum are included, how many are in each state, or whether Raw and Processed files contain originals, resized copies, or augmentations. Files were not downloaded, and there was no direct verification of image-level folder structure, label format, source URLs, or leakage.

The CC BY 4.0 statement is record-level. The page describes collection across real-world settings, but does not document individual image attribution or clarify whether all rights are held by the listed contributors. No commercial-use conclusion is made beyond the record's stated license.

## Suitability

AgriFreshNET is the strongest *metadata lead* for a possible three-stage image-classification experiment, because the record explicitly names Fresh, Semi-Fresh, and Rotten. It is not yet a verified candidate for any target vegetable. Keep all three labels distinct; never map Semi-Fresh automatically into Fresh or Rotten. Before considering acquisition, obtain the full class manifest and definitions, archive sizes/checksums, original-versus-processed lineage, per-image source/license documentation, and split/item identifiers. Confirm target categories and class counts against actual files first.

**Decision:** conditional research lead; no acquisition and no target vegetable is cleared.
