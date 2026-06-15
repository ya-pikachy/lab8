# app.py — Лабораторная №8. Базовое демо API + индивидуальное задание (вариант 2)
# Город: Омск

import re
import json
import math
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pygeohash as pgh

KEY = "adbe5bb8-61ce-420e-a519-b523cc53bd6c"
HOME_CITY = "Омск"

PAGES = {
    "demo": "Базовые API",
    "v2": "Вариант 2 · Маршрут",
}

st.set_page_config(
    page_title="Лабораторная №8. Картографические API",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    .stApp { background-color: #0a0a0a; }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #f5f5f5;
    }
    .block-container { padding-top: 1.2rem; padding-bottom: 3rem;
                       max-width: 100%; }
    header[data-testid="stHeader"] { background: #0a0a0a; }
    footer { visibility: hidden; }

    .app-header {
        padding: 28px 32px;
        background: linear-gradient(135deg, #1a0000 0%, #0a0a0a 60%, #1a1a1a 100%);
        border: 1px solid #3f0000;
        border-left: 4px solid #dc2626;
        border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.12);
    }
    .app-header h1 { margin: 0; font-size: 26px; font-weight: 700;
                     color: #fafafa; }
    .app-header p { margin: 8px 0 0 0; font-size: 14px; color: #a3a3a3; }
    .app-badges { margin-top: 12px; }
    .badge { display: inline-block; padding: 4px 11px; margin-right: 6px;
        background: rgba(220, 38, 38, 0.15); color: #fca5a5;
        border: 1px solid #7f1d1d; border-radius: 20px;
        font-size: 11px; font-weight: 600; }

    .nav-panel {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 16px 10px 10px 10px;
        position: sticky; top: 1rem;
    }
    .nav-title {
        font-size: 10px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; color: #dc2626; margin: 0 6px 14px 6px;
    }

    div[data-testid="column"]:first-of-type .stButton > button {
        width: 100%; text-align: left; justify-content: flex-start;
        background: transparent !important; color: #a3a3a3 !important;
        border: 1px solid transparent !important; border-radius: 8px !important;
        font-weight: 600; font-size: 14px; padding: 11px 14px !important;
        margin-bottom: 2px; box-shadow: none !important;
    }
    div[data-testid="column"]:first-of-type .stButton > button:hover {
        background: #1a1a1a !important; color: #fafafa !important;
    }
    div[data-testid="column"]:first-of-type .stButton > button[kind="primary"] {
        background: #1c0000 !important; color: #fafafa !important;
        border-color: #dc2626 !important;
        box-shadow: inset 3px 0 0 #dc2626 !important;
    }

    .section-title { font-size: 20px; font-weight: 700; color: #fafafa;
        margin: 0 0 14px 0; padding-bottom: 10px;
        border-bottom: 2px solid #3f0000; }
    .section-sub { font-size: 13px; color: #737373; margin: -6px 0 16px 0; }

    .task-card {
        background: #141414; border: 1px solid #2a2a2a;
        border-left: 4px solid #dc2626; border-radius: 10px;
        padding: 16px 20px; margin-bottom: 16px;
    }
    .task-card h3 { margin: 0 0 8px 0; font-size: 15px; color: #ef4444; }
    .task-io { font-size: 13px; color: #a3a3a3; line-height: 1.6; }
    .task-io b { color: #e5e5e5; }

    .block { background: #141414; border: 1px solid #2a2a2a;
        border-radius: 10px; padding: 18px 20px; margin-bottom: 14px; }
    .block-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.5px; color: #dc2626; margin-bottom: 6px;
        margin-top: 8px; }
    .block-value { background: #0a0a0a; border: 1px solid #333;
        border-radius: 8px; padding: 11px 13px; font-size: 14px;
        font-weight: 600; color: #f5f5f5; word-break: break-all;
        line-height: 1.55; }
    .mono { font-family: "Consolas","Courier New",monospace; font-size: 13px; }

    .report-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .report-table th { text-align: left; padding: 10px 12px; color: #ef4444;
        border-bottom: 2px solid #3f0000; font-weight: 700; }
    .report-table td { padding: 10px 12px; color: #e5e5e5 !important;
        border-bottom: 1px solid #2a2a2a; font-weight: 500; }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #141414 !important; border: 1px solid #404040 !important;
        border-radius: 8px; color: #f5f5f5 !important; }
    .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #d4d4d4 !important; font-weight: 600; }
    .stButton > button {
        background: #dc2626 !important; color: #fff !important;
        border: none !important; border-radius: 8px;
        padding: 10px 24px; font-weight: 600; font-size: 14px; }
    .stButton > button:hover {
        background: #b91c1c !important; color: #fff !important; }

    [data-testid="stMetric"] {
        background: #141414; border: 1px solid #2a2a2a;
        border-left: 3px solid #dc2626; border-radius: 10px;
        padding: 14px 16px; }
    [data-testid="stMetricLabel"] { font-weight: 700; color: #a3a3a3; }
    [data-testid="stMetricValue"] { color: #fafafa; }

    div[data-testid="stAlert"] {
        background-color: #1a0000; border: 1px solid #7f1d1d;
        color: #fca5a5;
    }
    .stSuccess { background-color: #0d1a0d !important;
        border-color: #166534 !important; }
    .stInfo { background-color: #141414 !important;
        border-color: #404040 !important; }

    [data-testid="stCodeBlock"] pre {
        background: #0a0a0a !important; border: 1px solid #333 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ======================= API-ФУНКЦИИ =======================

def _check_api(data):
    err = data.get("meta", {}).get("error")
    if err:
        raise ValueError(err.get("message", "Ошибка API 2ГИС"))


def geocode(query):
    url = "https://catalog.api.2gis.com/3.0/items/geocode"
    params = {"q": query, "fields": "items.point", "key": KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    _check_api(data)
    items = data.get("result", {}).get("items", [])
    if not items:
        raise ValueError(f"Объект не найден: {query}")
    p = items[0]["point"]
    return p["lat"], p["lon"]


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


def geohash_encode(lat, lon, precision=9):
    return pgh.encode(lat, lon, precision=precision)


def geohash_center(gh):
    lat, lon, _, _ = pgh.decode_exactly(gh)
    return lat, lon


def tile_url(x, y, z):
    return f"https://tile2.maps.2gis.com/tiles?x={x}&y={y}&z={z}&v=1"


def deg2tile(lat, lon, z):
    lat_rad = math.radians(lat)
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def osm_tile_url(x, y, z):
    return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"


def route_full(lat1, lon1, lat2, lon2):
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("Маршрут не найден")
    route = data["routes"][0]
    return route["duration"] / 60, route["distance"] / 1000, route["geometry"]


def get_isochrone(lat, lon, minutes, transport="driving"):
    url = f"https://routing.api.2gis.com/isochrone/2.0.0?key={KEY}"
    body = {"start": {"lat": lat, "lon": lon},
            "durations": [minutes * 60], "transport": transport}
    raw = requests.post(url, json=body, timeout=30).json()
    return parse_2gis_isochrone(raw)


def parse_2gis_isochrone(iso_json):
    if not isinstance(iso_json, dict):
        return None
    features = []
    isochrones = (iso_json.get("isochrones")
                  or iso_json.get("result", {}).get("isochrones") or [])
    for iso in isochrones:
        geom = iso.get("geometry")
        if not geom:
            continue
        if isinstance(geom, str):
            nums = [float(n) for n in re.findall(r"[-+]?\d+\.?\d*", geom)]
            ring = [[nums[i], nums[i + 1]]
                    for i in range(0, len(nums) - 1, 2)]
            if ring:
                features.append({"type": "Feature",
                                 "geometry": {"type": "Polygon",
                                              "coordinates": [ring]},
                                 "properties": {}})
        elif isinstance(geom, dict) and "coordinates" in geom:
            features.append({"type": "Feature", "geometry": geom,
                             "properties": {}})
    if not features:
        return None
    return {"type": "FeatureCollection", "features": features}


def hide_leaflet_logo(folium_map):
    folium_map.get_root().header.add_child(folium.Element(
        "<style>"
        ".leaflet-control-attribution a[href*='leafletjs']{display:none;}"
        ".leaflet-control-attribution svg,"
        ".leaflet-control-attribution img{display:none;}"
        "</style>"))
    return folium_map


def fmt_time(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h} ч {m} мин" if h else f"{m} мин"


def show_geojson(obj, label="GeoJSON результат"):
    st.markdown(f'<div class="block-label">{label}</div>',
                unsafe_allow_html=True)
    st.code(json.dumps(obj, ensure_ascii=False, indent=2), language="json")


def task_header(title, inp, out):
    st.markdown(
        f"""
        <div class="task-card">
            <h3>{title}</h3>
            <div class="task-io"><b>На входе:</b> {inp}</div>
            <div class="task-io"><b>На выходе:</b> {out}</div>
        </div>
        """, unsafe_allow_html=True)


def render_nav_title():
    return (
        '<div class="nav-panel">'
        '<div class="nav-title">Навигация</div></div>'
    )


# ======================= ШАПКА =======================

st.markdown(
    f"""
    <div class="app-header">
        <h1>Лабораторная работа №8</h1>
        <p>Картографические API — демонстрация и индивидуальное задание</p>
        <div class="app-badges">
            <span class="badge">Город: {HOME_CITY}</span>
            <span class="badge">Вариант 2</span>
            <span class="badge">2ГИС · OSRM · pygeohash</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "demo"

nav_col, content_col = st.columns([1, 4], gap="medium")

with nav_col:
    st.markdown(render_nav_title(), unsafe_allow_html=True)
    for key, label in PAGES.items():
        btn_type = "primary" if key == st.session_state.page else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type=btn_type):
            st.session_state.page = key
            st.rerun()

with content_col:
    page = st.session_state.page

    # ============== БАЗОВЫЕ API ==============
    if page == "demo":
        st.markdown('<div class="section-title">'
                    'Базовое взаимодействие с картографическими API'
                    '</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">Геокодинг · тайлинг · геохеш · '
            f'маршруты · изохроны для города {HOME_CITY}</div>',
            unsafe_allow_html=True)

        demo_addr = st.text_input(
            "Адрес / объект для демонстрации",
            value=f"{HOME_CITY}, площадь Ленина",
            key="demo_addr")

        if st.button("Запустить демонстрацию всех API", key="demo_btn"):
            try:
                lat, lon = geocode(demo_addr)
                st.session_state["demo"] = {
                    "lat": lat, "lon": lon, "addr": demo_addr}
            except Exception as e:
                st.error(f"Ошибка геокодинга: {e}")
                st.session_state.pop("demo", None)

        if "demo" in st.session_state:
            d = st.session_state["demo"]
            lat, lon = d["lat"], d["lon"]

            st.markdown(
                '<div class="block-label">1. Геокодинг '
                '(адрес → координаты)</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="block"><div class="block-value mono">'
                f'"{d["addr"]}" → {lat:.5f}, {lon:.5f}</div></div>',
                unsafe_allow_html=True)

            st.markdown(
                '<div class="block-label">2. Обратный геокодинг '
                '(координаты → адрес)</div>', unsafe_allow_html=True)
            try:
                rev = reverse_geocode(lat, lon)
            except Exception as e:
                rev = f"ошибка: {e}"
            st.markdown(
                f'<div class="block"><div class="block-value">'
                f'{lat:.5f}, {lon:.5f} → {rev}</div></div>',
                unsafe_allow_html=True)

            st.markdown(
                '<div class="block-label">3. Геохеш '
                '(координаты → строка разной точности)</div>',
                unsafe_allow_html=True)
            gh_rows = "".join(
                f"<tr><td>{p}</td><td class='mono'>"
                f"{geohash_encode(lat, lon, p)}</td></tr>"
                for p in range(1, 10))
            st.markdown(
                f'<div class="block"><table class="report-table">'
                f'<thead><tr><th>Точность</th><th>Геохеш</th></tr></thead>'
                f'<tbody>{gh_rows}</tbody></table></div>',
                unsafe_allow_html=True)

            z = 13
            tx, ty = deg2tile(lat, lon, z)
            url_osm = osm_tile_url(tx, ty, z)
            url_2gis = tile_url(tx, ty, z)
            st.markdown(
                '<div class="block-label">4. Тайлинг '
                '(координаты → номер тайла → изображение)</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="block"><div class="block-value mono">'
                f'z={z}, x={tx}, y={ty}<br>OSM: {url_osm}<br>'
                f'2ГИС: {url_2gis}</div></div>', unsafe_allow_html=True)
            try:
                st.image(url_osm, width=256,
                         caption=f"Тайл OSM z={z} x={tx} y={ty}")
            except Exception:
                st.info("Не удалось загрузить изображение тайла.")

            st.markdown(
                '<div class="block-label">5. Построение маршрута '
                '(OSRM, до центра города)</div>', unsafe_allow_html=True)
            try:
                c_lat, c_lon = geocode(HOME_CITY)
                mins, km, _ = route_full(lat, lon, c_lat, c_lon)
                st.markdown(
                    f'<div class="block"><div class="block-value">'
                    f'Маршрут до центра {HOME_CITY}: '
                    f'{fmt_time(mins)} · {km:.1f} км</div></div>',
                    unsafe_allow_html=True)
            except Exception as e:
                st.info(f"Маршрут не построен: {e}")

            st.markdown(
                '<div class="block-label">6. Построение изохроны '
                '(2ГИС, 10 мин на авто)</div>', unsafe_allow_html=True)
            iso = None
            try:
                iso = get_isochrone(lat, lon, 10, transport="driving")
                if iso:
                    st.success("Изохрона 10 минут получена (GeoJSON).")
                else:
                    st.info("Изохрона не вернулась на этом ключе.")
            except Exception as e:
                st.info(f"Ошибка изохроны: {e}")

            st.markdown('<div class="block-label">Сводная карта</div>',
                        unsafe_allow_html=True)
            m = folium.Map(location=[lat, lon], zoom_start=13,
                           tiles="cartodbdark_matter",
                           attr="© OpenStreetMap, © CartoDB")
            hide_leaflet_logo(m)
            folium.Marker([lat, lon], popup=rev,
                          icon=folium.Icon(color="red")).add_to(m)
            if iso:
                folium.GeoJson(iso, style_function=lambda x: {
                    "color": "#dc2626", "fillColor": "#ef4444",
                    "fillOpacity": 0.2, "weight": 2}).add_to(m)
            st_folium(m, width=None, height=420, key="demo_map",
                      returned_objects=[], use_container_width=True)

    # ============== ВАРИАНТ 2 — МАРШРУТ ПО ГЕОХЕШАМ ==============
    elif page == "v2":
        task_header(
            "Вариант 2. Маршрут между центрами двух геохешей",
            "2 геохеша",
            "маршрут в виде GeoJSON")

        c1, c2 = st.columns(2)
        gh1 = c1.text_input("Геохеш — аэропорт", value="v9u0skg2z", key="v2_gh1")
        gh2 = c2.text_input("Геохеш — центр города", value="v9u0vc4r7", key="v2_gh2")

        if st.button("Построить маршрут", key="v2_btn"):
            try:
                lat1, lon1 = geohash_center(gh1.strip())
                lat2, lon2 = geohash_center(gh2.strip())
                addr1 = reverse_geocode(lat1, lon1)
                addr2 = reverse_geocode(lat2, lon2)
                minutes, km, geom = route_full(lat1, lon1, lat2, lon2)
                st.session_state["v2"] = {
                    "p1": (lat1, lon1), "p2": (lat2, lon2),
                    "a1": addr1, "a2": addr2,
                    "min": minutes, "km": km, "geom": geom}
            except Exception as e:
                st.error(f"Ошибка: {e}")
                st.session_state.pop("v2", None)

        if "v2" in st.session_state:
            d = st.session_state["v2"]
            col1, col2 = st.columns(2)
            col1.markdown(
                f'<div class="block"><div class="block-label">Точка 1</div>'
                f'<div class="block-value">{d["a1"]}<br>'
                f'<span class="mono">{d["p1"][0]:.5f}, '
                f'{d["p1"][1]:.5f}</span></div></div>',
                unsafe_allow_html=True)
            col2.markdown(
                f'<div class="block"><div class="block-label">Точка 2</div>'
                f'<div class="block-value">{d["a2"]}<br>'
                f'<span class="mono">{d["p2"][0]:.5f}, '
                f'{d["p2"][1]:.5f}</span></div></div>',
                unsafe_allow_html=True)
            st.success(f"Маршрут: {fmt_time(d['min'])} · {d['km']:.1f} км")

            clat = (d["p1"][0] + d["p2"][0]) / 2
            clon = (d["p1"][1] + d["p2"][1]) / 2
            m = folium.Map(location=[clat, clon], zoom_start=13,
                           tiles="cartodbdark_matter",
                           attr="© OpenStreetMap, © CartoDB")
            hide_leaflet_logo(m)
            folium.Marker(d["p1"], popup="Аэропорт",
                          icon=folium.Icon(color="green", icon="plane",
                                           prefix="fa")).add_to(m)
            folium.Marker(d["p2"], popup="Центр города",
                          icon=folium.Icon(color="red", icon="home",
                                           prefix="fa")).add_to(m)
            folium.GeoJson({"type": "Feature", "geometry": d["geom"]},
                           style_function=lambda x: {
                               "color": "#dc2626", "weight": 5,
                               "opacity": 0.9}).add_to(m)
            st_folium(m, width=None, height=460, key="v2_map",
                      returned_objects=[], use_container_width=True)
            show_geojson(
                {"type": "Feature", "geometry": d["geom"],
                 "properties": {"duration_min": round(d["min"], 1),
                                  "distance_km": round(d["km"], 2)}},
                "Маршрут (GeoJSON)")
