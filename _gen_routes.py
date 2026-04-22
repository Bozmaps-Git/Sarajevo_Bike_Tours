"""
Generate real road-routed stages and GPX files for the
Tour of Bosnia and Herzegovina bike dashboard.

Route waypoints (per the 2026 poster image):
    Sarajevo -> Konjic -> Jablanica -> Mostar -> Ljubuski -> Neum
with Kravica waterfall inserted as a detour waypoint on the final stage
so the route traces the illustrated curve through the karst.

Pipeline:
    1. For each stage, request the driving route from the public OSRM demo
       (real road geometry, ~1000 points per stage).
    2. Down-sample uniformly along distance to ~200 points per stage.
    3. Batch-query OpenTopoData SRTM-30m to attach real elevations.
    4. Write _routes.json and one GPX per stage plus a combined GPX.

Run:
    python _gen_routes.py

Depends on `requests`; uses only public endpoints, no API keys.
"""
import json, math, time, sys, os
try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

OSRM = "https://router.project-osrm.org/route/v1/driving/{}?overview=full&geometries=geojson"
DEM  = "https://api.opentopodata.org/v1/srtm30m"
DEM_BATCH = 100   # max locations per free-tier request
DEM_SLEEP = 1.1   # free-tier rate limit

# ── Waypoints ──────────────────────────────────────────────────
SARAJEVO = (18.4131, 43.8563)       # Vijećnica area
KONJIC   = (17.9620, 43.6522)       # Stari most, Konjic
JABLANIC = (17.7625, 43.6580)       # Jablanica centar
MOSTAR   = (17.8081, 43.3380)       # Stari Most, Mostar
LJUBUSKI = (17.5489, 43.1961)       # Ljubuški centar
KRAVICA  = (17.6100, 43.1575)       # Vodopad Kravica (detour)
NEUM     = (17.6150, 42.9228)       # Neum riva

STAGES = [
    ("stage1", "Sarajevo → Konjic",
        "Stage 1 · Sarajevo → Konjic", "Etapa 1 · Sarajevo → Konjic",
        [SARAJEVO, KONJIC], 4),
    ("stage2", "Konjic → Jablanica",
        "Stage 2 · Konjic → Jablanica", "Etapa 2 · Konjic → Jablanica",
        [KONJIC, JABLANIC], 2),
    ("stage3", "Jablanica → Mostar",
        "Stage 3 · Jablanica → Mostar", "Etapa 3 · Jablanica → Mostar",
        [JABLANIC, MOSTAR], 2),
    ("stage4", "Mostar → Ljubuški",
        "Stage 4 · Mostar → Ljubuški", "Etapa 4 · Mostar → Ljubuški",
        [MOSTAR, LJUBUSKI], 3),
    ("stage5", "Ljubuški → Neum",
        "Stage 5 · Ljubuški → Neum (Adriatic)", "Etapa 5 · Ljubuški → Neum (Jadran)",
        [LJUBUSKI, KRAVICA, NEUM], 3),
]

TARGET_POINTS_PER_STAGE = 200

# ── Geometry helpers ───────────────────────────────────────────
def hav(a, b):
    R = 6371000.0
    lon1, lat1 = math.radians(a[0]), math.radians(a[1])
    lon2, lat2 = math.radians(b[0]), math.radians(b[1])
    dlon, dlat = lon2-lon1, lat2-lat1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(h))

def downsample(coords, target):
    if len(coords) <= target: return coords
    cum = [0.0]
    for i in range(1, len(coords)):
        cum.append(cum[-1] + hav(coords[i-1], coords[i]))
    total = cum[-1]
    step = total / (target - 1)
    out = [coords[0]]
    next_d = step
    for i in range(1, len(coords)):
        while cum[i] >= next_d and len(out) < target - 1:
            out.append(coords[i])
            next_d += step
    out.append(coords[-1])
    # dedupe consecutive identical points
    ded = [out[0]]
    for p in out[1:]:
        if p != ded[-1]: ded.append(p)
    return ded

# ── OSRM fetch ─────────────────────────────────────────────────
def osrm_route(waypoints):
    coord_str = ";".join(f"{lon},{lat}" for lon, lat in waypoints)
    r = requests.get(OSRM.format(coord_str), timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM: {data.get('code')} {data.get('message','')}")
    geom = data["routes"][0]["geometry"]["coordinates"]
    dist_km = data["routes"][0]["distance"] / 1000.0
    return [(c[0], c[1]) for c in geom], dist_km

# ── Elevation fetch (batched) ──────────────────────────────────
def elevations(coords):
    out = []
    for i in range(0, len(coords), DEM_BATCH):
        batch = coords[i:i+DEM_BATCH]
        locs = "|".join(f"{lat},{lon}" for lon, lat in batch)
        r = requests.get(DEM, params={"locations": locs}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "OK":
            raise RuntimeError(f"DEM: {data.get('status')} {data.get('error','')}")
        for row in data["results"]:
            e = row["elevation"]
            out.append(e if e is not None else 0.0)
        if i + DEM_BATCH < len(coords):
            time.sleep(DEM_SLEEP)
    return out

# ── GPX writer ─────────────────────────────────────────────────
def write_gpx(path, name, coords3d, desc=""):
    pts = "".join(
        f'<trkpt lat="{c[1]:.6f}" lon="{c[0]:.6f}"><ele>{c[2]:.1f}</ele></trkpt>'
        for c in coords3d
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gpx version="1.1" creator="Tour of BiH · Bozmaps" '
        'xmlns="http://www.topografix.com/GPX/1/1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
        'http://www.topografix.com/GPX/1/1/gpx.xsd">\n'
        f'<metadata><name>{name}</name><desc>{desc}</desc></metadata>\n'
        f'<trk><name>{name}</name><trkseg>{pts}</trkseg></trk>\n'
        '</gpx>\n'
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)

# ── Main ───────────────────────────────────────────────────────
def main():
    routes = {}
    all_coords = []

    for key, label_short, name_en, name_bs, waypoints, difficulty in STAGES:
        print(f"\n· {key}: {label_short}")
        print(f"  OSRM route …", end=" ", flush=True)
        road, rd_km = osrm_route(waypoints)
        print(f"{rd_km:.1f} km · {len(road)} points")
        sampled = downsample(road, TARGET_POINTS_PER_STAGE)
        print(f"  downsampled to {len(sampled)} points")
        print(f"  DEM lookup …", end=" ", flush=True)
        eles = elevations(sampled)
        print(f"ok")
        coords3d = [(round(lon,5), round(lat,5), round(e,1))
                    for (lon,lat), e in zip(sampled, eles)]
        emin, emax = min(c[2] for c in coords3d), max(c[2] for c in coords3d)
        gain = sum(max(0, coords3d[i][2]-coords3d[i-1][2]) for i in range(1, len(coords3d)))
        km = sum(hav((coords3d[i-1][0],coords3d[i-1][1]),
                     (coords3d[i][0],coords3d[i][1])) for i in range(1,len(coords3d)))/1000.0
        print(f"  → {km:.1f} km · {emin:.0f}–{emax:.0f} m · gain {gain:.0f} m")

        routes[key] = {
            "name": f"{name_en} · {name_bs}",
            "name_en": name_en, "name_bs": name_bs,
            "coords": [list(c) for c in coords3d],
            "difficulty": difficulty,
            "stats": {"km": round(km,1), "gain_m": round(gain),
                      "min_m": round(emin), "max_m": round(emax)},
        }

        write_gpx(f"gpx/{key}.gpx", name_en, coords3d, name_bs)
        all_coords.extend(coords3d if not all_coords else coords3d[1:])

    # combined tour GPX
    write_gpx("gpx/tour_complete.gpx",
              "Tour of Bosnia and Herzegovina · Complete Route",
              all_coords, "5 stages · Sarajevo to Neum")

    with open("_routes.json", "w", encoding="utf-8") as f:
        json.dump(routes, f, separators=(",", ":"))

    total_km = sum(r["stats"]["km"] for r in routes.values())
    total_gain = sum(r["stats"]["gain_m"] for r in routes.values())
    print(f"\n✓ Wrote _routes.json and 6 GPX files · total {total_km:.1f} km · gain {total_gain:.0f} m")

if __name__ == "__main__":
    os.makedirs("gpx", exist_ok=True)
    main()
