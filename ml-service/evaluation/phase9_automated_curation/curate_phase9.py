#!/usr/bin/env python3
"""Conservative Phase 9 vegetable inventory audit and candidate-manifest builder.

Run from any working directory: python curate_phase9.py
Writes only sibling Phase 9 CSV artifacts; reads the original Phase 11B inventory.
Requires Pillow for deterministic image verification and quality heuristics.
"""
from __future__ import annotations
import csv
import hashlib
import math
from collections import defaultdict, Counter
from pathlib import Path
from PIL import Image, ImageStat

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
INVENTORY = ROOT / "ml-service/datasets/expansion_15/dataset_inventory.csv"
CATEGORIES = {"Potato", "Tomato", "Onion", "Carrot", "Cucumber", "Bell Pepper"}
# Transparent triage thresholds; these are flags, not judgments of freshness.
MIN_FILE_BYTES = 1024
MIN_DIMENSION = 64
MAX_ASPECT_RATIO = 5.0
FLAT_STDDEV_MAX = 5.0
FLAT_RANGE_MAX = 15


def csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def actual_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def inspect_image(path: Path):
    """Return actual file hash and image checks; never changes the input file."""
    info = {"file_exists": path.is_file(), "file_bytes": 0, "actual_sha256": "",
            "width": 0, "height": 0, "format": "", "quality_flags": [],
            "quality_metrics": "", "readable": False, "error": ""}
    if not path.is_file():
        info["error"] = "missing_file"
        info["quality_flags"] = ["missing_file"]
        return info
    info["file_bytes"] = path.stat().st_size
    info["actual_sha256"] = actual_sha256(path)
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            info["width"], info["height"] = image.size
            info["format"] = image.format or ""
            gray = image.convert("L").resize((64, 64), Image.Resampling.BILINEAR)
            stat = ImageStat.Stat(gray)
            stddev = stat.stddev[0]
            low, high = gray.getextrema()
            info["quality_metrics"] = f"gray_stddev={stddev:.3f};gray_range={high-low};sample=64x64"
        info["readable"] = True
    except Exception as exc:  # corrupt/unsupported files are recorded, not discarded silently
        info["error"] = f"image_decode_error:{type(exc).__name__}:{str(exc)[:160]}"
        info["quality_flags"] = ["unreadable_image"]
        return info
    flags = []
    if info["file_bytes"] < MIN_FILE_BYTES:
        flags.append("small_file_under_1KiB")
    if min(info["width"], info["height"]) < MIN_DIMENSION:
        flags.append("small_dimensions_under_64px")
    ratio = max(info["width"], info["height"]) / max(1, min(info["width"], info["height"]))
    if ratio > MAX_ASPECT_RATIO:
        flags.append("extreme_aspect_ratio_over_5")
    if stddev < FLAT_STDDEV_MAX and (high - low) < FLAT_RANGE_MAX:
        flags.append("near_uniform_low_contrast_thumbnail")
    info["quality_flags"] = flags
    return info


def main():
    raw = csv_rows(INVENTORY)
    source_rows = [r for r in raw if r.get("normalized_category") in CATEGORIES]
    records = []
    missing_inventory_hash = 0
    inventory_hash_mismatches = 0
    for index, row in enumerate(source_rows, 1):
        path = ROOT / row["relative_image_path"]
        checked = inspect_image(path)
        recorded_hash = (row.get("sha256") or "").lower()
        if not recorded_hash:
            missing_inventory_hash += 1
        elif checked["actual_sha256"] and recorded_hash != checked["actual_sha256"]:
            inventory_hash_mismatches += 1
        records.append({**row, **checked, "inventory_sha256": recorded_hash})
        if index % 5000 == 0:
            print(f"Checked {index}/{len(source_rows)} images", flush=True)

    # Hash globally so identical bytes cannot cross category or condition boundaries unnoticed.
    by_hash = defaultdict(list)
    for rec in records:
        if rec["actual_sha256"]:
            by_hash[rec["actual_sha256"]].append(rec)
    condition_conflict_hashes = set()
    category_conflict_hashes = set()
    for digest, members in by_hash.items():
        if len({m["normalized_condition"] for m in members}) > 1:
            condition_conflict_hashes.add(digest)
        if len({m["normalized_category"] for m in members}) > 1:
            category_conflict_hashes.add(digest)
    conflict_hashes = condition_conflict_hashes | category_conflict_hashes

    # Existing manifest IDs are deterministic and cross-referenced to Phase 8.
    phase8_conflict_file = ROOT / "ml-service/evaluation/vegetable_dataset_approval/conflict_review.csv"
    known_phase8_hashes = set()
    if phase8_conflict_file.is_file():
        known_phase8_hashes = {r["sha256"].lower() for r in csv_rows(phase8_conflict_file) if r.get("sha256")}

    # Same-category, same-label byte-identical copies: retain one deterministic row only.
    duplicate_groups = defaultdict(list)
    for rec in records:
        digest = rec["actual_sha256"]
        if digest and digest not in conflict_hashes:
            duplicate_groups[(rec["normalized_category"], rec["normalized_condition"], digest)].append(rec)
    duplicate_extras = set()
    duplicate_group_for_path = {}
    duplicate_report = []
    for (category, label, digest), members in sorted(duplicate_groups.items()):
        members = sorted(members, key=lambda r: r["relative_image_path"].casefold())
        group_id = f"DUP-{digest[:16]}"
        if len(members) > 1:
            canonical = members[0]
            for member in members:
                duplicate_group_for_path[member["relative_image_path"]] = group_id
            for extra in members[1:]:
                duplicate_extras.add(extra["relative_image_path"])
            for member in members:
                duplicate_report.append({
                    "duplicate_group_id": group_id, "vegetable_category": category,
                    "original_label": label, "sha256": digest,
                    "image_path": member["relative_image_path"],
                    "original_split": member.get("split", ""),
                    "retained_canonical_path": canonical["relative_image_path"],
                    "row_status": "CANONICAL_RETAINED" if member is canonical else "EXCLUDED_DUPLICATE",
                    "split_leakage_within_group": len({m.get("split", "") for m in members}) > 1,
                    "reason": "Exact byte duplicate; retain one deterministic path, preserve its original split, exclude extra rows from candidate set."
                })

    conflict_group_for_path = {}
    conflict_report = []
    for digest in sorted(conflict_hashes):
        members = by_hash[digest]
        group_id = f"CONFLICT-{digest[:16]}"
        for m in members:
            conflict_group_for_path[m["relative_image_path"]] = group_id
            conflict_report.append({
                "conflict_group_id": group_id, "vegetable_category": m["normalized_category"],
                "original_category": m.get("original_category", ""),
                "original_label": m["normalized_condition"],
                "sha256": digest, "image_path": m["relative_image_path"],
                "source_name": m.get("source_name", ""), "source_identifier": m.get("source_identifier", ""),
                "original_split": m.get("split", ""),
                "known_phase8_conflict": digest in known_phase8_hashes,
                "group_categories": "|".join(sorted({x["normalized_category"] for x in members})),
                "group_labels": "|".join(sorted({x["normalized_condition"] for x in members})),
                "row_status": "EXCLUDED_CONFLICT",
                "reason": "Exclude every row for this exact-image group; conflicting labels/category cannot be resolved automatically."
            })

    # Primary status precedence keeps all exclusion/flag types visible; separate columns retain overlap signals.
    candidate_rows=[]
    for rec in records:
        path=rec["relative_image_path"]; digest=rec["actual_sha256"]
        qflags=rec["quality_flags"]
        if digest in conflict_hashes:
            status="EXCLUDED_CONFLICT"
            reason="Every row in exact-image group excluded because labels or categories conflict."
        elif path in duplicate_extras:
            status="EXCLUDED_DUPLICATE"
            reason="Same-label exact duplicate extra row; canonical row retained in its original split."
        elif qflags:
            status="FLAGGED_QUALITY"
            reason="Deterministic image-quality check flagged: " + ";".join(qflags)
        else:
            status="FLAGGED_PROVENANCE"
            reason="Per-image original source/rights not verified; Mendeley record license does not clear every aggregated image."
        candidate_rows.append({
            "stable_image_id": f"{rec['normalized_category']}:{digest or hashlib.sha256(path.encode()).hexdigest()}",
            "original_image_path": path, "vegetable_category": rec["normalized_category"],
            "original_category": rec.get("original_category", ""),
            "original_fresh_rotten_label": rec["normalized_condition"],
            "source_name": rec.get("source_name", ""), "source_identifier": rec.get("source_identifier", ""),
            "source_url": rec.get("source_url", ""), "recorded_license": rec.get("license", ""),
            "inventory_sha256": rec["inventory_sha256"], "recomputed_sha256": digest,
            "duplicate_group_id": conflict_group_for_path.get(path) or duplicate_group_for_path.get(path, ""),
            "original_split": rec.get("split", ""), "existing_split_field": rec.get("existing_split", ""),
            "file_exists": rec["file_exists"], "readable": rec["readable"],
            "file_bytes": rec["file_bytes"], "width": rec["width"], "height": rec["height"], "image_format": rec["format"],
            "automated_quality_status": "FLAGGED_QUALITY" if qflags else "PASS",
            "quality_flags": ";".join(qflags), "quality_metrics": rec["quality_metrics"],
            "provenance_status": "FLAGGED_PROVENANCE",
            "curation_status": status, "inclusion_exclusion_status": status,
            "exclusion_reason": reason, "inspection_error": rec["error"]
        })

    write_csv(OUT/"candidate_manifest.csv", list(candidate_rows[0].keys()), candidate_rows)
    write_csv(OUT/"duplicate_exclusion_report.csv", list(duplicate_report[0].keys()) if duplicate_report else ["duplicate_group_id"], duplicate_report)
    quality_fields=["stable_image_id","image_path","vegetable_category","original_label","sha256","file_exists","readable","file_bytes","width","height","image_format","quality_status","quality_flags","quality_metrics","inspection_error"]
    quality_rows=[{"stable_image_id":r["stable_image_id"],"image_path":r["original_image_path"],"vegetable_category":r["vegetable_category"],"original_label":r["original_fresh_rotten_label"],"sha256":r["recomputed_sha256"],"file_exists":r["file_exists"],"readable":r["readable"],"file_bytes":r["file_bytes"],"width":r["width"],"height":r["height"],"image_format":r["image_format"],"quality_status":r["automated_quality_status"],"quality_flags":r["quality_flags"],"quality_metrics":r["quality_metrics"],"inspection_error":r["inspection_error"]} for r in candidate_rows]
    write_csv(OUT/"image_quality_report.csv", quality_fields, quality_rows)
    write_csv(OUT/"conflict_exclusion_detail.csv", list(conflict_report[0].keys()) if conflict_report else ["conflict_group_id"], conflict_report)

    summary=[]
    for category in sorted(CATEGORIES):
        members=[r for r in candidate_rows if r["vegetable_category"]==category]
        fresh=sum(r["original_fresh_rotten_label"]=="fresh" for r in members)
        rotten=sum(r["original_fresh_rotten_label"]=="rotten" for r in members)
        category_groups=[m for m in by_hash.values() if any(x["normalized_category"]==category for x in m)]
        unique_count=len({r["recomputed_sha256"] for r in members if r["recomputed_sha256"]})
        category_conflicts={h for h in conflict_hashes if any(x["normalized_category"]==category for x in by_hash[h])}
        conflict_rows=sum(r["recomputed_sha256"] in category_conflicts for r in members)
        dup_excluded=sum(r["vegetable_category"]==category and r["curation_status"]=="EXCLUDED_DUPLICATE" for r in candidate_rows)
        quality_flagged=sum(r["vegetable_category"]==category and r["automated_quality_status"]=="FLAGGED_QUALITY" for r in candidate_rows)
        remaining_unique=sum(r["vegetable_category"]==category and r["curation_status"]=="FLAGGED_PROVENANCE" for r in candidate_rows)
        candidate_after_integrity=sum(r["vegetable_category"]==category and r["curation_status"] in {"INCLUDED_CANDIDATE","FLAGGED_PROVENANCE"} for r in candidate_rows)
        status_counts=Counter(r["curation_status"] for r in members)
        remaining_clean_fresh=sum(r["original_fresh_rotten_label"]=="fresh" and r["curation_status"]=="FLAGGED_PROVENANCE" for r in members)
        remaining_clean_rotten=sum(r["original_fresh_rotten_label"]=="rotten" and r["curation_status"]=="FLAGGED_PROVENANCE" for r in members)
        pre_quality_fresh=sum(r["original_fresh_rotten_label"]=="fresh" and r["curation_status"] in {"FLAGGED_PROVENANCE","FLAGGED_QUALITY"} for r in members)
        pre_quality_rotten=sum(r["original_fresh_rotten_label"]=="rotten" and r["curation_status"] in {"FLAGGED_PROVENANCE","FLAGGED_QUALITY"} for r in members)
        dup_fresh=sum(r["original_fresh_rotten_label"]=="fresh" and r["curation_status"]=="EXCLUDED_DUPLICATE" for r in members)
        dup_rotten=sum(r["original_fresh_rotten_label"]=="rotten" and r["curation_status"]=="EXCLUDED_DUPLICATE" for r in members)
        conflict_fresh=sum(r["original_fresh_rotten_label"]=="fresh" and r["curation_status"]=="EXCLUDED_CONFLICT" for r in members)
        conflict_rotten=sum(r["original_fresh_rotten_label"]=="rotten" and r["curation_status"]=="EXCLUDED_CONFLICT" for r in members)
        summary.append({
            "vegetable_category":category,"original_inventory_rows":len(members),
            "original_fresh_rows":fresh,"original_rotten_rows":rotten,
            "original_unique_image_hashes":unique_count,"augmented_images_added_in_phase9":0,
            "conflicting_hash_groups":len(category_conflicts),"conflicting_rows_excluded":conflict_rows,
            "conflicting_fresh_rows_excluded":conflict_fresh,"conflicting_rotten_rows_excluded":conflict_rotten,
            "same_label_duplicate_rows_excluded":dup_excluded,"same_label_duplicate_fresh_rows_excluded":dup_fresh,
            "same_label_duplicate_rotten_rows_excluded":dup_rotten,
            "same_label_duplicate_groups":sum(1 for (c,l,h),ms in duplicate_groups.items() if c==category and len(ms)>1),
            "quality_flagged_rows":quality_flagged,
            "quality_flagged_fresh_rows":sum(r["original_fresh_rotten_label"]=="fresh" and r["automated_quality_status"]=="FLAGGED_QUALITY" for r in members),
            "quality_flagged_rotten_rows":sum(r["original_fresh_rotten_label"]=="rotten" and r["automated_quality_status"]=="FLAGGED_QUALITY" for r in members),
            "remaining_rows_after_conflict_duplicate_exclusion":pre_quality_fresh+pre_quality_rotten,
            "remaining_fresh_after_conflict_duplicate_exclusion":pre_quality_fresh,
            "remaining_rotten_after_conflict_duplicate_exclusion":pre_quality_rotten,
            "remaining_unique_rows_after_conflict_duplicate_quality_filters":candidate_after_integrity,
            "remaining_candidate_fresh_rows_quality_clean":remaining_clean_fresh,
            "remaining_candidate_rotten_rows_quality_clean":remaining_clean_rotten,
            "remaining_rows_flagged_for_provenance":status_counts["FLAGGED_PROVENANCE"],
            "included_candidate_rows":status_counts["INCLUDED_CANDIDATE"],
            "excluded_conflict_rows":status_counts["EXCLUDED_CONFLICT"],
            "excluded_duplicate_rows":status_counts["EXCLUDED_DUPLICATE"],
            "flagged_quality_rows":status_counts["FLAGGED_QUALITY"],
            "original_fresh_rotten_ratio":f"{fresh/rotten:.3f}:1" if rotten else ("not_applicable" if not fresh else "infinite"),
            "remaining_quality_clean_fresh_rotten_ratio":f"{remaining_clean_fresh/remaining_clean_rotten:.3f}:1" if remaining_clean_rotten else ("not_applicable" if not remaining_clean_fresh else "infinite"),
            "split_assignment_source":"inventory.split; preserved on each row; no files moved",
            "provenance_status":"UNVERIFIED per-image source/rights" if members else "NO LOCAL DATA"
        })
    write_csv(OUT/"category_summary.csv", list(summary[0].keys()), summary)

    print(f"Rows={len(records)} conflicts={len(conflict_hashes)} condition_conflicts={len(condition_conflict_hashes)} category_conflicts={len(category_conflict_hashes)} conflict_rows={len(conflict_report)}")
    print(f"duplicate_groups={sum(1 for x in duplicate_groups.values() if len(x)>1)} duplicate_extra_rows={len(duplicate_extras)} quality_flag_rows={sum(bool(r['quality_flags']) for r in records)} missing_hash={missing_inventory_hash} hash_mismatches={inventory_hash_mismatches}")
    print("status_counts="+str(Counter(r["curation_status"] for r in candidate_rows)))
    for r in summary: print(r["vegetable_category"],r["original_inventory_rows"],r["original_fresh_rows"],r["original_rotten_rows"],r["conflicting_rows_excluded"],r["same_label_duplicate_rows_excluded"],r["quality_flagged_rows"],r["remaining_unique_rows_after_conflict_duplicate_quality_filters"],r["original_fresh_rotten_ratio"])
    print(f"hash_mismatches={inventory_hash_mismatches}; missing_inventory_hash={missing_inventory_hash}")

if __name__ == "__main__":
    main()
