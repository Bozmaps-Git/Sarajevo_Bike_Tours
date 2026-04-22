# Bozmaps Race-Dashboard Template — Scope, Design &amp; Reuse Guide

> The **reusable template** behind the Bozmaps race-dashboard platform — from the minimum-viable Falcon's Paths embed to the full Tour of Bosnia and Herzegovina website. Drop in for any future cycling, running, trail or rally event.

## 1. Product shape

Two linked pages, one repo. **No backend.** Works in any browser, embeds anywhere.

| Page | Purpose | File |
|---|---|---|
| **Landing site** | Marketing + education: hero, stages, "Learn about X", highlights, CTA | [index.html](./index.html) |
| **Interactive dashboard** | Map-first GIS view — overlay controls, markers, popups, elevation | [map.html](./map.html) |

The landing page **iframes** the dashboard into its map section, so visitors get a live preview without leaving the page — and journalists/tourism boards can embed `/map.html` in their own sites with one line.

## 2. Reference implementations

| Project | Repo | Live | Flavour |
|---|---|---|---|
| Falcon's Paths MTB Marathon | `Bozmaps-Git/Falcons_Paths` | `/` marketing + `/embed` widget | Dark · amber · MTB single-loop |
| Tour of Bosnia &amp; Herzegovina | `Bozmaps-Git/Sarajevo_Bike_Tours` | `/` full site + `/map` dashboard | Blue/gold/green · 5-stage tour · education-first |

## 3. Core design principles

1. **Two pages, not one** — marketing landing and interactive dashboard have different jobs. Don't cram both into a single file.
2. **Map-as-truth** — every fact on the landing page (km, climb, number of UNESCO sites, difficulty) is pulled from `_routes.json`, not hand-coded. Regenerate the data and the whole site updates.
3. **Real geometry, real elevations** — always. No synthesised curves in production. OSRM + SRTM via OpenTopoData is free and accurate enough for any pitch.
4. **Overlay-first dashboard** — controls float *on* the map, not above it. Side panel is a rounded card with margin, not flush to the edge.
5. **Bilingual** — all user-facing text goes through `I18N[LANG]`. Never hard-code a Balkan language into UI chrome.
6. **Static hosting forever** — no databases, no auth, no build step. If it needs a backend, it needs a different template.

## 4. Visual system

### Palette slots

| Slot | Meaning | Example (Falcons) | Example (Tour of BiH) |
|---|---|---|---|
| `--sky` / `--panel` | Background + panel | `#14100c` dark | `#1a3d5c` + `#faf6eb` cream |
| `--amber` / `--gold` | Primary accent (route, CTA, stars) | `#e8a55c` amber | `#ffc840` flag-gold |
| `--route` | Route line on map | `#e8a55c` amber | `#4a8ed8` flag-blue |
| `--mountain` | Mountain silhouettes in hero | warm brown | dinaric green |
| `--sea` | Sea / sky blues | — | `#4a8ed8` |

Swap these 4–5 variables and the whole site re-skins.

### Typography

- **Display** · Fraunces (elegant serif, bold at 600–800, italic script at 400)
- **Body** · Inter (clean sans, 400/500/600/700)
- **Mono** · JetBrains Mono (all-caps chip labels, 9–11 px with heavy letter-spacing)

### Hero cliché

Every landing page has a layered SVG hero: distant-mountain silhouette layer, near-mountain layer, meadow layer with jagged top edge. Bike silhouettes peek out of the meadow. The hero never uses a photo — a stylised poster vibe keeps it scalable and fast.

### Stage cards

Per-stage colour chip → varied hero-gradient top → bold 01/02/03 number → `Route A → Route B` line → stat trio (km, climb, difficulty stars) → GPX download + deep-link to map. Five cards across on desktop, one-column on mobile.

### "Learn about X" feature grid

Six cards with coloured icon blocks. Each card covers one *pillar* of what the race means:
- Infrastructure · Tourism · Heritage · Nature &amp; Geology · Culture &amp; Food · International Visibility

This is where the race becomes a vehicle for something bigger — tourism-board talking points live here.

### Highlight tiles

8 square-aspect tiles in a 4-wide grid. Each tile is a category-coloured gradient with a UNESCO/chip tag, the place name, and a 1-line hook. Replace `.hl .ph` CSS background with `<img>` once real photos arrive.

## 5. Dashboard marker vocabulary

| Kind | Colour | Icon | Use for |
|---|---|---|---|
| `start` | green | play | Stage start |
| `finish` | red | flag | Stage finish (when not a landmark) |
| `finish-tourist` | amber | pin | Finish *on* a UNESCO site or landmark |
| `checkpoint` | blue | drop | Aid / refreshment station |
| `viewpoint` | green | peak | Scenic outlook, summit, natural monument |
| `medical` | red | plus | First-aid point |
| `video` | amber | play | On-course video / media location |

Every marker popup carries: category tag · place name · stage context · km / elevation / during-race meta · **optional `note` for tourist/heritage context** · CTA (YouTube video link or Google Maps directions).

## 6. Technical stack

| Layer | Choice | Why |
|---|---|---|
| Hosting | Vercel (static) | Zero config, global CDN, free for small orgs |
| Framework | Vanilla HTML/CSS/JS | No build step — edit, push, done |
| Map engine | MapLibre GL JS 4.7+ | Free, WebGL, terrain, vector + raster |
| Basemaps | Esri / CARTO / OpenTopoMap | All free; organiser pays if heavy |
| Terrain DEM | AWS Terrarium | Public, no key, exaggeration via `setTerrain` |
| Routing | **OSRM public demo** (driving profile) | Real road geometry, free |
| Elevations | **OpenTopoData SRTM 30 m** | Free, 100 points/request, 1 req/sec |
| POI data | Overpass API (OSM) | Free, on-demand, 3 endpoints for failover |
| Fonts | Google Fonts CDN | Low-latency, free |

No backend required. Every feature runs in-browser.

## 7. File structure

```
<project-name>/
  index.html            # landing marketing + education page
  map.html              # interactive GIS dashboard
  _routes.json          # {stage-key: {name, coords, stats, difficulty}, ...}
  _gen_routes.py        # OSRM + OpenTopoData pipeline → _routes.json + gpx/
  gpx/
    stage1.gpx          # one GPX per stage
    ...
    tour_complete.gpx   # combined tour GPX
  vercel.json           # cleanUrls, caching, frame-ancestors *
  README.md             # client-facing project overview
  TEMPLATE.md           # this file (reusable architecture guide)
  .gitignore
```

## 8. How to fork this for a new race

1. **Clone** `Bozmaps-Git/Sarajevo_Bike_Tours` as starting point.
2. **Edit waypoints** at the top of `_gen_routes.py`: define city-anchor lon/lat tuples, list them in `STAGES`, run `python _gen_routes.py`. Outputs `_routes.json` + all GPX files.
3. **Replace `ROUTE_META`** in `map.html` — one block per stage with `title:{bs,en}`, `bulletsBs`, `bulletsEn`, `difficulty`, `shortLabel`.
4. **Replace `EVENT_MARKERS`** in `map.html` — per-stage markers with `kind`, `route`, `atRatio`, `name`, `km`, `ele`, `label:{bs,en}`, optional `note:{bs,en}` for tourist context, optional `video`.
5. **Update `STAGE_META`** in `index.html` (for stage cards) and the **highlight tiles** in the `#highlights` section.
6. **Update `I18N`** blocks in both files — all user-facing strings live there.
7. **Swap the palette** — update `:root` CSS variables in both files plus the mountain-silhouette SVG colours in the hero.
8. **Push &amp; link Vercel** — every push auto-deploys.

Total effort for a new race: **4–6 hours** assuming organiser provides:
- Waypoint list (or just city names — geocode manually)
- 1–2 photos or the organiser's poster for visual tone
- Stage-specific tourist highlights (UNESCO, viewpoints, aid stations)

## 9. Data flow

### Build time (once, when routes change)

```
_gen_routes.py
  ├── For each stage:
  │     ├── OSRM /route/v1/driving/{lon,lat};{...}   → real road coords
  │     ├── downsample uniformly to ~200 pts
  │     └── OpenTopoData /srtm30m?locations=…        → elevations
  ├── Writes _routes.json
  └── Writes gpx/stage*.gpx + gpx/tour_complete.gpx
```

### Runtime (every page load)

```
Browser
  ├── static HTML/CSS/JS (Vercel CDN)
  ├── _routes.json (local, <50 KB)
  ├── MapLibre raster tiles   → Esri / CARTO / OpenTopoMap CDNs
  ├── MapLibre DEM tiles      → AWS Terrarium S3
  └── POI query (Overpass)    → 3-endpoint failover
```

No database. No auth. No persistent user state beyond a `localStorage` language preference.

### When organisers need more

- **Race results or live leaderboard** → Vercel edge function hitting runtrace.net / timing-provider API → new right-panel tab
- **Live rider tracking** → Supabase realtime channel with per-rider lat/lng → custom marker layer
- **Photo gallery with CMS** → Sanity or Contentful → swap `.hl .ph` placeholders with `<img>` tags

## 10. Performance targets

| Metric | Target | Current (Tour of BiH) |
|---|---|---|
| First contentful paint | &lt; 1.5 s on 4G | ~0.9 s (Vercel edge) |
| Time to map interactive | &lt; 3 s | ~2.1 s |
| `_routes.json` size | &lt; 50 KB | ~26 KB (5 stages, 982 points) |
| POI payload | &lt; 500 KB | ~150–350 KB depending on stage corridor |
| Total JS | &lt; 200 KB | ~160 KB (MapLibre is the bulk) |
| Landing HTML | &lt; 80 KB | ~48 KB (inline CSS) |

## 11. Commercial pitch

Bozmaps sells this template as a **fixed-scope engagement**, not hourly:

| Package | Delivery | Price anchor (GBP) |
|---|---|---:|
| Proposal demo | Branded preview on `*.vercel.app` (synthetic routes OK) | free / lead gen |
| Production site | Real GPX, real photos, organiser's domain, 1 year hosting, 2 rounds of revisions | £2 000 – £4 500 |
| Ongoing season | Live rider tracking, timing integration, results panel, monthly updates | £500 / month |
| White-label template licence | One-time — the race org owns the repo, we help them fork for future events | £6 000 + £1 000 per new race |

The value prop: the organiser gets **something that looks like a €20 k custom build for the price of a weekend's work**, because the hard design work is already done and re-skinning is scripted.

## 12. Known gaps (template backlog)

- Vector-tile basemap (vs. raster) for crisper zoom at high DPI
- Client-side GPX upload on the dashboard → auto-profile + temporary share link
- Live rider overlay (requires timing-partner API — write a Vercel Edge function)
- Elevation-profile tooltip linked to map marker (hover strip → marker highlights on map)
- Gallery lightbox (tiles currently flat)
- Offline / PWA caching for course-day spectator use with weak signal
- Real cycling profile from **BRouter** or **Graphhopper** (OSRM public demo is driving-only; fine for paved-road tours, not for singletrack MTB)

## 13. Credits &amp; licensing

Template code © **[Bozmaps](https://bozmaps.com)** · MIT-licensed · data under each provider's terms (Esri, CARTO, OpenTopoMap, OpenStreetMap, AWS, OSRM, OpenTopoData). Organisers retain ownership of their route / photo assets.
