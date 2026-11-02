#!/usr/bin/env python3
"""Read-only Phase 10 archive/image validation and exact/near-duplicate scan.

Scans only ml-service/datasets/external_staging/phase10/. It never downloads,
extracts, moves, deletes, or edits image files. Pillow is required. If no external
images are staged, reports that image-level checks were not run.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageStat

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[4]
DEFAULT_STAGE = ROOT / "ml-service/datasets/external_staging/phase10"
DEFAULT_INVENTORY = ROOT / "ml-service/datasets/expansion_15/dataset_inventory.csv"
DEFAULT_REPORTS = ROOT / "ml-service/evaluation/phase10_external_acquisition"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".7z"}


def write_csv(path: Path, fields: list[str], records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(records)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dhash(path: Path) -> int:
    with Image.open(path) as im:
        im = im.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
        px = list(im.getdata())
    result = 0
    for y in range(8):
        for x in range(8):
            result = (result << 1) | int(px[y * 9 + x] > px[y * 9 + x + 1])
    return result


def bands(value: int):
    # Five bit bands guarantee at least one exact band for any 64-bit hashes
    # at Hamming distance <=4 (pigeonhole principle).
    sizes = [13, 13, 13, 13, 12]
    shift = 64
    for size in sizes:
        shift -= size
        yield (size, (value >> shift) & ((1 << size) - 1))


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def inspect(path: Path):
    info = {"exists": path.is_file(), "sha256": "", "dhash": "", "width": "", "height": "", "format": "", "bytes": 0, "readable": False, "quality_flags": [], "error": ""}
    if not path.is_file():
        info["error"] = "missing_file"; return info
    info["bytes"] = path.stat().st_size
    info["sha256"] = sha256(path)
    try:
        with Image.open(path) as im: im.verify()
        with Image.open(path) as im:
            im.load(); info["width"], info["height"] = im.size; info["format"] = im.format or ""
            gray = im.convert("L").resize((64, 64), Image.Resampling.BILINEAR)
            stddev = ImageStat.Stat(gray).stddev[0]; lo, hi = gray.getextrema()
        info["dhash"] = f"{dhash(path):016x}"; info["readable"] = True
        flags=[]
        if info["bytes"] < 1024: flags.append("small_file_under_1KiB")
        if min(info["width"], info["height"]) < 64: flags.append("small_dimensions_under_64px")
        if max(info["width"], info["height"]) / max(1, min(info["width"], info["height"])) > 5: flags.append("extreme_aspect_ratio_over_5")
        if stddev < 5 and hi-lo < 15: flags.append("near_uniform_low_contrast_thumbnail")
        info["quality_flags"] = flags
    except Exception as exc:
        info["error"] = f"decode_error:{type(exc).__name__}:{str(exc)[:160]}"
        info["quality_flags"] = ["unreadable_image"]
    return info


def read_local_inventory(path: Path):
    if not path.is_file(): return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--staging-root", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--local-inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    args=parser.parse_args()
    stage=args.staging_root.resolve(); reports=args.reports_dir.resolve()
    archives=sorted(p for p in (stage/"archives").rglob("*") if p.is_file() and p.suffix.lower() in ARCHIVE_SUFFIXES) if (stage/"archives").exists() else []
    images=sorted(p for p in (stage/"extracted").rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES) if (stage/"extracted").exists() else []
    archive_rows=[{"archive_path":str(p.relative_to(stage)),"size_bytes":p.stat().st_size,"sha256":sha256(p),"checksum_status":"CALCULATED"} for p in archives]
    write_csv(reports/"archive_checksum_report.csv",["archive_path","size_bytes","sha256","checksum_status"],archive_rows or [{"archive_path":"","size_bytes":"","sha256":"","checksum_status":"NO_ARCHIVES_FOUND"}])
    external=[]
    for path in images:
        info=inspect(path)
        external.append({"path":str(path.relative_to(stage)),"sha256":info["sha256"],"perceptual_hash_dhash64":info["dhash"],"width":info["width"],"height":info["height"],"format":info["format"],"file_bytes":info["bytes"],"readable":info["readable"],"quality_flags":";".join(info["quality_flags"]),"error":info["error"]})
    write_csv(reports/"image_integrity_report.csv",["path","sha256","perceptual_hash_dhash64","width","height","format","file_bytes","readable","quality_flags","error"],external or [{"path":"","sha256":"","perceptual_hash_dhash64":"","width":"","height":"","format":"","file_bytes":"","readable":"","quality_flags":"","error":"NOT RUN — no external images staged"}])

    pairs=[]
    if external:
        # Exact duplicates among staged images.
        by_sha=defaultdict(list)
        for row in external:
            if row["sha256"]: by_sha[row["sha256"]].append(row["path"])
        for digest, paths in by_sha.items():
            if len(paths)>1:
                for a,b in itertools.combinations(paths,2): pairs.append({"comparison":"external_external","path_a":a,"path_b":b,"sha256_a":digest,"sha256_b":digest,"dhash_distance":0,"status":"EXACT_DUPLICATE"})
        # Compare to existing local inventory; no source files are altered.
        local_rows=read_local_inventory(args.local_inventory)
        exact_local=defaultdict(list)
        for row in local_rows:
            if row.get("sha256"): exact_local[row["sha256"].lower()].append(row.get("relative_image_path",""))
        for ext in external:
            for local_path in exact_local.get(ext["sha256"],[]):
                pairs.append({"comparison":"external_local","path_a":ext["path"],"path_b":local_path,"sha256_a":ext["sha256"],"sha256_b":ext["sha256"],"dhash_distance":0,"status":"EXACT_LOCAL_OVERLAP"})
        # Perceptual cross-check: compute dHash for local readable paths only once.
        local_hashes=[]
        for row in local_rows:
            lp=ROOT/row.get("relative_image_path","")
            if lp.is_file():
                try: local_hashes.append((dhash(lp),row.get("relative_image_path","")))
                except Exception: pass
        bucket=defaultdict(list)
        for value,path in local_hashes:
            for key in bands(value): bucket[key].append((value,path))
        seen=set()
        for ext in external:
            if not ext["perceptual_hash_dhash64"]: continue
            value=int(ext["perceptual_hash_dhash64"],16); candidates={x for key in bands(value) for x in bucket.get(key,[])}
            for other,path in candidates:
                distance=hamming(value,other)
                if 1<=distance<=4:
                    key=(ext["path"],path)
                    if key not in seen:
                        seen.add(key); pairs.append({"comparison":"external_local","path_a":ext["path"],"path_b":path,"sha256_a":ext["sha256"],"sha256_b":"","dhash_distance":distance,"status":"NEAR_DUPLICATE_CANDIDATE — VISUAL REVIEW REQUIRED"})
    write_csv(reports/"duplicate_and_overlap_report.csv",["comparison","path_a","path_b","sha256_a","sha256_b","dhash_distance","status"],pairs or [{"comparison":"NONE","status":"NOT RUN — no external images staged; metadata overlap risks are in the report"}])
    print(f"Archives checked: {len(archives)}; staged images checked: {len(images)}; overlap rows: {len(pairs)}")

if __name__=="__main__": main()
