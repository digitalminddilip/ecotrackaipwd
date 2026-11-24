"""
EcoTrack AI - Kaggle Waste Classification Model Tester
Validates `kaggle/ecotrack_waste_model.h5` and `kaggle/waste_classes.json`
"""

import os
import sys
import json
from io import BytesIO
import numpy as np
from PIL import Image

# Metadata mapping: Maps 30 Kaggle classes to Municipal Bins, EcoTrack streams, and citizen instructions
CLASS_METADATA = {
    # 1. Plastics -> Blue Bin
    "disposable_plastic_cutlery": {
        "category": "plastic", "bin": "blue_bin", "label": "Disposable Plastic Cutlery",
        "instructions": "Rinse clean and place in Blue Bin (Dry Recyclables)."
    },
    "plastic_cup_lids": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Cup Lid",
        "instructions": "Dry recyclables; place in Blue Bin."
    },
    "plastic_detergent_bottles": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Detergent Bottle",
        "instructions": "Rinse soap residues thoroughly; discard in Blue Bin."
    },
    "plastic_food_containers": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Food Container",
        "instructions": "Rinse food residues; discard in Blue Bin."
    },
    "plastic_shopping_bags": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Shopping Bag",
        "instructions": "Bundle polybags together; discard in Blue Bin or drop at plastic bank."
    },
    "plastic_soda_bottles": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Soda Bottle (PET)",
        "instructions": "Empty liquid, crush bottle, screw cap back on, put in Blue Bin."
    },
    "plastic_straws": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Straw",
        "instructions": "Blue Bin (Dry Recyclables)."
    },
    "plastic_trash_bags": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Trash Bag",
        "instructions": "Ensure clean/dry or dispose with municipal dry waste."
    },
    "plastic_water_bottles": {
        "category": "plastic", "bin": "blue_bin", "label": "Plastic Water Bottle",
        "instructions": "Crush to reduce volume, place in Blue Bin."
    },
    "styrofoam_cups": {
        "category": "plastic", "bin": "blue_bin", "label": "Styrofoam Cup",
        "instructions": "Expanded polystyrene; clean and place in Blue Bin."
    },
    "styrofoam_food_containers": {
        "category": "plastic", "bin": "blue_bin", "label": "Styrofoam Food Container",
        "instructions": "Wipe clean and discard in Blue Bin."
    },

    # 2. Metals -> Blue Bin
    "aerosol_cans": {
        "category": "metal", "bin": "blue_bin", "label": "Aerosol Spray Can",
        "instructions": "Ensure completely depressurized and empty before placing in Blue Bin."
    },
    "aluminum_food_cans": {
        "category": "metal", "bin": "blue_bin", "label": "Aluminum Food Can",
        "instructions": "Rinse food particles, place in Blue Bin."
    },
    "aluminum_soda_cans": {
        "category": "metal", "bin": "blue_bin", "label": "Aluminum Soda Can",
        "instructions": "Empty and crush; high-value recyclable for Blue Bin."
    },
    "steel_food_cans": {
        "category": "metal", "bin": "blue_bin", "label": "Steel Food Can",
        "instructions": "Rinse out contents; dispose in Blue Bin."
    },

    # 3. Glass -> Blue Bin
    "glass_beverage_bottles": {
        "category": "glass", "bin": "blue_bin", "label": "Glass Beverage Bottle",
        "instructions": "Rinse clean; place in Blue Bin or glass recycling bank."
    },
    "glass_cosmetic_containers": {
        "category": "glass", "bin": "blue_bin", "label": "Glass Cosmetic Container",
        "instructions": "Empty remaining cream/liquid; place in Blue Bin."
    },
    "glass_food_jars": {
        "category": "glass", "bin": "blue_bin", "label": "Glass Food Jar",
        "instructions": "Wash jar and metal lid; place in Blue Bin."
    },

    # 4. Paper & Cardboard -> Blue Bin
    "cardboard_boxes": {
        "category": "cardboard", "bin": "blue_bin", "label": "Cardboard Box",
        "instructions": "Flatten boxes to save space; keep dry in Blue Bin."
    },
    "cardboard_packaging": {
        "category": "cardboard", "bin": "blue_bin", "label": "Cardboard Packaging",
        "instructions": "Flatten cartons and place in Blue Bin."
    },
    "magazines": {
        "category": "paper", "bin": "blue_bin", "label": "Magazine",
        "instructions": "Recyclable dry paper; place in Blue Bin."
    },
    "newspaper": {
        "category": "paper", "bin": "blue_bin", "label": "Newspaper",
        "instructions": "Bundle dry newspapers and discard in Blue Bin."
    },
    "office_paper": {
        "category": "paper", "bin": "blue_bin", "label": "Office Paper",
        "instructions": "Recyclable dry paper; place in Blue Bin."
    },
    "paper_cups": {
        "category": "paper", "bin": "blue_bin", "label": "Paper Cup",
        "instructions": "Empty liquids completely; dispose in Blue Bin."
    },

    # 5. Biodegradable / Organic -> Green Bin
    "coffee_grounds": {
        "category": "biodegradable", "bin": "green_bin", "label": "Coffee Grounds",
        "instructions": "Organic wet waste; compost or discard in Green Bin."
    },
    "eggshells": {
        "category": "biodegradable", "bin": "green_bin", "label": "Eggshells",
        "instructions": "Organic wet waste; ideal for compost or Green Bin."
    },
    "food_waste": {
        "category": "biodegradable", "bin": "green_bin", "label": "Food Waste / Kitchen Scraps",
        "instructions": "Wet organic waste; discard directly into Green Bin."
    },
    "tea_bags": {
        "category": "biodegradable", "bin": "green_bin", "label": "Tea Bag",
        "instructions": "Organic wet waste; place in Green Bin (remove any staple)."
    },

    # 6. Textiles / Shoes -> Special Handling
    "clothing": {
        "category": "other_issue", "bin": "special_handling", "label": "Clothing / Fabric",
        "instructions": "Textile waste; donate if wearable or send to textile recycling."
    },
    "shoes": {
        "category": "other_issue", "bin": "special_handling", "label": "Footwear / Shoes",
        "instructions": "Special waste stream; donate if usable or send to shoe recycling."
    },
}

_MODEL = None
_CLASSES = None
_IDX_TO_CLASS = None


def load_waste_model(model_path: str = "kaggle/ecotrack_waste_model.h5", classes_path: str = "kaggle/waste_classes.json"):
    """Loads and caches the Keras model and class index mapping."""
    global _MODEL, _CLASSES, _IDX_TO_CLASS
    if _MODEL is not None:
        return _MODEL, _IDX_TO_CLASS

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    if not os.path.exists(classes_path):
        raise FileNotFoundError(f"Classes file not found at: {classes_path}")

    print(f"[*] Loading model from {model_path}...")
    import tensorflow as tf

    # In Keras 3 / TF, compile=False avoids optimizer mismatch during inference
    _MODEL = tf.keras.models.load_model(model_path, compile=False)

    with open(classes_path, "r", encoding="utf-8") as f:
        _CLASSES = json.load(f)

    # Invert mapping: {index: class_name}
    _IDX_TO_CLASS = {int(v): k for k, v in _CLASSES.items()}
    print(f"[+] Model loaded successfully! {len(_IDX_TO_CLASS)} classes registered.")
    return _MODEL, _IDX_TO_CLASS


def preprocess_image(image_input) -> np.ndarray:
    """
    Preprocess image for MobileNetV2:
    - Resize to 160x160 RGB
    - Scale pixel values to [-1.0, 1.0]
    """
    if isinstance(image_input, (str, os.PathLike)):
        img = Image.open(image_input)
    elif isinstance(image_input, (bytes, bytearray)):
        img = Image.open(BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    img_rgb = img.convert("RGB").resize((160, 160), Image.Resampling.BILINEAR)
    arr = np.asarray(img_rgb, dtype=np.float32)

    # MobileNetV2 normalization: (pixel / 127.5) - 1.0 -> range [-1, 1]
    norm_arr = (arr / 127.5) - 1.0

    # Expand batch dimension: (1, 160, 160, 3)
    return np.expand_dims(norm_arr, axis=0)


def classify_waste(image_input, top_k: int = 3) -> dict:
    """
    Runs inference on an image and returns top predictions with municipal disposal advice.
    """
    model, idx_to_class = load_waste_model()
    tensor = preprocess_image(image_input)

    raw_preds = model.predict(tensor, verbose=0)[0]
    
    # Softmax probabilities if not already applied
    if np.abs(np.sum(raw_preds) - 1.0) > 0.05:
        exp_preds = np.exp(raw_preds - np.max(raw_preds))
        probs = exp_preds / np.sum(exp_preds)
    else:
        probs = raw_preds

    sorted_indices = np.argsort(probs)[::-1]
    top_idx = int(sorted_indices[0])
    top_class = idx_to_class[top_idx]
    top_conf = float(probs[top_idx])

    meta = CLASS_METADATA.get(top_class, {
        "category": "mixed", "bin": "blue_bin", "label": top_class.replace("_", " ").title(),
        "instructions": "Place in appropriate recycling bin."
    })

    top_k_results = []
    for i in range(min(top_k, len(sorted_indices))):
        idx = int(sorted_indices[i])
        cls_name = idx_to_class[idx]
        cls_meta = CLASS_METADATA.get(cls_name, {})
        top_k_results.append({
            "class": cls_name,
            "label": cls_meta.get("label", cls_name.replace("_", " ").title()),
            "confidence": round(float(probs[idx]) * 100, 2),
            "bin": cls_meta.get("bin", "blue_bin")
        })

    return {
        "status": "success",
        "predicted_class": top_class,
        "label": meta["label"],
        "category": meta["category"],
        "disposal_bin": meta["bin"],
        "disposal_instructions": meta["instructions"],
        "confidence": round(top_conf * 100, 2),
        "top_predictions": top_k_results,
        "provider": "kaggle:mobilenetv2_30class"
    }


def create_sample_waste_image(filename: str = "test_sample.png") -> str:
    """Generates a simple test image if no image path is passed."""
    img = Image.new("RGB", (200, 200), color=(50, 130, 220))
    img.save(filename)
    return filename


if __name__ == "__main__":
    test_img = sys.argv[1] if len(sys.argv) > 1 else None

    if not test_img or not os.path.exists(test_img):
        # Look for existing sample image or generate one
        candidates = ["frontend/bg.jpg", "logo.png", "test_sample.png"]
        for c in candidates:
            if os.path.exists(c):
                test_img = c
                break
        if not test_img:
            test_img = create_sample_waste_image()
            print(f"Created fallback sample image: {test_img}")

    print(f"\n==========================================")
    print(f" Running Waste Classification Test on: {test_img}")
    print(f"==========================================")

    result = classify_waste(test_img)

    print("\n>>> CLASSIFICATION RESULT:")
    print(f"Item Detected        : {result['label']} ({result['predicted_class']})")
    print(f"Category             : {result['category'].upper()}")
    print(f"Disposal Bin         : {result['disposal_bin'].upper()}")
    print(f"Confidence           : {result['confidence']}%")
    print(f"Disposal Advice      : {result['disposal_instructions']}")
    print("\n>>> TOP 3 PREDICTIONS:")
    for rank, p in enumerate(result['top_predictions'], 1):
        print(f"  {rank}. {p['label']} ({p['class']}): {p['confidence']}% [{p['bin']}]")
    print("==========================================\n")
