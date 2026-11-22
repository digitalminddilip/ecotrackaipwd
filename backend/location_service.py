import os
import json
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import googlemaps


def parse_google_address_components(components: list[dict[str, Any]]) -> dict[str, str]:
    details = {
        "street": "",
        "area": "",
        "city": "",
        "district": "",
        "state": "",
        "pin_code": "",
    }
    street_parts = []
    area_parts = []
    
    for comp in components:
        types = comp.get("types", [])
        name = comp.get("long_name", "")
        if "street_number" in types or "route" in types:
            street_parts.append(name)
        elif "sublocality" in types or "sublocality_level_1" in types or "neighborhood" in types:
            area_parts.append(name)
        elif "locality" in types:
            details["city"] = name
        elif "administrative_area_level_2" in types:
            details["district"] = name
        elif "administrative_area_level_1" in types:
            details["state"] = name
        elif "postal_code" in types:
            details["pin_code"] = name
            
    if street_parts:
        details["street"] = " ".join(street_parts)
    if area_parts:
        details["area"] = ", ".join(area_parts)
    if not details["city"] and details["area"]:
        details["city"] = details["area"]
    return details


def fallback_nominatim_reverse_geocode(latitude: float, longitude: float) -> dict[str, Any]:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&addressdetails=1"
    req = Request(url, headers={"User-Agent": "EcoTrackAI/2.0 (EcoTrack AI Municipal Waste Intelligence Platform)"})
    try:
        with urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
    except (HTTPError, URLError, TimeoutError, Exception) as err:
        return {
            "address": f"GPS Coordinates ({latitude:.6f}°, {longitude:.6f}°)",
            "formatted_address": f"GPS Coordinates ({latitude:.6f}°, {longitude:.6f}°)",
            "street": "",
            "area": "",
            "city": "",
            "district": "",
            "state": "",
            "pin_code": "",
            "latitude": latitude,
            "longitude": longitude,
            "provider": "coordinates-fallback",
        }

    addr = data.get("address", {}) if isinstance(data, dict) else {}
    street = addr.get("road") or addr.get("street") or addr.get("suburb") or ""
    area = addr.get("neighbourhood") or addr.get("suburb") or addr.get("residential") or addr.get("village") or ""
    city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or ""
    district = addr.get("state_district") or addr.get("county") or ""
    state = addr.get("state") or ""
    pin_code = addr.get("postcode") or ""
    display_name = data.get("display_name") or f"{city}, {state}".strip(", ") or f"{latitude:.6f}°, {longitude:.6f}°"

    return {
        "address": display_name,
        "formatted_address": display_name,
        "street": street,
        "area": area,
        "city": city,
        "district": district,
        "state": state,
        "pin_code": pin_code,
        "latitude": latitude,
        "longitude": longitude,
        "provider": "nominatim-geocoding",
    }


def google_geolocate(payload: dict[str, object]) -> dict[str, object]:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not configured on the server")

    try:
        client = googlemaps.Client(key=api_key, timeout=10)
        result = client.geolocate(**payload)
    except Exception as error:
        raise ValueError("Google Geolocation service is unavailable") from error

    location = result.get("location")
    if not isinstance(location, dict) or "lat" not in location or "lng" not in location:
        raise ValueError("Google returned no valid location")
    return {
        "latitude": location["lat"],
        "longitude": location["lng"],
        "accuracy_meters": result.get("accuracy"),
        "provider": "google-geolocation",
    }


def google_reverse_geocode(latitude: float, longitude: float) -> dict[str, Any]:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return fallback_nominatim_reverse_geocode(latitude, longitude)

    try:
        client = googlemaps.Client(key=api_key, timeout=10)
        results = client.reverse_geocode((latitude, longitude), language="en")
        if not results:
            return fallback_nominatim_reverse_geocode(latitude, longitude)
            
        first = results[0]
        formatted_address = first.get("formatted_address", "")
        components = first.get("address_components", [])
        parsed = parse_google_address_components(components)
        
        return {
            "address": formatted_address,
            "formatted_address": formatted_address,
            "street": parsed["street"],
            "area": parsed["area"],
            "city": parsed["city"],
            "district": parsed["district"],
            "state": parsed["state"],
            "pin_code": parsed["pin_code"],
            "latitude": latitude,
            "longitude": longitude,
            "provider": "google-geocoding",
        }
    except Exception as error:
        print(f"[LocationService] Google Reverse Geocode warning ({error}). Falling back to Nominatim...")
        return fallback_nominatim_reverse_geocode(latitude, longitude)


