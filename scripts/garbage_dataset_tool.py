"""
EcoTrack AI - Garbage Classification 3 Dataset Utility (v1 & v2-gc1)
Inspects, validates, and compares Garbage Classification datasets:
- v1: 17,365 images (2x augmentation)
- v2 (GC1): 10,464 images (1x augmentation)
"""

import os
import sys
import json
import re
import argparse
from collections import Counter

V1_DIR = r"c:\Users\01\Downloads\GARBAGE CLASSIFICATION 3.v1-garbage-classification.openai"
V2_DIR = r"c:\Users\01\Downloads\GARBAGE CLASSIFICATION 3.v2-gc1.openai"

CLASSES = ["BIODEGRADABLE", "CARDBOARD", "GLASS", "METAL", "PAPER", "PLASTIC"]

DISPOSAL_GUIDE = {
    "BIODEGRADABLE": {
        "bin": "Green Bin (Wet Waste)",
        "destination": "Municipal Composting & Biogas Plants",
        "examples": "Food waste, fruit peels, vegetable scraps, dry leaves"
    },
    "PLASTIC": {
        "bin": "Blue Bin (Dry Recyclable Waste)",
        "destination": "Plastic Granulation & Textile Fiber Recycling",
        "examples": "PET bottles, HDPE containers, polythene wrappers, milk pouches"
    },
    "CARDBOARD": {
        "bin": "Blue Bin (Dry Recyclable Waste)",
        "destination": "Paper Pulp & Corrugated Packaging Facilities",
        "examples": "Shipping boxes, carton packaging, egg crates"
    },
    "GLASS": {
        "bin": "Blue Bin / Dedicated Glass Crates",
        "destination": "Cullet Melting & Glass Remanufacturing",
        "examples": "Glass bottles, sauce jars, beverage containers"
    },
    "METAL": {
        "bin": "Blue Bin (Dry Recyclable Waste)",
        "destination": "Scrap Smelting & Metal Recovery",
        "examples": "Aluminum soda cans, tin cans, food foil, metal caps"
    },
    "PAPER": {
        "bin": "Blue Bin (Dry Recyclable Waste)",
        "destination": "Recycled Paper Mills",
        "examples": "Newspapers, office notebooks, shredded paper, magazines"
    }
}


def inspect_dataset(dataset_dir: str):
    if not os.path.exists(dataset_dir):
        print(f"[ERROR] Dataset directory not found: {dataset_dir}")
        return None

    folder_name = os.path.basename(dataset_dir)
    print("=" * 72)
    print(f" ECOTRACK AI - DATASET ANALYSIS: {folder_name}")
    print("=" * 72)
    print(f"Location: {dataset_dir}\n")

    splits = {
        "Train": "_annotations.train.jsonl",
        "Valid": "_annotations.valid.jsonl",
        "Test": "_annotations.test.jsonl"
    }

    stats = {
        "total_images": 0,
        "splits": {},
        "classes": Counter()
    }

    for split_name, filename in splits.items():
        file_path = os.path.join(dataset_dir, filename)
        if not os.path.exists(file_path):
            continue

        sample_count = 0
        split_classes = Counter()

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                sample_count += 1
                try:
                    data = json.loads(line)
                    for msg in data.get("messages", []):
                        if msg.get("role") == "assistant":
                            content = msg.get("content", "")
                            labels = re.findall(r">\s*([A-Z_]+)", content)
                            for lbl in labels:
                                split_classes[lbl] += 1
                                stats["classes"][lbl] += 1
                except Exception:
                    pass

        stats["total_images"] += sample_count
        stats["splits"][split_name] = {"count": sample_count, "classes": split_classes}

        print(f"[{split_name} Split]")
        print(f"  • Total Images: {sample_count:,}")
        for cls, count in split_classes.most_common():
            print(f"    - {cls:15}: {count:6,} occurrences")
        print()

    print("-" * 72)
    print(f"Total Dataset Images: {stats['total_images']:,}")
    total_objects = sum(stats["classes"].values())
    print(f"Total Annotated Objects across all splits: {total_objects:,}\n")

    for cls, count in stats["classes"].most_common():
        pct = (count / total_objects * 100) if total_objects else 0
        guide = DISPOSAL_GUIDE.get(cls, {})
        bin_name = guide.get("bin", "General")
        print(f"  • {cls:15}: {count:6,} ({pct:5.1f}%) -> Bin: {bin_name}")

    print("=" * 72 + "\n")
    return stats


def compare_datasets():
    print("=" * 72)
    print(" ECOTRACK AI - COMPARING DATASET V1 VS V2 (GC1)")
    print("=" * 72)

    s1 = inspect_dataset(V1_DIR)
    s2 = inspect_dataset(V2_DIR)

    if s1 and s2:
        print("=" * 72)
        print(" COMPARISON SUMMARY (V1 vs V2-GC1)")
        print("=" * 72)
        print(f"{'Metric':<30} | {'v1 (2x Augmented)':<18} | {'v2-gc1 (1x Clean)':<18}")
        print("-" * 72)
        print(f"{'Total Images':<30} | {s1['total_images']:<18,d} | {s2['total_images']:<18,d}")
        print(f"{'Train Split Images':<30} | {s1['splits'].get('Train', {}).get('count', 0):<18,d} | {s2['splits'].get('Train', {}).get('count', 0):<18,d}")
        print(f"{'Valid Split Images':<30} | {s1['splits'].get('Valid', {}).get('count', 0):<18,d} | {s2['splits'].get('Valid', {}).get('count', 0):<18,d}")
        print(f"{'Test Split Images':<30} | {s1['splits'].get('Test', {}).get('count', 0):<18,d} | {s2['splits'].get('Test', {}).get('count', 0):<18,d}")
        print(f"{'Total Object Annotations':<30} | {sum(s1['classes'].values()):<18,d} | {sum(s2['classes'].values()):<18,d}")
        print("-" * 72)
        print("Key Differences:")
        print("• v2-gc1 has 1x augmentation (less overfitting risk, 50% faster training).")
        print("• v1 has 2x augmentation (higher volume for deep networks needing heavier augmentation).")
        print("• Both share the exact same 6 material streams and test/validation splits.")
        print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Inspect Garbage Classification 3 Dataset")
    parser.add_argument("--v1", action="store_true", help="Inspect v1 dataset")
    parser.add_argument("--v2", action="store_true", help="Inspect v2-gc1 dataset")
    parser.add_argument("--compare", action="store_true", help="Compare v1 and v2 side by side")
    parser.add_argument("--path", type=str, help="Custom dataset path", default=None)

    args = parser.parse_args()

    if args.compare:
        compare_datasets()
    elif args.v1:
        inspect_dataset(V1_DIR)
    elif args.v2:
        inspect_dataset(V2_DIR)
    elif args.path:
        inspect_dataset(args.path)
    else:
        # Default: inspect v2-gc1
        inspect_dataset(V2_DIR)


if __name__ == "__main__":
    main()
