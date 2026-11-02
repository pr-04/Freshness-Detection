# Freshness labeling guide for visual image datasets

## Scope

Labels describe visible evidence on the photographed produce item at the time of capture. They are not food-safety determinations and cannot establish internal condition from an exterior photograph.

## Fresh

Use **Fresh** when the visible portions show no clear signs of decomposition or spoilage under the category-specific rubric. Normal color/shape variation, soil, minor surface marks, small healed scratches, or an isolated minor bruise are not sufficient reasons to call an item Rotten. Do not infer firmness, smell, taste, or internal quality from an image.

## Rotten

Use **Rotten** only when the visible evidence clearly indicates active decomposition/spoilage, such as visible mold/decay, widespread wet or collapsed tissue, leaking/soft breakdown, or extensive progressive decomposition patterns defined for that vegetable. Define category-specific examples before collection. A defect label, disease symptom, bruise, cut, discoloration, or deformity alone is not enough; if it does not clearly establish visible spoilage, use Uncertain or a separate defect annotation.

## Uncertain

Use **Uncertain** when the image does not provide enough evidence: a potentially internal defect, ambiguous discoloration, obstruction, blur, poor lighting, an unshown side, an immature/ripeness difference, damage without clear decomposition, or disagreement between assessors. Keep Uncertain cases out of binary Fresh/Rotten candidate training data; preserve them in a separate review/holdout ledger.

## Recording and consistency

- Apply the decision to the physical item, then associate all its views with that one item-level label.
- Record the visible cue and rubric version, not only the class name.
- Do not translate `Defective`, `Good/Bad`, `Healthy/Unhealthy`, `Mild`, or `Semi-Fresh` into these labels without direct, documented definitions and a separately approved mapping.
- Preserve the source label and normalized label in separate fields.
- Track disagreements and adjudications without overwriting original decisions.

## Safety limitation

FreshGuard's visual label is an image classification result only. Appearance can miss internal spoilage, contamination, or pathogens. A `Fresh` result must never be presented as proof that food is safe to eat.
