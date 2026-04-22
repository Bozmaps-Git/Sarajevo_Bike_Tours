"""
Generate _routes.json for Tour of Bosnia and Herzegovina dashboard.

Stages follow real cycling corridor Sarajevo -> Konjic -> Jablanica -> Mostar
-> Ljubuski -> Stolac -> Neum. Coordinates are approximate (interpolated
between known city anchors with mild curvature) and elevation is synthesized
to match the known macro-terrain:
  * Stage 1 climbs Ivan Saddle (~970 m) then drops to Konjic (~270 m)
  * Stage 2 descends Neretva gorge to Mostar (~60 m)
  * Stage 3 Mostar -> Ljubuski rolls through karst hills (~200 m peaks)
  * Stage 4 Ljubuski -> Stolac over the high karst plateau (~400 m peaks)
  * Stage 5 Stolac -> Neum drops through Popovo polje to Adriatic (0 m)

Real GPX replaces this file when the race organiser provides tracks.
"""
import json, math, random

random.seed(42)

# Known city anchor points (lon, lat, approx elevation m)
SARAJEVO = (18.4131, 43.8563, 520)
IVAN_SAD = (18.0200, 43.7500, 970)   # Ivan Saddle pass
KONJIC   = (17.9631, 43.6536, 270)
JABLAN   = (17.7625, 43.6580, 200)
MOSTAR   = (17.8078, 43.3438,  60)
LJUBUSKI = (17.5489, 43.1961,  95)
STOLAC   = (17.9547, 43.0842,  70)
NEUM     = (17.6106, 42.9239,   0)

def bezier(p0, p1, ctrl, n):
    out = []
    for i in range(n):
        t = i / (n-1)
        x = (1-t)**2 * p0[0] + 2*(1-t)*t*ctrl[0] + t*t*p1[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t*ctrl[1] + t*t*p1[1]
        out.append((x, y))
    return out

def interp_segment(p0, p1, ctrl_offset, n):
    """Quadratic bezier between two lat/lon points with perpendicular offset."""
    mx = (p0[0] + p1[0]) / 2
    my = (p0[1] + p1[1]) / 2
    # perpendicular
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return [p0]
    nx, ny = -dy/length, dx/length
    ctrl = (mx + nx*ctrl_offset, my + ny*ctrl_offset)
    return bezier(p0, p1, ctrl, n)

def elev_along(points, ele_start, ele_end, peak_at=None, peak_ele=None, noise=8):
    """Synthesize elevation. If peak_at (0..1) given, route over a peak."""
    n = len(points)
    out = []
    for i, (x, y) in enumerate(points):
        t = i / (n-1) if n > 1 else 0
        if peak_at is None:
            e = ele_start + (ele_end - ele_start) * t
        else:
            # two-segment: 0..peak then peak..end
            if t <= peak_at:
                local = t / peak_at
                e = ele_start + (peak_ele - ele_start) * (0.5 - 0.5*math.cos(math.pi*local))
            else:
                local = (t - peak_at) / (1 - peak_at)
                e = peak_ele + (ele_end - peak_ele) * (0.5 - 0.5*math.cos(math.pi*local))
        # wiggle
        e += math.sin(t*math.pi*6) * 18 + random.uniform(-noise, noise)
        out.append([x, y, round(e, 1)])
    return out

def build_stage(name_sr, name_en, anchors, ele_profile, total_points=180):
    """anchors = list of (lon,lat), ele_profile = list of (ele, peak_ratio_or_None)
    Builds coords with ele along the anchor path."""
    # distribute points across segments proportional to great-circle distance
    seg_pts = []
    dists = []
    for a, b in zip(anchors[:-1], anchors[1:]):
        d = math.hypot(b[0]-a[0], b[1]-a[1])
        dists.append(d)
    total_d = sum(dists)
    seg_counts = [max(30, int(total_points * d / total_d)) for d in dists]
    # generate
    coords2d = []
    for i, (a, b) in enumerate(zip(anchors[:-1], anchors[1:])):
        # random-ish curvature
        offset = random.uniform(-0.04, 0.04)
        pts = interp_segment(a, b, offset, seg_counts[i])
        if i > 0: pts = pts[1:]  # avoid duplicate
        coords2d.extend(pts)
    # Apply elevation piecewise
    # For simplicity: compute ele along whole path using provided start/peak/end
    # ele_profile: {"start":X, "peak_at":Y, "peak":Z, "end":W, "noise":N}
    coords = elev_along(
        coords2d,
        ele_profile["start"], ele_profile["end"],
        ele_profile.get("peak_at"), ele_profile.get("peak"),
        ele_profile.get("noise", 8),
    )
    return {"name": f"{name_en} · {name_sr}", "coords": [[round(c[0],5), round(c[1],5), c[2]] for c in coords]}

routes = {
    "stage1": build_stage(
        "Sarajevo → Konjic", "Stage 1: Sarajevo to Konjic",
        [SARAJEVO, IVAN_SAD, KONJIC],
        {"start": 520, "peak_at": 0.55, "peak": 970, "end": 270, "noise": 12},
        total_points=200,
    ),
    "stage2": build_stage(
        "Konjic → Mostar", "Stage 2: Konjic via Jablanica to Mostar",
        [KONJIC, JABLAN, MOSTAR],
        {"start": 270, "end": 60, "noise": 10},
        total_points=200,
    ),
    "stage3": build_stage(
        "Mostar → Ljubuški", "Stage 3: Mostar to Ljubuški",
        [MOSTAR, LJUBUSKI],
        {"start": 60, "peak_at": 0.5, "peak": 220, "end": 95, "noise": 8},
        total_points=140,
    ),
    "stage4": build_stage(
        "Ljubuški → Stolac", "Stage 4: Ljubuški to Stolac",
        [LJUBUSKI, STOLAC],
        {"start": 95, "peak_at": 0.45, "peak": 410, "end": 70, "noise": 10},
        total_points=160,
    ),
    "stage5": build_stage(
        "Stolac → Neum", "Stage 5: Stolac to Neum (Adriatic Finale)",
        [STOLAC, NEUM],
        {"start": 70, "peak_at": 0.55, "peak": 340, "end": 0, "noise": 10},
        total_points=150,
    ),
}

with open("_routes.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, separators=(",", ":"))

lengths = {k: len(v["coords"]) for k, v in routes.items()}
total_km_est = sum(
    sum(math.hypot(
        (v["coords"][i][0]-v["coords"][i-1][0])*111*math.cos(math.radians(v["coords"][i][1])),
        (v["coords"][i][1]-v["coords"][i-1][1])*111,
    ) for i in range(1, len(v["coords"])))
    for v in routes.values()
)
print(f"Wrote _routes.json · {sum(lengths.values())} total points · ~{total_km_est:.0f} km total")
for k, v in routes.items():
    km = sum(math.hypot(
        (v["coords"][i][0]-v["coords"][i-1][0])*111*math.cos(math.radians(v["coords"][i][1])),
        (v["coords"][i][1]-v["coords"][i-1][1])*111,
    ) for i in range(1, len(v["coords"])))
    emin = min(c[2] for c in v["coords"])
    emax = max(c[2] for c in v["coords"])
    print(f"  {k}: {len(v['coords'])} pts · ~{km:.1f} km · {emin:.0f}–{emax:.0f} m")
