# Category-wise MobileNetV2 Evaluation

## Method and integrity checks

- Selected 420 test filenames across seven fruits; 418 unique image hashes received exactly one full-image MobileNetV2 forward pass.
- Exact duplicate test files reused the identical prediction and were excluded from metric counts: 2 duplicate file row(s).
- Used only `datasets/prepared/test`; train and validation images were not used.
- Jujube was excluded from evaluation and aggregate metrics; its dataset files were left untouched.
- Checkpoint and metadata class mapping verified: `fresh=0`, `rotten=1`.
- The saved checkpoint had already been evaluated on this held-out test split in the earlier aggregate evaluation. This run adds the fruit-wise breakdown without training or tuning the model.
- CPU inference; RGB conversion, 224×224 resize, ToTensor, and normalization match training/evaluation configuration.
- All selected image paths, unique hashes, expected 30 Fresh/30 Rotten counts per fruit, and image readability were checked before inference.
- No YOLO, boxes, or crops were used. No checkpoint or original dataset files were written.

## Per-category results

| Fruit | Unique N | Fresh correct / Fresh N | Rotten correct / Rotten N | Accuracy | Macro F1 | False Fresh | False Rotten |
|---|---:|---:|---:|---:|---:|---:|---:|
| Apple | 60 | 30/30 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Banana | 60 | 30/30 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Guava | 60 | 30/30 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Orange | 58 | 28/28 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Pomegranate | 60 | 30/30 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Strawberry | 60 | 30/30 | 30/30 | 1.0000 | 1.0000 | 0 | 0 |
| Grape | 60 | 30/30 | 29/30 | 0.9833 | 0.9833 | 1 | 0 |

Per-class precision, recall, and F1 are in the CSV. Confusion matrices use actual rows and predicted columns, ordered Fresh then Rotten:

| Fruit | Matrix `[[Fresh→Fresh, Fresh→Rotten], [Rotten→Fresh, Rotten→Rotten]]` |
|---|---|
| Apple | `[[30, 0], [0, 30]]` |
| Banana | `[[30, 0], [0, 30]]` |
| Grape | `[[30, 0], [1, 29]]` |
| Guava | `[[30, 0], [0, 30]]` |
| Orange | `[[28, 0], [0, 30]]` |
| Pomegranate | `[[30, 0], [0, 30]]` |
| Strawberry | `[[30, 0], [0, 30]]` |
| Overall | `[[208, 0], [1, 209]]` |

## Overall results for the seven selected fruits

- Unique test images counted: 418 (208 Fresh, 210 Rotten); selected test filenames: 420.
- Accuracy: 0.997608.
- Macro precision: 0.997608; macro recall: 0.997619.
- Macro F1: 0.997608; weighted F1: 0.997608.
- Combined confusion matrix (actual rows, predicted columns; Fresh, Rotten): `[[208, 0], [1, 209]]`.
- False Fresh: 1 (actual Rotten, predicted Fresh); false Rotten: 0 (actual Fresh, predicted Rotten).

## False Fresh predictions

| Filename | Fruit | Fresh score | Rotten score |
|---|---|---:|---:|
| `grape_02093_fee4403e3107.jpg` | Grape | 0.502751 | 0.497249 |

## False Rotten predictions

No false Rotten predictions occurred in this evaluation.

## Category ranking and recommendation

- Highest macro F1 in this sample: Apple (1.0000; false Fresh rate 0.0000).
- Lowest macro F1 in this sample: Grape (0.9833; false Fresh rate 0.0333).
- The Orange metric uses 58 unique images because two exact duplicate file rows were excluded; each other fruit uses 60 unique images.
- Provisional candidates for a limited, supervised prototype with fruit category supplied by the user: Apple, Banana, Guava, Orange, Pomegranate, and Strawberry (no false Fresh or false Rotten errors in these small test samples).
- Temporarily withhold Grape from the initial supported choices pending review and additional testing: its one false Fresh prediction is 1 of 30 Rotten unique test images (3.33%).
- These results do not establish production readiness. Even zero observed false Fresh errors among 30 Rotten examples leaves substantial uncertainty; validate candidates on independent real-world images before prototype claims.
- The model itself does not output fruit identity. The provisional category list is not automatic fruit recognition; without user-declared category or a separately evaluated identification/rejection system, the binary classifier will return Fresh or Rotten for unsupported images too.
- Manually inspected the Grape false Fresh image: it shows a bunch with visibly dark/damaged areas on some grapes alongside green-looking grapes. This mixed appearance may make a single image-level label difficult, but one image does not establish the cause of the error.
- A binary MobileNetV2 always returns Fresh or Rotten; it cannot identify fruit, reject non-fruit images, or detect out-of-domain inputs. Scores are not freshness percentages or food-safety estimates.
- Scores are class probabilities, not freshness percentages or food-safety estimates.

## Limitations

- Dataset metrics may not generalize to different cameras, lighting, varieties, backgrounds, or real-world spoilage conditions.
- Existing data preparation grouped exact SHA-256 duplicates in one split; perceptual duplicates and similar re-encodings were not checked.
- The evaluation reports appearance labels only; it does not establish edibility or food safety.
