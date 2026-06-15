# main.py — Вариант 2: маршрут между центрами двух геохешей
# Город по варианту: Омск

import json
import sys

import pygeohash as pgh
import requests

KEY = "adbe5bb8-61ce-420e-a519-b523cc53bd6c"
HOME_CITY = "Омск"

# Аэропорт Омска → центр города
DEFAULT_GH1 = "v9u0skg2z"
DEFAULT_GH2 = "v9u0vc4r7"


def _check_api(data):
    err = data.get("meta", {}).get("error")
    if err:
        raise ValueError(err.get("message", "Ошибка API 2ГИС"))


def reverse_geocode(lat, lon):
    url = "https://catalog.api.2gis.com/3.0/items/geocode"
    params = {"lat": lat, "lon": lon, "fields": "items.full_name", "key": KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    _check_api(data)
    items = data.get("result", {}).get("items", [])
    if not items:
        return "адрес не найден"
    return items[0].get("full_name", items[0].get("name", "—"))


def geohash_center(gh):
    lat, lon, _, _ = pgh.decode_exactly(gh.strip())
    return lat, lon


def route_geojson(lat1, lon1, lat2, lon2):
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("Маршрут не найден")
    route = data["routes"][0]
    minutes = route["duration"] / 60
    km = route["distance"] / 1000
    return minutes, km, route["geometry"]


def build_route(gh1, gh2):
    lat1, lon1 = geohash_center(gh1)
    lat2, lon2 = geohash_center(gh2)
    addr1 = reverse_geocode(lat1, lon1)
    addr2 = reverse_geocode(lat2, lon2)
    minutes, km, geometry = route_geojson(lat1, lon1, lat2, lon2)
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "geohash_1": gh1,
            "geohash_2": gh2,
            "address_1": addr1,
            "address_2": addr2,
            "duration_min": round(minutes, 1),
            "distance_km": round(km, 2),
        },
    }
    return feature, minutes, km, (lat1, lon1), (lat2, lon2), addr1, addr2


if __name__ == "__main__":
    print(f"=== Вариант 2: маршрут по геохешам ({HOME_CITY}) ===\n")

    if len(sys.argv) >= 3:
        gh1, gh2 = sys.argv[1], sys.argv[2]
    else:
        gh1, gh2 = DEFAULT_GH1, DEFAULT_GH2

    print(f"Геохеш 1: {gh1}")
    print(f"Геохеш 2: {gh2}\n")

    try:
        feature, minutes, km, p1, p2, addr1, addr2 = build_route(gh1, gh2)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    h = int(minutes // 60)
    m = int(minutes % 60)
    time_str = f"{h} ч {m} мин" if h else f"{m} мин"

    print(f"Точка 1: {addr1}")
    print(f"         {p1[0]:.5f}, {p1[1]:.5f}")
    print(f"Точка 2: {addr2}")
    print(f"         {p2[0]:.5f}, {p2[1]:.5f}")
    print(f"\nМаршрут: {time_str} · {km:.1f} км")
    print("\nGeoJSON:")
    print(json.dumps(feature, ensure_ascii=False, indent=2))
