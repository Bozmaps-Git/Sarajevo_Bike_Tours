# Bozmaps Race-Dashboard Template — Scope, Design &amp; Reuse Guide

> This document captures the **reusable template** behind the Bozmaps race-dashboard platform — the product shape that was first shipped for [Falcon's Paths MTB Marathon](https://falcons-paths.vercel.app/embed) and is now re-skinned for the Tour of Bosnia and Herzegovina. Drop in for any future cycling, running, trail or rally event.

## 1. Product scope

A **single-page, iframe-ready GIS dashboard** that a race organiser can embed on their website, share on social, and give to journalists as a visual brief — without commissioning any custom web dev.

**Core jobs-to-be-done:**

1. **Orient riders & spectators** — show the route, elevation, aid stations and key landmarks in one screen.
2. **Sell the region** — surface tourism, heritage and natural features along the corridor.
3. **Drop into a website** — single URL, `<iframe>` friendly, mobile-responsive, bilingual.
4. **Stay cheap** — static hosting (free on Vercel), open data (OSM, free DEMs), no database.

## 2. Reference implementations

| Project | Repo | Live | Theme |
|---|---|---|---|
| Falcon's Paths MTB Marathon | `Bozmaps-Git/Falcons_Paths` | `/embed` | Dark · amber |
| Falcon's Paths (light variant) | same | `/standalone` | Light · amber |
| Tour of Bosnia &amp; Herzegovina | `Bozmaps-Git/Sarajevo_Bike_Tours` | `/` | Dark · navy + gold |

## 3. Design system

### 3.1 Layout (fixed slots)

```
┌─────────────────────────────────────────────────┐
│  Top bar (56 px)                                │   brand + nav tabs + lang
├─────────────────────────────────────────────────┤
│                                 ┌─────────────┐ │
│                                 │  Side panel │ │   route info / gallery /
│     MAP (fills viewport)        │  (320 px)   │ │   contacts — tabbed
│                                 │             │ │
│     · labeled markers           │             │ │
│     · layer-pill bar (top)      │             │ │
│     · OSM POI dots              │             │ │
│                                 └─────────────┘ │
├─────────────────────────────────────────────────┤
│  Elevation strip (108 px)       GPX · Share · ℹ │   hover-scrubbable profile
└─────────────────────────────────────────────────┘
```

### 3.2 Overlay-first controls

- Layer toggles (routes / POI / relief / basemap) float on the map canvas, not above it.
- Side panel is an overlay card, not a sidebar flush to the viewport edge — leaves margin so the map breathes.
- Elevation strip is the only fixed dock (bottom). Everything else floats.

### 3.3 Marker vocabulary

| Kind | Colour | Icon | Use for |
|---|---|---|---|
| `start` | green | play | Stage start |
| `finish` | red | flag | Stage finish |
| `checkpoint` | blue | drop | Aid / refreshment station |
| `viewpoint` | green | peak | Scenic outlook, summit |
| `medical` | red | plus | First-aid point |
| `video` | amber | play | On-course video / media location |
| `finish-tourist` | amber | pin | UNESCO or landmark as finish line |

Rich popups always carry: category tag, place name, stage context, km / elevation / during-race meta, optional historical note, and a CTA (YouTube video link OR Google Maps directions).

### 3.4 Palette swap

Per-project accent pair is set via CSS variables. No other CSS changes needed for a re-skin.

| Project | `--amber` (primary) | Route line | Banner mood |
|---|---|---|---|
| Falcon's Paths | `#e8a55c` warm amber | `#e8a55c` | Dinaric sunset silhouette |
| Tour of BiH | `#ffc840` flag gold | `#4a8ed8` flag blue | Dinaric ridge + navy gradient |

## 4. Technical stack

| Layer | Choice | Why |
|---|---|---|
| Hosting | Vercel (static) | Zero config, CDN, free for small orgs |
| Framework | Vanilla HTML/CSS/JS | No build step — edit, push, done |
| Map engine | MapLibre GL JS 4.7+ | Free, WebGL, terrain, vector + raster |
| Basemaps | Esri / CARTO / OpenTopoMap | All free for non-commercial use; organiser pays if heavy |
| Terrain DEM | AWS Terrarium | Public, no key, exaggeration via `setTerrain` |
| POI data | Overpass API (OSM) | Free, on-demand, 3 endpoints for redundancy |
| Fonts | Google Fonts (Inter / Fraunces / JetBrains Mono) | CDN, low-latency |
| Geocoding | OSM Nominatim (optional) | Free |
| Routing | OSRM or organiser GPX | Synthetic curves for proposals, real GPX for production |

**No backend required.** Every feature runs in-browser.

## 5. File structure

```
<project-name>/
  index.html            # the entire app (≈40 KB HTML + CSS + JS)
  _routes.json          # {stage-key: {name, coords:[[lon,lat,ele], ...]}, ...}
  _gen_routes.py        # script that generates _routes.json from city anchors
  vercel.json           # cleanUrls, caching, iframe-embedding headers
  README.md             # client-facing overview + embed snippet
  TEMPLATE.md           # this file (internal reuse guide)
  .gitignore
  assets/               # (optional) photos for gallery tab
```

## 6. How to fork this for a new race

1. **Clone template.** Copy `Bozmaps-Git/Sarajevo_Bike_Tours` (or `Falcons_Paths`) as starting point.
2. **Replace route data** in `_routes.json`:
   - Each stage key gets `{name, coords:[[lon,lat,ele], ...]}`.
   - Use `_gen_routes.py` for synthesised proposal-quality routes, or drop organiser GPX in, parse with `DOMParser`.
3. **Replace event markers** — find `const EVENT_MARKERS = […]` in `index.html`, rewrite per-stage with real aid-stations, viewpoints, medical posts, tourist highlights. Each marker needs: `kind`, `route`, `atRatio` (0–1), `name`, `ele`, `km`, `label:{bs,en}`, optional `note`, optional `video`.
4. **Replace route meta** — find `const ROUTE_META = {…}` and fill `title`, `lenOverride`, `gainOverride`, `difficulty`, `bulletsBs`, `bulletsEn` per stage.
5. **Swap colors** in the `:root` CSS block — two variable pairs (`--amber`, `--amber-deep`) and line-color values in `paint:{"line-color":…}` lines in the JS.
6. **Update header** — brand text, mountain silhouette colours (two inline SVG `url("data:…")` blocks), logo icon.
7. **Update Gallery & Contacts tabs** — `galleryHtml()` and `contactsHtml()` functions — with organiser details and real photos.
8. **Deploy** — push to a GitHub repo, link to Vercel once, every push auto-deploys.

Total effort per new race: **2–4 hours** if organiser provides GPX + photo pack.

## 7. Backend / data flow

Runtime:

```
Browser
  ├── static HTML/CSS/JS (Vercel CDN)
  ├── _routes.json (local file, <50 KB)
  ├── MapLibre raster tile requests → Esri / CARTO / OpenTopoMap CDNs
  ├── MapLibre DEM requests        → AWS Terrarium S3
  └── POI query (POST)             → Overpass API (3 endpoint failover)
```

- No database. No auth. No persistent user state beyond a `localStorage` language preference.
- All POI fetches are cached in-memory for the session.
- Elevation profile and stats are computed client-side from `_routes.json` coordinates — no API calls.

**When the organiser needs more:**
- Race results or live leaderboard → add a `/api/` edge function on Vercel, hit runtrace.net or timing-provider API, swap a new side-panel tab.
- Live rider tracking (GPS dot on map) → add a Supabase realtime channel, push lat/lng per rider, subscribe client-side and render a custom marker layer.
- Photo galleries with CMS → drop-in Sanity or Contentful; replace the placeholder tiles in `galleryHtml()` with a fetch against their API.

## 8. Performance targets

| Metric | Target | Current |
|---|---|---|
| First contentful paint | &lt; 1.5 s on 4G | ~0.9 s (Vercel edge) |
| Time to map interactive | &lt; 3 s | ~2.1 s |
| `_routes.json` size | &lt; 50 KB | ~22 KB for 5 stages / 846 points |
| POI payload | &lt; 500 KB | ~120–300 KB depending on corridor |
| Total JS | &lt; 200 KB | ~160 KB (MapLibre is the bulk) |

## 9. Monetisation / pitch

Bozmaps sells this to race organisers as a **fixed-scope engagement**, not a time-and-materials build:

| Package | Delivery | Price anchor |
|---|---|---|
| Proposal demo (synthetic routes) | Branded preview on `*.vercel.app` | Free / lead gen |
| Production dashboard | Real GPX, real photos, organiser's domain, 1 year hosting | £1,800 – £3,500 |
| Ongoing season | Realtime rider tracking, timing integration, results panel | £400 / month |

The template's value prop: the organiser gets **something that looks like a €20k custom build for the price of a weekend's work**, because the hard design work is already done and re-skinning is scripted.

## 10. Known gaps (template backlog)

- Vector-tile basemap (vs. raster) for crisper zoom at high DPI
- Client-side GPX upload → auto-profile + temporary share link
- Ridership live overlay (requires timing-partner API)
- Elevation-profile tooltip linked to map marker (hover strip → marker highlights on map)
- Gallery lightbox (currently flat tiles)
- Offline / PWA caching for course-day spectator use with weak signal

## 11. Credits &amp; licensing

Template by **[Bozmaps](https://bozmaps.com)** · MIT-licensed code · data under each provider's terms (Esri, CARTO, OpenTopoMap, OpenStreetMap, AWS). Organisers retain ownership of their route / photo assets.
