import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def lookup_ip_location(client_ip: str | None) -> dict[str, object]:
    # Resolve public IP if local
    if not client_ip or client_ip in {"127.0.0.1", "::1", "localhost"}:
        try:
            req = Request("https://api.ipify.org?format=json", headers={"User-Agent": "EcoTrackAI/1.0"})
            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                client_ip = data.get("ip")
        except Exception:
            client_ip = None

    if not client_ip or client_ip in {"127.0.0.1", "::1", "localhost"}:
        return {
            "provider": "default-fallback",
            "ip": "127.0.0.1",
            "city": "Kanpur",
            "region": "Uttar Pradesh",
            "country": "India",
            "latitude": 26.4813,
            "longitude": 80.2904,
            "accuracy": "approximate",
        }

    # Query ipapi.co
    try:
        request = Request(f"https://ipapi.co/{client_ip}/json/", headers={"User-Agent": "EcoTrackAI/1.0"})
        with urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode())
            if not result.get("error") and result.get("latitude") and result.get("longitude"):
                return {
                    "provider": "ipapi.co",
                    "ip": result.get("ip", client_ip),
                    "city": result.get("city", "Kanpur"),
                    "region": result.get("region", "Uttar Pradesh"),
                    "country": result.get("country_name", "India"),
                    "latitude": float(result["latitude"]),
                    "longitude": float(result["longitude"]),
                    "accuracy": "approximate",
                }
    except Exception:
        pass

    # Fallback to ip-api.com
    try:
        req2 = Request(f"http://ip-api.com/json/{client_ip}", headers={"User-Agent": "EcoTrackAI/1.0"})
        with urlopen(req2, timeout=5) as response2:
            res2 = json.loads(response2.read().decode())
            if res2.get("status") == "success":
                return {
                    "provider": "ip-api.com",
                    "ip": client_ip,
                    "city": res2.get("city", "Kanpur"),
                    "region": res2.get("regionName", "Uttar Pradesh"),
                    "country": res2.get("country", "India"),
                    "latitude": float(res2.get("lat", 26.4813)),
                    "longitude": float(res2.get("lon", 80.2904)),
                    "accuracy": "approximate",
                }
    except Exception:
        pass

    return {
        "provider": "fallback",
        "ip": client_ip,
        "city": "Kanpur",
        "region": "Uttar Pradesh",
        "country": "India",
        "latitude": 26.4813,
        "longitude": 80.2904,
        "accuracy": "approximate",
    }
