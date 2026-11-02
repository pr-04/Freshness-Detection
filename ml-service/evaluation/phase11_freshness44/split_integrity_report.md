# Split integrity report

**Status: NOT EVALUATED — cleaned archive unavailable.** The Mendeley record says the derivative was split into training and testing sets, but no archive, README, file list, split manifest, or image identifiers were accessible. No claim is made about split counts, whether a validation set exists, the split unit, or whether related images cross splits.

The Phase 9 local vegetable audit reports that its local exact duplicate groups did not cross the existing split values, but those are local Mendeley FoodClass images, not Freshness44. That finding cannot validate the cleaned Freshness44 splits. Existing Project-AgML and vegetable split manifests were not modified.

If a future acquisition is approved, compute exact hashes and perceptual-hash candidates first; identify same-source, near-duplicate, augmentation, and repeated-subject groups; then report group intersections across train/test/validation. Do not edit the supplied splits in this audit. If leakage is found, retain the original archive and recommend a separate group-aware split for future experiments. Keep any existing untouched test set reserved for final evaluation.
