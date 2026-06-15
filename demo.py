# demo.py — Демонстрация 5 картографических API (2ГИС)
# Лабораторная №8. Город: Омск

import requests
import pygeohash as pgh

KEY = "adbe5bb8-61ce-420e-a519-b523cc53bd6c"


def _check_api(data):
    err = data.get("meta", {}).get("error")
    if err:
        raise ValueError(err.get("message", "Ошибка API 2ГИС"))


# --- 1. ГЕОКОДИНГ: адрес -> координаты ---
def geocode(query):
    url = "https://catalog.api.2gis.com/3.0/items/geocode"
    params = {"q": query, "fields": "items.point", "key": KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    _check_api(data)
    items = data.get("result", {}).get("items", [])
    if not items:
        raise ValueError(f"Не найдено: {query}")
    p = items[0]["point"]
    return p["lat"], p["lon"]


# --- 2. ТАЙЛИНГ: ссылка на тайл карты ---
def tile_url(x, y, z):
    return f"https://tile2.maps.2gis.com/tiles?x={x}&y={y}&z={z}&v=1"


# --- 3. ГЕОХЕШ: координаты -> строка ---
def geohash(lat, lon, precision=9):
    return pgh.encode(lat, lon, precision=precision)


# --- 4. ОБРАТНЫЙ ГЕОКОДИНГ: координаты -> адрес ---
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


# --- 5. ИЗОХРОНА: зона достижимости за N минут ---
def isochrone(lat, lon, minutes=15):
    url = f"https://routing.api.2gis.com/isochrone/2.0.0?key={KEY}"
    body = {
        "start": {"lat": lat, "lon": lon},
        "durations": [minutes * 60],
        "transport": "driving",
    }
    r = requests.post(url, json=body, timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    city = "Омск"
    print(f"=== Демонстрация 5 API для города {city} ===\n")

    print("[1] ГЕОКОДИНГ")
    lat, lon = geocode(city)
    print(f"    {city} -> {lat:.5f}, {lon:.5f}\n")

    print("[2] ТАЙЛИНГ")
    print(f"    {tile_url(620, 320, 10)}\n")

    print("[3] ГЕОХЕШ")
    print(f"    {city} -> {geohash(lat, lon)}\n")

    print("[4] ОБРАТНЫЙ ГЕОКОДИНГ (координаты -> адрес)")
    try:
        addr = reverse_geocode(lat, lon)
        print(f"    {lat:.5f}, {lon:.5f} -> {addr}\n")
    except Exception as e:
        print(f"    Ошибка: {e}\n")

    print("[5] ИЗОХРОНА (15 минут на авто)")
    try:
        isochrone(lat, lon, 15)
        print("    Изохрона получена (GeoJSON-зона)\n")
    except Exception as e:
        print(f"    Ошибка: {e}\n")
