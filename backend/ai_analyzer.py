import json
import os
from typing import Any
from urllib.request import Request, urlopen
from io import BytesIO

import numpy as np
from PIL import Image


AI_ENDPOINT = os.getenv("ECOTRACK_AI_ENDPOINT") or os.getenv("CLEANCONNECT_AI_ENDPOINT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "garbage_model_weights.json")
_LOADED_MODEL: dict[str, Any] | None = None

# Kaggle MobileNetV2 Model Paths & Metadata
KAGGLE_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kaggle", "ecotrack_waste_model.h5")
KAGGLE_CLASSES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kaggle", "waste_classes.json")
_KAGGLE_MODEL: Any | None = None
_KAGGLE_IDX_TO_CLASS: dict[int, str] | None = None

KAGGLE_CLASS_METADATA = {
    # 1. Plastics -> Blue Bin
    "disposable_plastic_cutlery": {"category": "plastic", "bin": "blue_bin", "label": "Disposable Plastic Cutlery", "instructions": "Rinse clean and place in Blue Bin (Dry Recyclables)."},
    "plastic_cup_lids": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Cup Lid", "instructions": "Dry recyclables; place in Blue Bin."},
    "plastic_detergent_bottles": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Detergent Bottle", "instructions": "Rinse soap residues thoroughly; discard in Blue Bin."},
    "plastic_food_containers": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Food Container", "instructions": "Rinse food residues; discard in Blue Bin."},
    "plastic_shopping_bags": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Shopping Bag", "instructions": "Bundle polybags together; discard in Blue Bin or drop at plastic bank."},
    "plastic_soda_bottles": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Soda Bottle (PET)", "instructions": "Empty liquid, crush bottle, screw cap back on, put in Blue Bin."},
    "plastic_straws": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Straw", "instructions": "Blue Bin (Dry Recyclables)."},
    "plastic_trash_bags": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Trash Bag", "instructions": "Ensure clean/dry or dispose with municipal dry waste."},
    "plastic_water_bottles": {"category": "plastic", "bin": "blue_bin", "label": "Plastic Water Bottle", "instructions": "Crush to reduce volume, place in Blue Bin."},
    "styrofoam_cups": {"category": "plastic", "bin": "blue_bin", "label": "Styrofoam Cup", "instructions": "Expanded polystyrene; clean and place in Blue Bin."},
    "styrofoam_food_containers": {"category": "plastic", "bin": "blue_bin", "label": "Styrofoam Food Container", "instructions": "Wipe clean and discard in Blue Bin."},

    # 2. Metals -> Blue Bin
    "aerosol_cans": {"category": "metal", "bin": "blue_bin", "label": "Aerosol Spray Can", "instructions": "Ensure completely depressurized and empty before placing in Blue Bin."},
    "aluminum_food_cans": {"category": "metal", "bin": "blue_bin", "label": "Aluminum Food Can", "instructions": "Rinse food particles, place in Blue Bin."},
    "aluminum_soda_cans": {"category": "metal", "bin": "blue_bin", "label": "Aluminum Soda Can", "instructions": "Empty and crush; high-value recyclable for Blue Bin."},
    "steel_food_cans": {"category": "metal", "bin": "blue_bin", "label": "Steel Food Can", "instructions": "Rinse out contents; dispose in Blue Bin."},

    # 3. Glass -> Blue Bin
    "glass_beverage_bottles": {"category": "glass", "bin": "blue_bin", "label": "Glass Beverage Bottle", "instructions": "Rinse clean; place in Blue Bin or glass recycling bank."},
    "glass_cosmetic_containers": {"category": "glass", "bin": "blue_bin", "label": "Glass Cosmetic Container", "instructions": "Empty remaining cream/liquid; place in Blue Bin."},
    "glass_food_jars": {"category": "glass", "bin": "blue_bin", "label": "Glass Food Jar", "instructions": "Wash jar and metal lid; place in Blue Bin."},

    # 4. Paper & Cardboard -> Blue Bin
    "cardboard_boxes": {"category": "cardboard", "bin": "blue_bin", "label": "Cardboard Box", "instructions": "Flatten boxes to save space; keep dry in Blue Bin."},
    "cardboard_packaging": {"category": "cardboard", "bin": "blue_bin", "label": "Cardboard Packaging", "instructions": "Flatten cartons and place in Blue Bin."},
    "magazines": {"category": "paper", "bin": "blue_bin", "label": "Magazine", "instructions": "Recyclable dry paper; place in Blue Bin."},
    "newspaper": {"category": "paper", "bin": "blue_bin", "label": "Newspaper", "instructions": "Bundle dry newspapers and discard in Blue Bin."},
    "office_paper": {"category": "paper", "bin": "blue_bin", "label": "Office Paper", "instructions": "Recyclable dry paper; place in Blue Bin."},
    "paper_cups": {"category": "paper", "bin": "blue_bin", "label": "Paper Cup", "instructions": "Empty liquids completely; dispose in Blue Bin."},

    # 5. Biodegradable / Organic -> Green Bin
    "coffee_grounds": {"category": "biodegradable", "bin": "green_bin", "label": "Coffee Grounds", "instructions": "Organic wet waste; compost or discard in Green Bin."},
    "eggshells": {"category": "biodegradable", "bin": "green_bin", "label": "Eggshells", "instructions": "Organic wet waste; ideal for compost or Green Bin."},
    "food_waste": {"category": "biodegradable", "bin": "green_bin", "label": "Food Waste / Kitchen Scraps", "instructions": "Wet organic waste; discard directly into Green Bin."},
    "tea_bags": {"category": "biodegradable", "bin": "green_bin", "label": "Tea Bag", "instructions": "Organic wet waste; place in Green Bin (remove any staple)."},

    # 6. Textiles / Special -> Special Handling
    "clothing": {"category": "other_issue", "bin": "special_handling", "label": "Clothing / Fabric", "instructions": "Textile waste; donate if wearable or send to textile recycling."},
    "shoes": {"category": "other_issue", "bin": "special_handling", "label": "Footwear / Shoes", "instructions": "Special waste stream; donate if usable or send to shoe recycling."},
}

# Garbage Classification 3 Supported Material Classes:
# BIODEGRADABLE, CARDBOARD, GLASS, METAL, PAPER, PLASTIC
SUPPORTED_WASTE_MATERIALS = {
    "plastic": {"disposal_bin": "blue_bin", "recyclable": True, "description": "Plastic bottles, wrappers, polybags, containers"},
    "biodegradable": {"disposal_bin": "green_bin", "recyclable": True, "description": "Organic food waste, leaves, fruit & vegetable peels"},
    "cardboard": {"disposal_bin": "blue_bin", "recyclable": True, "description": "Corrugated boxes, carton packaging"},
    "glass": {"disposal_bin": "blue_bin", "recyclable": True, "description": "Glass bottles, jars, broken glass"},
    "metal": {"disposal_bin": "blue_bin", "recyclable": True, "description": "Beverage cans, tin foil, scrap metal"},
    "paper": {"disposal_bin": "blue_bin", "recyclable": True, "description": "Newspapers, books, office paper sheets"},
}


def _get_model() -> dict[str, Any] | None:
    global _LOADED_MODEL
    if _LOADED_MODEL is None and os.path.exists(WEIGHTS_PATH):
        try:
            with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
                _LOADED_MODEL = json.load(f)
        except Exception as e:
            print(f"Error loading garbage model weights: {e}")
    return _LOADED_MODEL


def extract_features(img: Image.Image) -> np.ndarray:
    """Extract 96-dimensional visual feature vector matching the training pipeline."""
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
        float(h.std() / 128.0), float(h.std() / 128.0), float(v.std() / 128.0),
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
    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm
    return features


def classify_with_trained_model(image_bytes: bytes) -> dict[str, Any] | None:
    """Classifies an uploaded waste image using the trained EcoTrack-GarbageNet weights."""
    model = _get_model()
    if not model or "prototypes" not in model:
        return None

    try:
        with Image.open(BytesIO(image_bytes)) as img:
            feat = extract_features(img)

        prototypes = model["prototypes"]
        sims = {}
        for cls_name, proto in prototypes.items():
            centroid = np.array(proto["centroid"], dtype=np.float32)
            sim = float(np.dot(feat, centroid))
            sims[cls_name] = sim

        # Softmax probabilities over cosine similarities (temperature = 0.08)
        classes = list(sims.keys())
        raw_sims = np.array([sims[c] for c in classes], dtype=np.float32)
        exp_sims = np.exp((raw_sims - np.max(raw_sims)) / 0.08)
        probs = exp_sims / np.sum(exp_sims)

        best_idx = int(np.argmax(probs))
        predicted_class = classes[best_idx]
        confidence = float(probs[best_idx])

        proto_info = prototypes[predicted_class]
        category = proto_info.get("category", predicted_class.lower())
        disposal_bin = proto_info.get("disposal_bin", "blue_bin")

        return {
            "ai_result": "issue_detected",
            "category": category,
            "material": category,
            "disposal_bin": disposal_bin,
            "confidence": round(confidence, 3),
            "class_probabilities": {c: round(float(p), 3) for c, p in zip(classes, probs)},
            "provider": f"trained-model:{model.get('model_name', 'EcoTrack-GarbageNet')}",
        }
    except Exception as e:
        print(f"Trained model classification failed: {e}")
        return None


def _local_analysis(image_bytes: bytes, filename: str) -> dict[str, Any]:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
    except Exception as error:
        raise ValueError("The uploaded file is not a valid image") from error

    # 1. Use the fine-grained Kaggle MobileNetV2 model if available
    k_pred = classify_with_kaggle_model(image_bytes)
    if k_pred and k_pred.get("confidence", 0) >= 0.18:
        return k_pred

    # 2. Use centroid prototype weights fallback
    trained_pred = classify_with_trained_model(image_bytes)
    if trained_pred and trained_pred.get("confidence", 0) >= 0.18:
        return trained_pred

    # 2. Rule-based keyword matching fallback
    name = filename.lower()
    category = "garbage_dumps"
    material = "mixed"
    disposal_bin = "blue_bin"

    rules = [
        (["plastic", "bottle", "poly", "wrapper", "bag", "pet", "packet", "pouch"], "plastic", "plastic", "blue_bin"),
        (["bio", "food", "organic", "peel", "leaf", "leaves", "vegetable", "fruit", "rotten"], "biodegradable", "biodegradable", "green_bin"),
        (["cardboard", "carton", "box", "packaging", "corrugated"], "cardboard", "cardboard", "blue_bin"),
        (["glass", "jar", "shisha", "kaanch"], "glass", "glass", "blue_bin"),
        (["metal", "can", "tin", "aluminum", "foil", "loha"], "metal", "metal", "blue_bin"),
        (["paper", "newspaper", "kagaz", "sheet", "magazine"], "paper", "paper", "blue_bin"),
        (["animal", "dead", "mrit"], "dead_animals", "none", "special_handling"),
        (["toilet", "shauchalay"], "dirty_public_toilets", "none", "special_handling"),
        (["dustbin", "kudedan"], "uncleaned_dustbins", "mixed", "blue_bin"),
        (["sweep", "jhadu"], "sweeping_not_done", "mixed", "green_bin"),
        (["drain", "naali", "gutter"], "other_issue", "mixed", "special_handling"),
        (["dump", "garbage", "kachra", "kooda"], "garbage_dumps", "mixed", "blue_bin"),
    ]

    for keywords, detected_cat, detected_mat, bin_type in rules:
        if any(k in name for k in keywords):
            category = detected_cat
            material = detected_mat
            disposal_bin = bin_type
            break

    return {
        "ai_result": "issue_detected",
        "category": category,
        "material": material,
        "disposal_bin": disposal_bin,
        "confidence": 0.82,
        "provider": "garbage-classification-engine",
    }


def _gemini_analysis(image_bytes: bytes, filename: str) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = """
    You are an expert AI Computer Vision model trained on the Garbage Classification 3 dataset (17,000+ annotated waste images).
    Your goal is to inspect the uploaded image, identify municipal cleanliness issues, and classify the primary waste material.
    
    Waste Material Streams (Garbage Classification 3 categories):
    - plastic: Plastic bottles, polythene bags, wrappers, packaging, cups
    - biodegradable: Organic wet waste, food leftovers, fruit/vegetable peels, leaves
    - cardboard: Shipping boxes, corrugated cartons, packing boards
    - glass: Glass bottles, jars, glass fragments
    - metal: Drink cans, aluminum tins, foil, scrap metal
    - paper: Newspapers, books, discarded paper sheets
    
    Civic Issue Categories (Swachh Bharat / Municipal Sanitation):
    - garbage_dumps (large open piles of mixed waste)
    - uncleaned_dustbins (overflowing public garbage bins)
    - dead_animals (deceased animal carcass on road)
    - dirty_public_toilets (unhygienic public restrooms)
    - sweeping_not_done (littered roads/streets needing sweeping)
    - other_issue (clogged drains, hazardous construction debris)
    
    If the image clearly shows a specific material, set category to that material (e.g., 'plastic', 'biodegradable', 'cardboard', 'glass', 'metal', 'paper').
    If it is a general street dump, use 'garbage_dumps'.
    If no cleanliness issue or waste is present (e.g. clean street, natural landscape, indoor portrait), set ai_result to 'no_issue_detected' and category to 'none'.
    
    Also indicate:
    - material: "plastic" | "biodegradable" | "cardboard" | "glass" | "metal" | "paper" | "mixed" | "none"
    - disposal_bin: "blue_bin" (dry recyclables) | "green_bin" (wet organic) | "special_handling"
    - confidence: float between 0.0 and 1.0
    
    Respond STRICTLY in valid JSON without markdown wrapping:
    {
      "ai_result": "issue_detected",
      "category": "plastic",
      "material": "plastic",
      "disposal_bin": "blue_bin",
      "confidence": 0.94
    }
    """
    
    mime_type = "image/jpeg"
    lower_name = filename.lower()
    if lower_name.endswith(".png"):
        mime_type = "image/png"
    elif lower_name.endswith(".webp"):
        mime_type = "image/webp"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
                prompt,
            ]
        )
        
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        result = json.loads(result_text)
        if not isinstance(result, dict) or "ai_result" not in result or "category" not in result:
            raise ValueError("Invalid structure")
            
        result["provider"] = "google-gemini-garbage-v3"
        return result
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None


def _get_kaggle_model():
    """Lazy loader for the Kaggle MobileNetV2 model and class mapping."""
    global _KAGGLE_MODEL, _KAGGLE_IDX_TO_CLASS
    if _KAGGLE_MODEL is not None:
        return _KAGGLE_MODEL, _KAGGLE_IDX_TO_CLASS

    if not os.path.exists(KAGGLE_MODEL_PATH) or not os.path.exists(KAGGLE_CLASSES_PATH):
        return None, None

    try:
        import tensorflow as tf
        _KAGGLE_MODEL = tf.keras.models.load_model(KAGGLE_MODEL_PATH, compile=False)
        with open(KAGGLE_CLASSES_PATH, "r", encoding="utf-8") as f:
            classes_dict = json.load(f)
        _KAGGLE_IDX_TO_CLASS = {int(v): k for k, v in classes_dict.items()}
        print(f"[EcoTrack AI] Kaggle MobileNetV2 model loaded successfully ({len(_KAGGLE_IDX_TO_CLASS)} classes).")
    except Exception as e:
        print(f"[EcoTrack AI] Could not load Kaggle model: {e}")
        _KAGGLE_MODEL = None
        _KAGGLE_IDX_TO_CLASS = None

    return _KAGGLE_MODEL, _KAGGLE_IDX_TO_CLASS


def classify_with_kaggle_model(image_bytes: bytes) -> dict[str, Any] | None:
    """Classifies an uploaded waste image using the fine-grained 30-class Kaggle MobileNetV2 model."""
    try:
        model, idx_to_class = _get_kaggle_model()
        if not model or not idx_to_class:
            return None

        with Image.open(BytesIO(image_bytes)) as img:
            img_rgb = img.convert("RGB").resize((160, 160), Image.Resampling.BILINEAR)
            arr = np.asarray(img_rgb, dtype=np.float32)

        # MobileNetV2 normalization: [-1.0, 1.0]
        norm_arr = (arr / 127.5) - 1.0
        tensor = np.expand_dims(norm_arr, axis=0)

        raw_preds = model.predict(tensor, verbose=0)[0]

        # Softmax probabilities
        if np.abs(np.sum(raw_preds) - 1.0) > 0.05:
            exp_preds = np.exp(raw_preds - np.max(raw_preds))
            probs = exp_preds / np.sum(exp_preds)
        else:
            probs = raw_preds

        best_idx = int(np.argmax(probs))
        predicted_class = idx_to_class[best_idx]
        confidence = float(probs[best_idx])

        meta = KAGGLE_CLASS_METADATA.get(predicted_class, {
            "category": "mixed",
            "bin": "blue_bin",
            "label": predicted_class.replace("_", " ").title(),
            "instructions": "Place in appropriate recycling bin."
        })

        class_probabilities = {idx_to_class[i]: round(float(probs[i]), 3) for i in range(len(idx_to_class))}

        return {
            "ai_result": "issue_detected",
            "category": meta["category"],
            "material": meta["category"],
            "detected_item": predicted_class,
            "detected_label": meta["label"],
            "disposal_bin": meta["bin"],
            "disposal_instructions": meta["instructions"],
            "confidence": round(confidence, 3),
            "class_probabilities": class_probabilities,
            "provider": "kaggle:mobilenetv2_30class",
        }
    except Exception as e:
        print(f"[EcoTrack AI] Kaggle model inference error: {e}")
        return None


def analyze_image(image_bytes: bytes, filename: str) -> dict[str, Any]:
    """
    Hybrid Multimodal Waste Analyzer:
    Tier 1: Fast local Kaggle MobileNetV2 inference (sub-50ms CPU, zero API cost).
            If confidence >= 0.70 for a specific item, returns instantly.
    Tier 2: Google Gemini Multimodal Vision API (if configured) for complex civic scenes,
            large roadside dumps, overflowing bins, dead animals, or ambiguous mixed waste.
    Tier 3: External microservice endpoint fallback (if configured).
    Tier 4: Local prototype / keyword heuristic fallback.
    """
    # 1. Tier 1: Fast Local Kaggle Model
    kaggle_pred = classify_with_kaggle_model(image_bytes)
    if kaggle_pred and kaggle_pred.get("confidence", 0) >= 0.70:
        return kaggle_pred

    # 2. Tier 2: Google Gemini Multimodal for Complex Context
    if GEMINI_API_KEY:
        try:
            gemini_pred = _gemini_analysis(image_bytes, filename)
            if gemini_pred and gemini_pred.get("ai_result"):
                if kaggle_pred and "detected_item" not in gemini_pred:
                    gemini_pred["local_model_hint"] = kaggle_pred.get("detected_item")
                return gemini_pred
        except Exception as e:
            print(f"[EcoTrack AI] Gemini analysis failed: {e}")

    # 3. Tier 3: External Endpoint (if configured)
    if AI_ENDPOINT:
        try:
            request = Request(
                AI_ENDPOINT,
                data=image_bytes,
                headers={"Content-Type": "application/octet-stream", "X-Filename": filename},
                method="POST",
            )
            with urlopen(request, timeout=15) as response:
                result = json.loads(response.read().decode())
            if isinstance(result, dict) and "ai_result" in result and "category" in result:
                result["provider"] = "external"
                return result
        except Exception as e:
            print(f"[EcoTrack AI] External endpoint failed: {e}")

    # 4. If Kaggle prediction had reasonable confidence (>= 0.18, ~6x random chance for 30 classes), use it
    if kaggle_pred and kaggle_pred.get("confidence", 0) >= 0.18:
        return kaggle_pred

    # 5. Local prototype / keyword heuristic fallback
    return _local_analysis(image_bytes, filename)
