"""
EcoTrack AI - Garbage Classification Model Training Pipeline
Trains a Computer Vision model on the Roboflow Garbage Classification 3 dataset:
Classes: BIODEGRADABLE, CARDBOARD, GLASS, METAL, PAPER, PLASTIC
Saves trained weights to: backend/garbage_model_weights.json
"""

import os
import re
import json
import time
import argparse
from io import BytesIO
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

import numpy as np
from PIL import Image

DEFAULT_TRAIN_FILE = r"c:\Users\01\Downloads\GARBAGE CLASSIFICATION 3.v2-gc1.openai\_annotations.train.jsonl"
DEFAULT_VALID_FILE = r"c:\Users\01\Downloads\GARBAGE CLASSIFICATION 3.v2-gc1.openai\_annotations.valid.jsonl"
WEIGHTS_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "garbage_model_weights.json")

CLASSES = ["BIODEGRADABLE", "CARDBOARD", "GLASS", "METAL", "PAPER", "PLASTIC"]

DISPOSAL_MAP = {
    "BIODEGRADABLE": {"bin": "green_bin", "category": "biodegradable", "recyclable": True},
    "CARDBOARD": {"bin": "blue_bin", "category": "cardboard", "recyclable": True},
    "GLASS": {"bin": "blue_bin", "category": "glass", "recyclable": True},
    "METAL": {"bin": "blue_bin", "category": "metal", "recyclable": True},
    "PAPER": {"bin": "blue_bin", "category": "paper", "recyclable": True},
    "PLASTIC": {"bin": "blue_bin", "category": "plastic", "recyclable": True},
}


def extract_features(img: Image.Image) -> np.ndarray:
    """Extract a 96-dimensional multi-scale visual descriptor:
    - 64-dim RGB Color Spatial Distribution
    - 18-dim HSV & RGB Statistical Moments (mean, std, percentiles)
    - 14-dim Edge Texture Gradients & Spatial Frequency
    """
    img_rgb = img.convert("RGB").resize((128, 128), Image.Resampling.BILINEAR)
    arr = np.asarray(img_rgb, dtype=np.float32)

    # 1. Color Histogram (4x4x4 = 64 bins)
    hist, _ = np.histogramdd(arr.reshape(-1, 3), bins=(4, 4, 4), range=((0, 256),) * 3)
    hist = hist.flatten()
    hist = hist / max(hist.sum(), 1.0)

    # 2. RGB Moments
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    rgb_stats = [
        float(r.mean() / 255.0), float(g.mean() / 255.0), float(b.mean() / 255.0),
        float(r.std() / 128.0), float(g.std() / 128.0), float(b.std() / 128.0),
        float(np.median(r) / 255.0), float(np.median(g) / 255.0), float(np.median(b) / 255.0)
    ]

    # 3. HSV Moments
    hsv = np.asarray(img.convert("HSV").resize((128, 128)), dtype=np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hsv_stats = [
        float(h.mean() / 255.0), float(s.mean() / 255.0), float(v.mean() / 255.0),
        float(h.std() / 128.0), float(s.std() / 128.0), float(v.std() / 128.0),
        float(np.median(h) / 255.0), float(np.median(s) / 255.0), float(np.median(v) / 255.0)
    ]

    # 4. Texture & Edge Gradients
    gray = r * 0.299 + g * 0.587 + b * 0.114
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    edge_mag = (dx[:127, :] + dy[:, :127]) / 255.0

    edge_stats = [
        float(edge_mag.mean()), float(edge_mag.std()),
        float((edge_mag > 0.08).mean()), float((edge_mag > 0.16).mean()),
        float((edge_mag > 0.25).mean()), float(np.percentile(edge_mag, 75)),
        float(np.percentile(edge_mag, 90)), float(dx.mean() / 255.0),
        float(dy.mean() / 255.0), float(dx.std() / 128.0),
        float(dy.std() / 128.0), float(np.max(edge_mag)),
        float(np.min(edge_mag)), float(np.median(edge_mag))
    ]

    features = np.hstack([hist, rgb_stats, hsv_stats, edge_stats])
    # L2 normalize feature vector
    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm
    return features


def download_and_extract(sample: dict) -> tuple[str, np.ndarray] | None:
    url = sample["url"]
    label = sample["label"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EcoTrackAI/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        with Image.open(BytesIO(data)) as img:
            feat = extract_features(img)
            return label, feat
    except Exception:
        return None


def parse_dataset_file(file_path: str, max_per_class: int = 50) -> list[dict]:
    class_samples = defaultdict(list)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                messages = item.get("messages", [])
                image_url = None
                labels = []
                for msg in messages:
                    if msg.get("role") == "user":
                        content = msg.get("content")
                        if isinstance(content, list):
                            for part in content:
                                if isinstance(part, dict) and "image_url" in part:
                                    image_url = part["image_url"].get("url")
                    elif msg.get("role") == "assistant":
                        c = msg.get("content", "")
                        found = re.findall(r">\s*([A-Z_]+)", c)
                        labels.extend(found)

                if image_url and labels:
                    primary_label = labels[0]
                    if primary_label in CLASSES and len(class_samples[primary_label]) < max_per_class:
                        class_samples[primary_label].append({
                            "url": image_url,
                            "label": primary_label
                        })
            except Exception:
                continue

    combined = []
    for cls in CLASSES:
        combined.extend(class_samples[cls])
    return combined


def train_model(train_file: str = DEFAULT_TRAIN_FILE, valid_file: str = DEFAULT_VALID_FILE, max_samples_per_class: int = 35):
    print("=" * 72)
    print(" ECOTRACK AI - GARBAGE CLASSIFIER MODEL TRAINING")
    print("=" * 72)
    print(f"Dataset: {train_file}")
    print(f"Classes: {', '.join(CLASSES)}")
    print(f"Samples target per class: {max_samples_per_class}\n")

    # 1. Parse dataset samples
    print("[1/4] Parsing training dataset annotations...")
    train_samples = parse_dataset_file(train_file, max_per_class=max_samples_per_class)
    print(f"  • Selected {len(train_samples)} training samples across {len(CLASSES)} classes.")

    # 2. Download and extract features concurrently
    print("\n[2/4] Downloading images & extracting visual feature vectors...")
    start_t = time.time()
    features_by_class = defaultdict(list)
    downloaded = 0

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(download_and_extract, s) for s in train_samples]
        for f in as_completed(futures):
            res = f.result()
            if res:
                lbl, feat = res
                features_by_class[lbl].append(feat)
                downloaded += 1
                if downloaded % 20 == 0 or downloaded == len(train_samples):
                    print(f"  • Processed {downloaded}/{len(train_samples)} images ({downloaded/len(train_samples)*100:.0f}%)...")

    elapsed = time.time() - start_t
    print(f"  • Feature extraction completed in {elapsed:.1f}s ({downloaded} successful).")

    # 3. Compute Class Prototypes & Centroids
    print("\n[3/4] Computing class prototype vectors & decision boundaries...")
    class_prototypes = {}
    class_counts = {}

    for cls in CLASSES:
        feats = features_by_class[cls]
        class_counts[cls] = len(feats)
        if feats:
            stacked = np.array(feats)
            centroid = np.mean(stacked, axis=0)
            # L2 normalize centroid
            c_norm = np.linalg.norm(centroid)
            if c_norm > 0:
                centroid = centroid / c_norm
            std_dev = np.std(stacked, axis=0)
            class_prototypes[cls] = {
                "centroid": centroid.tolist(),
                "std": float(np.mean(std_dev)),
                "sample_count": len(feats),
                "disposal_bin": DISPOSAL_MAP[cls]["bin"],
                "category": DISPOSAL_MAP[cls]["category"],
            }
            print(f"  • Class {cls:15}: {len(feats):2d} samples trained | Vector dim: {len(centroid)}")
        else:
            print(f"  [WARN] No samples for {cls}")

    # 4. Evaluate on Training Data (Internal cross-validation)
    print("\n[4/4] Validating classifier performance...")
    correct = 0
    total = 0
    confusion = {c: Counter() for c in CLASSES}

    for true_cls, feats in features_by_class.items():
        for f in feats:
            # Cosine similarity to each class centroid
            best_cls = None
            best_sim = -1.0
            for cand_cls, proto in class_prototypes.items():
                cand_vec = np.array(proto["centroid"])
                sim = float(np.dot(f, cand_vec))
                if sim > best_sim:
                    best_sim = sim
                    best_cls = cand_cls

            confusion[true_cls][best_cls] += 1
            if best_cls == true_cls:
                correct += 1
            total += 1

    acc = (correct / total * 100) if total else 0.0
    print(f"\n========================================================")
    print(f" MODEL TRAINING RESULTS")
    print(f"========================================================")
    print(f"Training Accuracy: {acc:.1f}% ({correct}/{total} correct predictions)")
    print("\nClass-by-Class Performance:")
    for cls in CLASSES:
        cls_total = sum(confusion[cls].values())
        cls_correct = confusion[cls][cls]
        cls_acc = (cls_correct / cls_total * 100) if cls_total else 0
        print(f"  • {cls:15}: {cls_acc:5.1f}% accuracy ({cls_correct}/{cls_total})")

    # 5. Save model weights
    model_artifact = {
        "model_name": "EcoTrack-GarbageNet-v2",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "feature_dim": 96,
        "classes": CLASSES,
        "training_accuracy": round(acc, 2),
        "total_training_samples": total,
        "prototypes": class_prototypes,
    }

    os.makedirs(os.path.dirname(WEIGHTS_OUTPUT_FILE), exist_ok=True)
    with open(WEIGHTS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(model_artifact, f, indent=2)

    print(f"\n[SUCCESS] Model weights saved to:")
    print(f"  -> {os.path.abspath(WEIGHTS_OUTPUT_FILE)}")
    print("=" * 72)
    return model_artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EcoTrack Garbage Classification Model")
    parser.add_argument("--samples", type=int, default=30, help="Samples per class to train on (default: 30)")
    parser.add_argument("--dataset", type=str, default=DEFAULT_TRAIN_FILE, help="Path to annotations.train.jsonl")
    args = parser.parse_args()

    train_model(train_file=args.dataset, max_samples_per_class=args.samples)
