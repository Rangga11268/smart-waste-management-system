"""
Dataset Download & Curation Script for Smart Waste Management System (SWMS)

This script automates downloading, extracting, validating, and partitioning
the 12-Class Garbage Classification dataset (Mostafa Abla) into three target classes:
  - organic (mapped from biological)
  - plastic (mapped from plastic)
  - paper   (mapped from paper)

Partition: 80% train / 20% validation (deterministic split using seed 42).
"""

import argparse
import io
import os
import random
import shutil
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from PIL import Image

DATASET_URL = (
    "https://huggingface.co/datasets/UdaraChamidu/"
    "Garbage-Classification-with-12-classes/resolve/main/garbage_classification.zip"
)

CLASS_MAPPING = {
    "biological": "organic",
    "plastic": "plastic",
    "paper": "paper",
}


def download_file(url: str, dest_path: Path, chunk_size: int = 1024 * 1024) -> None:
    """Download a file with progress reporting."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")

    print(f"Connecting to {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()

    with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, "wb") as f:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        last_print = t0

        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)

            now = time.time()
            if now - last_print >= 3.0:
                last_print = now
                pct = (downloaded / total) * 100 if total else 0.0
                mb = downloaded / (1024 * 1024)
                speed = mb / (now - t0 + 1e-6)
                print(f"  [Download] {pct:5.1f}% ({mb:6.1f} MB) - {speed:4.2f} MB/s")

    elapsed = time.time() - t0
    final_mb = downloaded / (1024 * 1024)
    print(f"Download complete: {final_mb:.1f} MB in {elapsed:.1f}s ({final_mb / (elapsed + 1e-6):.2f} MB/s)")

    if dest_path.exists():
        dest_path.unlink()
    temp_path.rename(dest_path)


def validate_image_data(image_bytes: bytes) -> Image.Image:
    """Validate image bytes using Pillow, verifying format and converting to RGB."""
    # First verify integrity
    bio = io.BytesIO(image_bytes)
    with Image.open(bio) as img:
        img.verify()

    # Re-open for actual processing (verify closes/invalidates the file pointer)
    bio.seek(0)
    with Image.open(bio) as img:
        img_rgb = img.convert("RGB")
        return img_rgb


def curate_dataset(
    zip_source: Path,
    output_dir: Path,
    num_per_class: int = 70,
    train_ratio: float = 0.8,
    seed: int = 42,
    force: bool = False,
) -> dict:
    """Extract, validate, and partition images from zip archive into train/val structure."""
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"

    target_classes = list(CLASS_MAPPING.values())

    # Check if already curated
    if not force:
        already_curated = True
        counts = {"train": {}, "val": {}}
        for target_cls in target_classes:
            t_imgs = list((train_dir / target_cls).glob("*.jpg")) if (train_dir / target_cls).exists() else []
            v_imgs = list((val_dir / target_cls).glob("*.jpg")) if (val_dir / target_cls).exists() else []
            counts["train"][target_cls] = len(t_imgs)
            counts["val"][target_cls] = len(v_imgs)
            if len(t_imgs) < int(num_per_class * train_ratio) or len(v_imgs) < int(num_per_class * (1 - train_ratio)):
                already_curated = False
                break

        if already_curated:
            print("Dataset already curated and complete on disk:")
            for target_cls in target_classes:
                print(f"  {target_cls}: {counts['train'][target_cls]} train, {counts['val'][target_cls]} val")
            return counts

    print(f"Opening zip archive: {zip_source} ...")
    with zipfile.ZipFile(zip_source, "r") as zf:
        all_entries = zf.namelist()

        rng = random.Random(seed)
        curated_counts = {"train": {}, "val": {}}

        train_count_per_cls = int(round(num_per_class * train_ratio))
        val_count_per_cls = num_per_class - train_count_per_cls

        for src_cls, target_cls in CLASS_MAPPING.items():
            prefix = f"garbage_classification/{src_cls}/"
            matching_files = [
                n for n in all_entries
                if n.startswith(prefix) and n.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            matching_files.sort()  # Deterministic base order

            if len(matching_files) < num_per_class:
                raise ValueError(
                    f"Not enough images for class '{src_cls}': found {len(matching_files)}, needed {num_per_class}"
                )

            # Deterministic shuffle
            shuffled = list(matching_files)
            rng.shuffle(shuffled)
            selected = shuffled[:num_per_class]

            train_files = selected[:train_count_per_cls]
            val_files = selected[train_count_per_cls:]

            out_train_cls = train_dir / target_cls
            out_val_cls = val_dir / target_cls
            out_train_cls.mkdir(parents=True, exist_ok=True)
            out_val_cls.mkdir(parents=True, exist_ok=True)

            # Process train images
            for idx, file_name in enumerate(train_files, start=1):
                raw_bytes = zf.read(file_name)
                img = validate_image_data(raw_bytes)
                out_path = out_train_cls / f"{target_cls}_{idx:03d}.jpg"
                img.save(out_path, format="JPEG", quality=95)

            # Process val images
            for idx, file_name in enumerate(val_files, start=1):
                raw_bytes = zf.read(file_name)
                img = validate_image_data(raw_bytes)
                out_path = out_val_cls / f"{target_cls}_{idx:03d}.jpg"
                img.save(out_path, format="JPEG", quality=95)

            curated_counts["train"][target_cls] = len(train_files)
            curated_counts["val"][target_cls] = len(val_files)
            print(
                f"  Extracted '{target_cls}': {len(train_files)} train, "
                f"{len(val_files)} val (total: {len(selected)})"
            )

    return curated_counts


def verify_dataset(output_dir: Path) -> bool:
    """Verify all images in dataset are non-empty, valid RGB images."""
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"

    all_valid = True
    total_checked = 0

    for split_dir, split_name in [(train_dir, "train"), (val_dir, "val")]:
        for cls_name in ["organic", "plastic", "paper"]:
            cls_dir = split_dir / cls_name
            if not cls_dir.exists():
                print(f"ERROR: Missing directory {cls_dir}")
                all_valid = False
                continue

            images = list(cls_dir.glob("*.jpg"))
            if not images:
                print(f"ERROR: No images found in {cls_dir}")
                all_valid = False
                continue

            for img_path in images:
                total_checked += 1
                if img_path.stat().st_size == 0:
                    print(f"ERROR: Zero-byte file: {img_path}")
                    all_valid = False
                    continue

                try:
                    with Image.open(img_path) as img:
                        img.verify()
                    with Image.open(img_path) as img:
                        if img.mode != "RGB":
                            print(f"WARNING: Image {img_path} mode is {img.mode}, expected RGB")
                except Exception as exc:
                    print(f"ERROR: Corrupted image {img_path}: {exc}")
                    all_valid = False

    print(f"Verification complete: checked {total_checked} images across all classes. Status: {'OK' if all_valid else 'FAILED'}")
    return all_valid


def main():
    parser = argparse.ArgumentParser(description="Download and curate waste classification dataset.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "dataset",
        help="Directory where train/ and val/ datasets should be stored.",
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=None,
        help="Optional local path to garbage_classification.zip archive.",
    )
    parser.add_argument(
        "--num-per-class",
        type=int,
        default=70,
        help="Number of images to curate per category (default: 70).",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Proportion of images allocated to training split (default: 0.8).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic sampling (default: 42).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-extraction even if dataset already exists.",
    )
    parser.add_argument(
        "--clean-zip",
        action="store_true",
        help="Remove downloaded zip archive after extraction to save disk space.",
    )

    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if dataset is already complete on disk
    if not args.force:
        target_classes = ["organic", "plastic", "paper"]
        train_req = int(round(args.num_per_class * args.train_ratio))
        val_req = args.num_per_class - train_req
        already_curated = True
        counts = {"train": {}, "val": {}}
        for target_cls in target_classes:
            t_imgs = list((output_dir / "train" / target_cls).glob("*.jpg")) if (output_dir / "train" / target_cls).exists() else []
            v_imgs = list((output_dir / "val" / target_cls).glob("*.jpg")) if (output_dir / "val" / target_cls).exists() else []
            counts["train"][target_cls] = len(t_imgs)
            counts["val"][target_cls] = len(v_imgs)
            if len(t_imgs) < train_req or len(v_imgs) < val_req:
                already_curated = False
                break

        if already_curated:
            print("Dataset already curated and complete on disk:")
            for target_cls in target_classes:
                print(f"  {target_cls}: {counts['train'][target_cls]} train, {counts['val'][target_cls]} val")
            verified = verify_dataset(output_dir)
            if verified:
                print("\nDataset verified and ready for model training!")
                return
            else:
                print("Dataset verification failed. Re-curating...")

    zip_path = args.zip_path
    if zip_path is None:
        zip_path = output_dir / "garbage_classification.zip"

    # If zip doesn't exist, download it
    if not zip_path.exists():
        download_file(DATASET_URL, zip_path)
    else:
        print(f"Using existing zip archive: {zip_path} ({zip_path.stat().st_size / (1024 * 1024):.1f} MB)")

    # Curate dataset
    counts = curate_dataset(
        zip_source=zip_path,
        output_dir=output_dir,
        num_per_class=args.num_per_class,
        train_ratio=args.train_ratio,
        seed=args.seed,
        force=args.force,
    )

    # Verify integrity
    verified = verify_dataset(output_dir)
    if not verified:
        sys.exit(1)

    # Clean zip if requested
    if args.clean_zip and zip_path.exists():
        print(f"Removing archive {zip_path} ...")
        zip_path.unlink()

    print("\nDataset successfully curated and ready for model training!")


if __name__ == "__main__":
    main()
