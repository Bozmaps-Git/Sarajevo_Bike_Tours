# Tour of Bosnia &amp; Herzegovina · Interactive Race Website

> *Od planina do mora.* From Sarajevo's cobbled old town, over Ivan-Saddle pass, through the Neretva canyon past Mostar's UNESCO Old Bridge, and down to the Adriatic at Neum. Five stages, 217 kilometres, 3 270 m of climb — a whole country's geography told on a bike.

Built by **[Bozmaps](https://bozmaps.com)** as a pitch-ready website and embeddable widget for the **Tour of Bosnia and Herzegovina** race organisers and tourism partners.

**Live site:** *(auto-deployed on push to `main`)*

## What's here

| Page | What it is |
|---|---|
| `/` — [index.html](./index.html) | Full marketing + educational website: hero, pillar quote, **5 stage cards with real stats**, interactive map preview, "Learn about BiH" feature grid, 8 highlight tiles, copy-paste embed CTA |
| `/map` — [map.html](./map.html) | The interactive GIS dashboard — overlay controls, labelled markers, rich popups, 3-D terrain, POI layer, elevation profile with hover scrub |
| `/gpx/stage1.gpx` … `stage5.gpx` | Real GPX files for each stage — downloadable from every stage card |
| `/gpx/tour_complete.gpx` | The whole 217 km tour as a single GPX |

## Real routes (not synthetic)

Route geometry uses **OSRM** (public demo) for real road alignment. Elevations come from **SRTM 30 m** via OpenTopoData. Regenerate anytime with `python _gen_routes.py`.

| Stage | Route | Distance | Climb | Min–Max | Difficulty |
|---|---|---:|---:|---|---:|
| S1 | Sarajevo → Konjic | **55.5 km** | 1 215 m | 275 – 998 m | ★★★★☆ |
| S2 | Konjic → Jablanica | 22.7 km | 507 m | 183 – 368 m | ★★☆☆☆ |
| S3 | Jablanica → Mostar | 47.1 km | 474 m | 60 – 236 m | ★★☆☆☆ |
| S4 | Mostar → Ljubuški | 34.1 km | 538 m | 63 – 411 m | ★★★☆☆ |
| S5 | Ljubuški → Neum | 57.4 km | 536 m | 0 – 157 m | ★★★☆☆ |
| **Total** |  | **216.8 km** | **3 270 m** |  |  |

## Features

### On the landing page (`/`)

- **Hero** with layered mountain + meadow SVG silhouettes, bike-mascot animation, pulsing race-dot, hero stats block, animated dashed route in the final CTA
- **Pillar quote** framing the race as *sport as a development platform* (paraphrases the organiser's LinkedIn manifesto)
- **5 stage cards** with per-stage chip (*Queen stage / Easy / Cultural / Karst / Adriatic Finale*), km, climb, 5-star difficulty, GPX download, and "See on map" deep-link
- **Map preview** — `map.html` iframed into the page with a "Open in a new tab" button
- **Learn about BiH** — 6 pillar cards: Infrastructure · Tourism (3 climates) · UNESCO · Nature &amp; Geology · Culture &amp; Food · International Visibility
- **Highlights** — 8 hero tiles (Stari Most, Kravica, Ivan-sedlo, Blagaj Vrelo Bune, Počitelj, Neum, Radimlja Stećci, Prenj)
- **Embed CTA** with copy-to-clipboard iframe snippet, full-tour GPX download
- **Footer** with race links, BiH tourism, GitHub, maker credit
- **Bilingual** Bosnian / English — one click, stored in `localStorage`

### On the dashboard (`/map`)

- MapLibre GL JS with **satellite / streets / topo** basemaps, **2-D / 3-D terrain**
- Labelled custom markers for **starts, finishes, aid stations, viewpoints, medical, video locations, UNESCO sites**
- Rich popup cards per marker — with localised note, km/elevation meta, `Watch video (YouTube)` or `Directions` CTA
- OpenStreetMap POI overlay (Overpass) — shops, fuel, lodging, food, medical, amenities — filterable
- Tabbed right panel — *Stage info · Gallery · Contacts*, with stage picker
- Elevation strip at the bottom with hoverable km/elevation tooltip
- GPX download per active stage + Share / Info actions
- Iframe-ready — CSP headers in `vercel.json` allow embedding anywhere

## Tech stack

- **Hosting** · Vercel (static, zero config) — `vercel.json` sets cleanUrls + `frame-ancestors *` for embedding
- **Framework** · Vanilla HTML/CSS/JS — no build step, no npm
- **Maps** · MapLibre GL JS 4.7 · Esri / CARTO / OpenTopoMap raster basemaps · AWS Terrarium DEM for 3-D
- **Routing** · OSRM public demo (driving profile — approximates cycling on paved roads)
- **Elevations** · OpenTopoData SRTM 30 m
- **POIs** · Overpass API (OSM) with 3 endpoint failover
- **Fonts** · Inter · Fraunces · JetBrains Mono (Google Fonts CDN)

Total JS payload &lt; 200 KB. First contentful paint &lt; 1.5 s on 4G (Vercel edge).

## Embedding on another site

```html
<iframe
  src="https://sarajevo-bike-tours.vercel.app/map.html"
  style="width:100%;height:720px;border:0;border-radius:12px"
  title="Tour of Bosnia and Herzegovina · Interactive Map"
  allowfullscreen loading="lazy"></iframe>
```

The embed code above is also available with a one-click copy button in the final CTA section of the landing page.

## Running locally

```bash
python -m http.server 8080
# http://localhost:8080/         → landing page
# http://localhost:8080/map.html → interactive dashboard
```

## Regenerating route data

```bash
pip install requests
python _gen_routes.py
```

This refetches OSRM road geometry and SRTM elevations and rewrites `_routes.json` + the six `gpx/*.gpx` files. Takes ~30 seconds due to the DEM service rate limit.

## Scope &amp; design

See [TEMPLATE.md](./TEMPLATE.md) for the reusable architecture behind this project — the Bozmaps race-dashboard template that ships as Falcon's Paths, Tour of BiH, and whatever race is next.

## Contact

**[semir@bozmaps.com](mailto:semir@bozmaps.com)** · **[bozmaps.com](https://bozmaps.com)**

Geospatial consultancy based in the UK &amp; Balkans. Happy to white-label this dashboard for any cycling, running, rally or trail event.

---

**Data:** Routes via [OSRM](https://project-osrm.org/) · Elevations via [OpenTopoData](https://www.opentopodata.org/) SRTM30m · POIs via [OpenStreetMap](https://openstreetmap.org/) · Terrain via [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) · Satellite via Esri World Imagery · © respective providers.
