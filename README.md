# Tour of Bosnia &amp; Herzegovina · Interactive Race Dashboard

An embeddable GIS dashboard for the **Tour of Bosnia and Herzegovina** — five stages from Sarajevo through Konjic, Jablanica, Mostar, Ljubuški and Stolac to Neum on the Adriatic.

Built by **[Bozmaps](https://bozmaps.com)** as a marketing proposal to the race organisers: a single page that anchors the race website, lives on tourism-board portals, and hands international journalists a visual brief they can link to in one click.

**Live preview:** *(auto-deployed from `main` branch)*

## Why this dashboard

The LinkedIn post from the organiser framed the Tour as a *"development platform"* linking **infrastructure, tourism and international visibility** — not just a race. This dashboard operationalises that framing:

| Pillar | How the map shows it |
|---|---|
| Infrastructure | Every stage line + elevation + surface, riders and media see exactly what roads carry them |
| Tourism | UNESCO sites (Stari Most, Počitelj, Radimlja stećci), natural monuments (Kravice, Vjetrenica, Hutovo Blato), viewpoints — layered along the route |
| Visibility | Shareable, iframeable, bilingual (BS / EN), mobile-responsive · one URL media can link to worldwide |

## What's in the dashboard

- **5 stages** · Sarajevo → Konjic → Mostar → Ljubuški → Stolac → Neum · ~193 km total · sea level to 971 m (Ivan Saddle)
- **Stage selector** with live elevation profile, distance, climb, difficulty stars
- **Labelled markers** for aid stations, tourist stops, UNESCO heritage, viewpoints, first-aid, and on-course video locations
- **Rich popup cards** with km/elevation metadata, historical notes, direct "Get directions" and "Watch video" CTAs
- **OpenStreetMap POI layer** overlaid live — shops, fuel, lodging, food — so riders and spectators can plan around the route
- **Satellite + Topo + Streets** basemap toggle, **2D / 3D terrain** view, **stage line** toggle
- **Bilingual** Bosnian / English with one click
- **Iframe-ready** — CSP + X-Frame-Options allow embedding on the race site, tourism-board portal, or federation pages

## Embedding

```html
<iframe
  src="https://sarajevo-bike-tours.vercel.app/"
  style="width:100%;height:720px;border:0;border-radius:12px"
  allowfullscreen loading="lazy"></iframe>
```

## Architecture

- Single static page (`index.html`) — no build step, no server
- **MapLibre GL JS** for raster tiles, hillshade and 3D terrain
- **Overpass API** (OpenStreetMap) for live amenity queries
- **AWS Terrarium** DEM for 3D terrain exaggeration
- Route data in `_routes.json` (coords + elevation per stage)
- Deployed on **Vercel** (static, zero-config)

See [TEMPLATE.md](./TEMPLATE.md) for the full scope, design system, and how to adapt this template for other races.

## Data sources

| Dataset | Source |
|---|---|
| Stage routes | Synthesised from city anchors (Sarajevo → Neum corridor); replace with organiser's real GPX |
| Amenity POIs | OpenStreetMap via Overpass API |
| Terrain | AWS Terrain Tiles (Terrarium encoding) |
| Satellite imagery | Esri World Imagery |
| Topographic map | OpenTopoMap (CC-BY-SA) |
| Street basemap | CARTO Voyager |
| UNESCO sites | whc.unesco.org |

## Running locally

```bash
python -m http.server 8080
# open http://localhost:8080/
```

## Regenerating the stage data

```bash
python _gen_routes.py
# overwrites _routes.json with the synthesised 5-stage corridor
```

Replace `_routes.json` with real GPX-derived coordinate arrays once the race organiser provides stage tracks.

## License

Dashboard code © 2026 Bozmaps · Route and race data © the respective organisers.

---

**Pitch this to race organisers:** [semir@bozmaps.com](mailto:semir@bozmaps.com) · [bozmaps.com](https://bozmaps.com)
