"""
Build an interactive HTML map of Nigeria 2058 voting districts.
Pre-computes district/zone boundaries with shapely, then embeds
everything into a standalone Leaflet.js HTML file (no Turf.js).
"""
import json
from collections import defaultdict
from shapely.geometry import shape, mapping, box, Polygon, MultiPolygon
from shapely.ops import unary_union

# ── Load data ──────────────────────────────────────────────────────────
with open('GeoJSON/nga_lga_enriched.geojson') as f:
    lga_data = json.load(f)
with open('GeoJSON/nga_admin1.geojson') as f:
    state_data = json.load(f)
with open('GeoJSON/nga_admin0.geojson') as f:
    country_data = json.load(f)
with open('GeoJSON/district_info.json') as f:
    district_info = json.load(f)
with open('GeoJSON/zone_info.json') as f:
    zone_info = json.load(f)

# ── Build Nigeria mask (opaque fill to hide basemap under the country) ─
print("Building country mask...")
nigeria_geoms = [shape(f['geometry']).buffer(0) for f in country_data['features']]
nigeria_outline = unary_union(nigeria_geoms)
mask_geo = {
    'type': 'FeatureCollection',
    'features': [{
        'type': 'Feature',
        'properties': {},
        'geometry': mapping(nigeria_outline),
    }]
}
print("  Mask polygon created")

# ── Strip unnecessary properties ──────────────────────────────────────
for feat in lga_data['features']:
    p = feat['properties']
    feat['properties'] = {
        'n': p.get('adm2_name'),   # LGA name
        's': p.get('adm1_name'),   # state
        'd': p.get('district_id'), # district
        'z': p.get('az'),          # zone number
        'zn': p.get('az_name'),    # zone name
    }

for feat in state_data['features']:
    p = feat['properties']
    feat['properties'] = {'n': p.get('adm1_name')}

# ── Pre-compute centroids for all label layers ────────────────────────
print("Computing LGA centroids...")
lga_centers = []
for feat in lga_data['features']:
    try:
        geom = shape(feat['geometry'])
        c = geom.representative_point()
        lga_centers.append({
            'n': feat['properties']['n'],
            'lat': round(c.y, 4),
            'lon': round(c.x, 4),
        })
    except Exception:
        pass

print("Computing state centroids...")
state_centers = []
for feat in state_data['features']:
    try:
        geom = shape(feat['geometry']).buffer(0)
        c = geom.representative_point()
        state_centers.append({
            'n': feat['properties']['n'],
            'lat': round(c.y, 4),
            'lon': round(c.x, 4),
        })
    except Exception:
        pass

# ── Pre-compute district boundaries ───────────────────────────────────
print("Computing district boundaries...")
district_lgas = defaultdict(list)
district_props = {}
for feat in lga_data['features']:
    did = feat['properties']['d']
    if did:
        district_lgas[did].append(feat)
        if did not in district_props:
            district_props[did] = {
                'd': did,
                'z': feat['properties']['z'],
                'zn': feat['properties']['zn'],
            }

district_features = []
for did, feats in district_lgas.items():
    try:
        geoms = [shape(f['geometry']).buffer(0) for f in feats]
        merged = unary_union(geoms)
        district_features.append({
            'type': 'Feature',
            'properties': district_props[did],
            'geometry': mapping(merged),
        })
    except Exception as e:
        print(f"  Warning: district {did} union failed: {e}")

district_geo = {'type': 'FeatureCollection', 'features': district_features}
print(f"  {len(district_features)} district boundaries computed")

print("Computing district centroids...")
district_centers = []
for feat in district_features:
    try:
        geom = shape(feat['geometry'])
        c = geom.representative_point()
        district_centers.append({
            'n': feat['properties']['d'],
            'z': feat['properties']['z'],
            'lat': round(c.y, 4),
            'lon': round(c.x, 4),
        })
    except Exception:
        pass

# ── Pre-compute zone boundaries ───────────────────────────────────────
print("Computing zone boundaries...")
zone_lgas = defaultdict(list)
zone_props = {}
for feat in lga_data['features']:
    az = feat['properties']['z']
    if az:
        zone_lgas[az].append(feat)
        if az not in zone_props:
            zone_props[az] = {
                'z': az,
                'zn': feat['properties']['zn'],
            }

zone_features = []
for az, feats in zone_lgas.items():
    try:
        geoms = [shape(f['geometry']).buffer(0) for f in feats]
        merged = unary_union(geoms)
        zone_features.append({
            'type': 'Feature',
            'properties': zone_props[az],
            'geometry': mapping(merged),
        })
    except Exception as e:
        print(f"  Warning: zone {az} union failed: {e}")

zone_geo = {'type': 'FeatureCollection', 'features': zone_features}
print(f"  {len(zone_features)} zone boundaries computed")

print("Computing zone centroids...")
zone_centers = []
for feat in zone_features:
    try:
        geom = shape(feat['geometry'])
        c = geom.representative_point()
        zone_centers.append({
            'n': 'AZ' + str(feat['properties']['z']),
            'fn': feat['properties']['zn'],
            'z': feat['properties']['z'],
            'lat': round(c.y, 4),
            'lon': round(c.x, 4),
        })
    except Exception:
        pass

# ── Serialize ─────────────────────────────────────────────────────────
lga_json = json.dumps(lga_data)
state_json = json.dumps(state_data)
mask_json = json.dumps(mask_geo)
district_geo_json = json.dumps(district_geo)
zone_geo_json = json.dumps(zone_geo)
district_json = json.dumps(district_info)
zone_json = json.dumps(zone_info)
centers_json = json.dumps(lga_centers)
state_centers_json = json.dumps(state_centers)
district_centers_json = json.dumps(district_centers)
zone_centers_json = json.dumps(zone_centers)

# ── Build HTML ────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NIGERIA 2058 — Electoral Territories</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    background: #FEFDD0; color: #3A2A08; overflow: hidden;
  }}
  #map {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 1;
    background: radial-gradient(ellipse at 40% 50%, #FEFDD0 0%, #EFE9AB 70%);
  }}

  /* ── Scanline overlay ── */
  .scanlines {{
    position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(187,137,14,0.015) 2px,
      rgba(187,137,14,0.015) 4px
    );
  }}

  /* ── Vignette ── */
  .vignette {{
    position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 999;
    pointer-events: none;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(187,137,14,0.12) 100%);
  }}

  /* ── Panel base — Golden parchment HUD ── */
  .panel {{
    position: relative;
    background: linear-gradient(135deg, rgba(254,253,210,0.95) 0%, rgba(239,233,171,0.93) 100%);
    border: 1px solid rgba(187,137,14,0.3);
    backdrop-filter: blur(20px);
    box-shadow:
      0 2px 20px rgba(187,137,14,0.1),
      0 0 10px rgba(205,166,70,0.08),
      inset 0 1px 0 rgba(255,255,255,0.5),
      inset 0 0 30px rgba(252,194,1,0.04);
    clip-path: polygon(
      0 8px, 8px 0, calc(100% - 8px) 0, 100% 8px,
      100% calc(100% - 8px), calc(100% - 8px) 100%, 8px 100%, 0 calc(100% - 8px)
    );
  }}
  /* Corner accents — inline SVG decorations */
  .panel-corners {{
    position: absolute; inset: -1px; pointer-events: none; z-index: 2;
  }}
  .corner {{
    position: absolute; width: 20px; height: 20px;
  }}
  .corner::before, .corner::after {{
    content: ''; position: absolute; background: #BB890E;
  }}
  .corner-tl {{ top: 0; left: 0; }}
  .corner-tl::before {{ top: 0; left: 0; width: 20px; height: 2px; }}
  .corner-tl::after {{ top: 0; left: 0; width: 2px; height: 20px; }}
  .corner-tr {{ top: 0; right: 0; }}
  .corner-tr::before {{ top: 0; right: 0; width: 20px; height: 2px; }}
  .corner-tr::after {{ top: 0; right: 0; width: 2px; height: 20px; }}
  .corner-bl {{ bottom: 0; left: 0; }}
  .corner-bl::before {{ bottom: 0; left: 0; width: 20px; height: 2px; }}
  .corner-bl::after {{ bottom: 0; left: 0; width: 2px; height: 20px; }}
  .corner-br {{ bottom: 0; right: 0; }}
  .corner-br::before {{ bottom: 0; right: 0; width: 20px; height: 2px; }}
  .corner-br::after {{ bottom: 0; right: 0; width: 2px; height: 20px; }}

  /* ── Glowing separator line ── */
  .glow-line {{
    height: 1px; margin: 8px 0;
    background: linear-gradient(90deg,
      transparent 0%,
      rgba(187,137,14,0.15) 15%,
      rgba(187,137,14,0.4) 50%,
      rgba(187,137,14,0.15) 85%,
      transparent 100%
    );
    box-shadow: 0 0 6px rgba(205,166,70,0.15);
  }}

  /* ── Search panel ── */
  .search-panel {{
    position: absolute; top: 14px; left: 56px; z-index: 1000;
    width: 360px; font-size: 13px;
  }}
  .search-panel input {{
    width: 100%; padding: 12px 18px; border: none;
    background: rgba(254,253,220,0.98); color: #3A2A08;
    font-size: 14px; outline: none;
    font-family: 'Rajdhani', sans-serif; font-weight: 500;
    letter-spacing: 1px;
    border: 1px solid rgba(187,137,14,0.25);
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px));
    transition: border-color 0.3s, box-shadow 0.3s;
  }}
  .search-panel input:focus {{
    border-color: rgba(187,137,14,0.6);
    box-shadow: 0 0 20px rgba(252,194,1,0.15), 0 0 40px rgba(205,166,70,0.08);
  }}
  .search-panel input::placeholder {{ color: rgba(187,137,14,0.35); letter-spacing: 3px; font-size: 12px; }}
  .search-results {{
    max-height: 340px; overflow-y: auto; display: none;
    background: rgba(254,253,220,0.98);
    border: 1px solid rgba(187,137,14,0.15); border-top: none;
  }}
  .search-results::-webkit-scrollbar {{ width: 3px; }}
  .search-results::-webkit-scrollbar-thumb {{ background: rgba(187,137,14,0.5); }}
  .search-item {{
    padding: 9px 18px; cursor: pointer;
    border-bottom: 1px solid rgba(187,137,14,0.08);
    display: flex; justify-content: space-between; align-items: center;
    transition: all 0.2s;
  }}
  .search-item:hover {{
    background: rgba(252,194,1,0.1);
    border-left: 2px solid rgba(187,137,14,0.5);
    padding-left: 16px;
  }}
  .search-item .name {{ font-weight: 600; color: #3A2A08; letter-spacing: 0.3px; }}
  .search-item .type {{
    font-size: 8px; padding: 3px 8px;
    text-transform: uppercase; letter-spacing: 2px; font-weight: 700;
    flex-shrink: 0; font-family: 'Orbitron', monospace;
  }}
  .type-lga {{ background: rgba(34,139,34,0.1); color: #1a7a1a; border: 1px solid rgba(34,139,34,0.2); }}
  .type-district {{ background: rgba(0,120,180,0.1); color: #0078b4; border: 1px solid rgba(0,120,180,0.2); }}
  .type-state {{ background: rgba(187,137,14,0.1); color: #BB890E; border: 1px solid rgba(187,137,14,0.2); }}
  .type-zone {{ background: rgba(140,50,200,0.1); color: #8c32c8; border: 1px solid rgba(140,50,200,0.2); }}

  /* ── Layer control ── */
  .layer-control {{
    position: absolute; top: 14px; right: 14px; z-index: 1000;
    padding: 16px 20px; font-size: 13px;
  }}
  .layer-control h3 {{
    font-family: 'Orbitron', monospace;
    font-size: 8px; text-transform: uppercase; letter-spacing: 4px;
    color: rgba(187,137,14,0.6); margin-bottom: 12px;
  }}
  .layer-control .lc-header {{
    display: grid; grid-template-columns: 1fr 50px 50px; gap: 0; align-items: center;
    margin-bottom: 6px; padding-bottom: 4px;
    border-bottom: 1px solid rgba(187,137,14,0.15);
  }}
  .layer-control .lc-header span {{
    font-family: 'Orbitron', monospace; font-size: 7px;
    text-transform: uppercase; letter-spacing: 2px;
    color: rgba(187,137,14,0.4); text-align: center;
  }}
  .layer-control .lc-row {{
    display: grid; grid-template-columns: 1fr 50px 50px; gap: 0; align-items: center;
    padding: 4px 0;
  }}
  .layer-control .lc-row .lc-name {{
    color: rgba(58,42,8,0.6); font-weight: 500; letter-spacing: 0.5px;
  }}
  .layer-control label {{
    display: flex; align-items: center; justify-content: center; cursor: pointer;
    color: rgba(58,42,8,0.6); transition: all 0.2s;
  }}
  .layer-control label:hover {{ color: #BB890E; text-shadow: 0 0 8px rgba(187,137,14,0.2); }}
  .layer-control input[type=checkbox] {{
    accent-color: #BB890E; width: 13px; height: 13px;
  }}

  /* ── Info panel ── */
  .info-panel {{
    position: absolute; bottom: 14px; left: 14px; z-index: 1000;
    padding: 20px 24px; min-width: 350px; max-width: 420px;
    font-size: 13px; display: none;
  }}
  .info-panel h2 {{
    font-family: 'Orbitron', monospace;
    font-size: 14px; color: #BB890E; margin-bottom: 2px;
    letter-spacing: 2px; font-weight: 700;
    text-shadow: 0 1px 2px rgba(187,137,14,0.15);
  }}
  .info-panel .subtitle {{
    font-family: 'Orbitron', monospace;
    font-size: 8px; color: rgba(187,137,14,0.55);
    margin-bottom: 4px; text-transform: uppercase; letter-spacing: 4px;
  }}
  .info-panel .info-row {{
    display: flex; justify-content: space-between; padding: 4px 0;
    border-bottom: 1px solid rgba(187,137,14,0.08);
  }}
  .info-panel .info-label {{ color: rgba(58,42,8,0.5); font-weight: 400; letter-spacing: 0.3px; }}
  .info-panel .info-value {{ color: #3A2A08; font-weight: 600; text-align: right; }}
  .nav-link {{
    cursor: pointer; color: #BB890E;
    border-bottom: 1px dotted rgba(187,137,14,0.35);
    transition: all 0.2s;
  }}
  .nav-link:hover {{
    color: #FCC201;
    text-shadow: 0 0 6px rgba(252,194,1,0.3);
    border-bottom-color: rgba(187,137,14,0.6);
  }}
  .info-panel .close-btn {{
    position: absolute; top: 12px; right: 16px; cursor: pointer;
    color: rgba(187,137,14,0.35); font-size: 18px; line-height: 1;
    font-family: 'Orbitron', monospace;
    transition: all 0.2s;
  }}
  .info-panel .close-btn:hover {{ color: #BB890E; text-shadow: 0 0 8px rgba(187,137,14,0.3); }}

  /* ── Title cartouche ── */
  .map-title {{
    position: absolute; bottom: 14px; right: 14px; z-index: 1000;
    padding: 16px 24px; text-align: center;
    background: linear-gradient(135deg, rgba(254,253,210,0.96) 0%, rgba(239,233,171,0.94) 100%);
    border: 1px solid rgba(187,137,14,0.35);
    backdrop-filter: blur(20px);
    box-shadow: 0 2px 30px rgba(187,137,14,0.1), 0 0 20px rgba(205,166,70,0.06);
    clip-path: polygon(
      0 10px, 10px 0, calc(100% - 10px) 0, 100% 10px,
      100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px)
    );
  }}
  .map-title h1 {{
    font-family: 'Orbitron', monospace;
    font-size: 24px; font-weight: 900;
    letter-spacing: 10px; text-transform: uppercase;
    background: linear-gradient(180deg, #FCC201 0%, #BB890E 40%, #8A6200 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 1px 3px rgba(187,137,14,0.25));
  }}
  .map-title .year {{
    font-family: 'Orbitron', monospace;
    font-size: 10px; color: rgba(187,137,14,0.5);
    letter-spacing: 10px; margin-top: 4px;
  }}
  .map-title p {{
    font-size: 11px; color: rgba(58,42,8,0.4);
    letter-spacing: 2px; margin-top: 8px;
  }}
  .map-title .adinkra {{
    font-size: 16px; letter-spacing: 6px; margin: 4px 0;
    color: rgba(187,137,14,0.25);
  }}

  /* ── Legend ── */
  .legend {{
    position: absolute; bottom: 130px; right: 14px; z-index: 1000;
    padding: 14px 18px; font-size: 12px;
  }}
  .legend h3 {{
    font-family: 'Orbitron', monospace;
    font-size: 7px; text-transform: uppercase; letter-spacing: 4px;
    color: rgba(187,137,14,0.5); margin-bottom: 10px;
  }}
  .legend-item {{
    display: flex; align-items: center; gap: 10px; padding: 3px 0;
    color: rgba(58,42,8,0.65); font-weight: 500; font-size: 11px;
  }}
  .legend-swatch {{
    width: 12px; height: 14px;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    box-shadow: 0 0 6px currentColor;
  }}

  /* ── Leaflet overrides ── */
  .leaflet-control-zoom a {{
    background: rgba(254,253,220,0.95) !important;
    color: #BB890E !important;
    border-color: rgba(187,137,14,0.25) !important;
    font-family: 'Orbitron', monospace !important;
  }}
  .leaflet-control-zoom a:hover {{
    background: rgba(252,194,1,0.15) !important;
    box-shadow: 0 2px 10px rgba(187,137,14,0.15) !important;
  }}
  .leaflet-control-attribution {{
    background: rgba(254,253,220,0.7) !important;
    color: rgba(58,42,8,0.3) !important;
    font-size: 9px !important;
  }}
  .leaflet-control-attribution a {{ color: rgba(187,137,14,0.4) !important; }}

  /* ── Animated ambient glow ── */
  @keyframes glow-pulse {{
    0%, 100% {{ opacity: 0.2; }}
    50% {{ opacity: 0.4; }}
  }}
  .ambient-glow {{
    position: fixed; pointer-events: none; z-index: 0;
    width: 600px; height: 600px; border-radius: 50%;
    filter: blur(120px);
    animation: glow-pulse 12s ease-in-out infinite;
  }}
  .glow-1 {{
    top: -200px; left: -100px;
    background: rgba(252,194,1,0.06);
  }}
  .glow-2 {{
    bottom: -200px; right: -100px;
    background: rgba(187,137,14,0.05);
    animation-delay: -6s;
  }}
  .glow-3 {{
    top: 30%; left: 40%;
    width: 400px; height: 400px;
    background: rgba(205,166,70,0.04);
    animation-delay: -3s;
  }}

  /* ── Floating holographic grid (subtle) ── */
  @keyframes grid-drift {{
    0% {{ transform: translate(0, 0); }}
    100% {{ transform: translate(30px, 30px); }}
  }}
  .holo-grid {{
    position: fixed; inset: 0; z-index: 998; pointer-events: none;
    opacity: 0.012;
    background-image:
      linear-gradient(rgba(187,137,14,1) 1px, transparent 1px),
      linear-gradient(90deg, rgba(187,137,14,1) 1px, transparent 1px);
    background-size: 80px 80px;
    animation: grid-drift 20s linear infinite;
  }}
</style>
</head>
<body>

<!-- Ambient atmosphere -->
<div class="ambient-glow glow-1"></div>
<div class="ambient-glow glow-2"></div>
<div class="ambient-glow glow-3"></div>
<div class="holo-grid"></div>
<div class="scanlines"></div>
<div class="vignette"></div>

<div id="map"></div>

<!-- Search -->
<div class="search-panel panel">
  <div class="panel-corners"><div class="corner corner-tl"></div><div class="corner corner-tr"></div><div class="corner corner-bl"></div><div class="corner corner-br"></div></div>
  <input type="text" id="searchInput" placeholder="SEARCH TERRITORIES..." autocomplete="off" />
  <div class="search-results" id="searchResults"></div>
</div>

<!-- Layer control -->
<div class="layer-control panel">
  <div class="panel-corners"><div class="corner corner-tl"></div><div class="corner corner-tr"></div><div class="corner corner-bl"></div><div class="corner corner-br"></div></div>
  <h3>Layers</h3>
  <div class="lc-header"><span></span><span>Border</span><span>Label</span></div>
  <div class="lc-row"><span class="lc-name">Admin Zones</span><label><input type="checkbox" id="togZone" checked></label><label><input type="checkbox" id="togZoneLbl" checked></label></div>
  <div class="lc-row"><span class="lc-name">States</span><label><input type="checkbox" id="togState" checked></label><label><input type="checkbox" id="togStateLbl" checked></label></div>
  <div class="lc-row"><span class="lc-name">Districts</span><label><input type="checkbox" id="togDistrict" checked></label><label><input type="checkbox" id="togDistrictLbl" checked></label></div>
  <div class="lc-row"><span class="lc-name">LGAs</span><label><input type="checkbox" id="togLGA" checked></label><label><input type="checkbox" id="togLGALbl" checked></label></div>
</div>

<!-- Info panel -->
<div class="info-panel panel" id="infoPanel">
  <div class="panel-corners"><div class="corner corner-tl"></div><div class="corner corner-tr"></div><div class="corner corner-bl"></div><div class="corner corner-br"></div></div>
  <span class="close-btn" onclick="document.getElementById('infoPanel').style.display='none'; clearHighlight();">&#x2715;</span>
  <div id="infoPanelContent"></div>
</div>

<!-- Legend -->
<div class="legend panel" id="legend">
  <div class="panel-corners"><div class="corner corner-tl"></div><div class="corner corner-tr"></div><div class="corner corner-bl"></div><div class="corner corner-br"></div></div>
  <h3>Admin Zones</h3>
  <div id="legendItems"></div>
</div>

<!-- Title cartouche -->
<div class="map-title">
  <div class="adinkra">&#x2726; &#x25C7; &#x2726;</div>
  <h1>NIGERIA</h1>
  <div class="year">&#x2736; 2 0 5 8 &#x2736;</div>
  <div class="glow-line"></div>
  <p>150 Districts &middot; 774 LGAs &middot; 8 Zones</p>
  <div class="adinkra">&#x25C7; &#x2726; &#x25C7;</div>
</div>

<script>
// ── Embedded data ──
const lgaData = {lga_json};
const stateData = {state_json};
const districtGeo = {district_geo_json};
const zoneGeo = {zone_geo_json};
const maskData = {mask_json};
const districtInfo = {district_json};
const zoneInfo = {zone_json};
const lgaCenters = {centers_json};
const stateCenters = {state_centers_json};
const districtCenters = {district_centers_json};
const zoneCenters = {zone_centers_json};

// ── Zone colors — warm earth-tone palette for cream theme ──
const ZC = {{
  1: '#BB890E', // Federal Capital — Dark Amber
  2: '#C85A10', // Niger — Burnt Sienna
  3: '#8B3AA0', // Confluence — Rich Plum
  4: '#1A8A50', // Littoral — Forest Emerald
  5: '#1878A8', // Eastern — Deep Teal
  6: '#C42040', // Central — Crimson
  7: '#D07010', // Chad — Copper Sun
  8: '#5B3DC8', // Savanna — Royal Indigo
}};
// Brighter versions for zone borders
const ZG = {{
  1: '#FCC201', 2: '#E87830', 3: '#A855C8', 4: '#28A868',
  5: '#2098C8', 6: '#E83858', 7: '#E89030', 8: '#7B5DE8',
}};

// ── Build legend ──
const legendEl = document.getElementById('legendItems');
for (const [az, info] of Object.entries(zoneInfo).sort((a,b) => a[1].az - b[1].az)) {{
  legendEl.innerHTML += '<div class="legend-item"><div class="legend-swatch" style="background:' + ZC[info.az] + '"></div>' + info.zone_name + '</div>';
}}

// ── Map init ──
const map = L.map('map', {{
  center: [9.05, 7.49], zoom: 7, zoomControl: false, preferCanvas: true,
}});
L.control.zoom({{ position: 'topleft' }}).addTo(map);
// Light basemap — fully visible
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OSM &copy; CARTO', subdomains: 'abcd', maxZoom: 19,
  opacity: 1,
}}).addTo(map);

// Nigeria-shaped mask: opaque cream fill hides basemap rivers/terrain under the country
L.geoJSON(maskData, {{
  style: {{ fillColor: '#FEFDD0', fillOpacity: 1, stroke: false }},
  interactive: false,
}}).addTo(map);

function fmt(n) {{ return n == null ? '\u2014' : Number(n).toLocaleString(); }}

// ── LGA layer — glowing polygons ──
let hlLGA = null;
const lgaLayer = L.geoJSON(lgaData, {{
  style: function(f) {{
    return {{
      fillColor: ZC[f.properties.z] || '#222',
      fillOpacity: 0.18,
      color: ZC[f.properties.z] || '#333',
      weight: 0.6,
      opacity: 0.3,
    }};
  }},
  onEachFeature: function(f, layer) {{
    layer.on({{
      mouseover: function() {{
        if (hlActive) return;
        if (hlLGA && hlLGA !== layer) lgaLayer.resetStyle(hlLGA);
        const c = ZG[f.properties.z] || '#BB890E';
        layer.setStyle({{ fillOpacity: 0.4, weight: 2, color: c, opacity: 0.8 }});
        layer.bringToFront();
        if (map.hasLayer(districtLayer)) districtLayer.bringToFront();
        if (map.hasLayer(stateLayer)) stateLayer.bringToFront();
        if (map.hasLayer(zoneLayer)) zoneLayer.bringToFront();
        hlLGA = layer;
      }},
      mouseout: function() {{
        if (hlActive) return;
        if (hlLGA === layer) {{ lgaLayer.resetStyle(layer); hlLGA = null; }}
      }},
      click: function() {{
        // Zoom-based selection: click picks entity type matching current zoom
        const z = map.getZoom();
        const p = f.properties;
        if (z >= 11)     selectLGA(p);
        else if (z >= 9) selectDistrict(p.d);
        else if (z >= 8) selectState(p.s);
        else             selectZone(p.z);
      }},
    }});
  }},
}}).addTo(map);

// ── District layer — dashed neon outlines (display only, clicks via LGA layer) ──
const districtLayer = L.geoJSON(districtGeo, {{
  interactive: false,
  style: function(f) {{
    return {{
      fillColor: 'transparent', fillOpacity: 0,
      color: ZG[f.properties.z] || '#fff',
      weight: 1.5, opacity: 0.5, dashArray: '8,4',
    }};
  }},
}}).addTo(map);

// ── State layer — amber filigree (display only) ──
const stateLayer = L.geoJSON(stateData, {{
  interactive: false,
  style: {{ fillColor: 'transparent', fillOpacity: 0, color: 'rgba(187,137,14,0.4)', weight: 1.5, dashArray: '1,4' }},
}}).addTo(map);

// ── Zone layer — heavy glowing borders (display only) ──
const zoneLayer = L.geoJSON(zoneGeo, {{
  interactive: false,
  style: function(f) {{
    return {{
      fillColor: 'transparent', fillOpacity: 0,
      color: ZG[f.properties.z] || '#fff',
      weight: 3, opacity: 0.8,
    }};
  }},
}}).addTo(map);
// Double-stroke glow layer underneath
L.geoJSON(zoneGeo, {{
  style: function(f) {{
    return {{
      fillColor: 'transparent', fillOpacity: 0,
      color: ZC[f.properties.z] || '#fff',
      weight: 8, opacity: 0.15,
    }};
  }},
  interactive: false,
}}).addTo(map);

// ── Zoom-dependent labels for all entity types ──
function makeLabel(lat, lon, text, style) {{
  return L.marker([lat, lon], {{
    icon: L.divIcon({{
      className: '',
      html: '<span style="' + style + '">' + text + '</span>',
      iconSize: [0, 0], iconAnchor: [0, 0],
    }}),
    interactive: false,
  }});
}}

const labelBase = 'font-family:Rajdhani,sans-serif;white-space:nowrap;pointer-events:none;text-shadow:0 0 6px rgba(254,253,208,0.9),0 0 3px rgba(254,253,208,0.95),0 1px 3px rgba(254,253,208,0.8);display:inline-block;transform:translate(-50%,-50%);';

// Zone labels (AZ name + full name)
const zoneLabels = L.layerGroup(zoneCenters.map(c =>
  makeLabel(c.lat, c.lon, c.n + '<br><span style="font-size:11px;opacity:0.7;letter-spacing:1px">' + c.fn + '</span>',
    labelBase + 'font-family:Orbitron,monospace;font-size:16px;font-weight:900;color:' + (ZC[c.z] || '#BB890E') + ';letter-spacing:4px;text-align:center;line-height:1.5;filter:drop-shadow(0 0 4px rgba(254,253,208,0.8))')
));

// State labels
const stateLabels = L.layerGroup(stateCenters.map(c =>
  makeLabel(c.lat, c.lon, c.n,
    labelBase + 'font-size:12px;font-weight:700;color:rgba(58,42,8,0.7);letter-spacing:2px;text-transform:uppercase')
));

// District labels
const districtLabels = L.layerGroup(districtCenters.map(c =>
  makeLabel(c.lat, c.lon, c.n,
    labelBase + 'font-size:10px;font-weight:600;color:' + (ZG[c.z] || '#ccc') + ';opacity:0.75;letter-spacing:1px')
));

// LGA labels
const lgaLabels = L.layerGroup(lgaCenters.map(c =>
  makeLabel(c.lat, c.lon, c.n,
    labelBase + 'font-size:9px;font-weight:500;color:rgba(58,42,8,0.55);letter-spacing:0.5px')
));

// Zoom thresholds per label layer
const lblOn = {{ zone: true, state: true, district: true, lga: true }};
function updateLabels() {{
  const z = map.getZoom();
  const want = {{
    zone:     lblOn.zone     && z >= 6  && z < 9,
    state:    lblOn.state    && z >= 8  && z < 11,
    district: lblOn.district && z >= 9  && z < 11,
    lga:      lblOn.lga      && z >= 11,
  }};
  want.zone     ? (map.hasLayer(zoneLabels)     || map.addLayer(zoneLabels))     : map.removeLayer(zoneLabels);
  want.state    ? (map.hasLayer(stateLabels)    || map.addLayer(stateLabels))    : map.removeLayer(stateLabels);
  want.district ? (map.hasLayer(districtLabels) || map.addLayer(districtLabels)) : map.removeLayer(districtLabels);
  want.lga      ? (map.hasLayer(lgaLabels)      || map.addLayer(lgaLabels))      : map.removeLayer(lgaLabels);
}}
map.on('zoomend', updateLabels);
updateLabels();

// ── Layer toggles (borders) ──
document.getElementById('togLGA').onchange = function() {{ this.checked ? map.addLayer(lgaLayer) : map.removeLayer(lgaLayer); }};
document.getElementById('togDistrict').onchange = function() {{ this.checked ? map.addLayer(districtLayer) : map.removeLayer(districtLayer); }};
document.getElementById('togState').onchange = function() {{ this.checked ? map.addLayer(stateLayer) : map.removeLayer(stateLayer); }};
document.getElementById('togZone').onchange = function() {{ this.checked ? map.addLayer(zoneLayer) : map.removeLayer(zoneLayer); }};

// ── Layer toggles (labels) ──
document.getElementById('togZoneLbl').onchange = function() {{ lblOn.zone = this.checked; updateLabels(); }};
document.getElementById('togStateLbl').onchange = function() {{ lblOn.state = this.checked; updateLabels(); }};
document.getElementById('togDistrictLbl').onchange = function() {{ lblOn.district = this.checked; updateLabels(); }};
document.getElementById('togLGALbl').onchange = function() {{ lblOn.lga = this.checked; updateLabels(); }};

// ── Selection highlight system ──
let hlActive = false;
let hlBorderLayer = null;   // the border layer being highlighted
let hlBorderRef = null;     // which border layerGroup it belongs to

function highlightLGAs(pred) {{
  // Dim all LGAs, brighten matching ones
  hlActive = true;
  lgaLayer.eachLayer(l => {{
    const f = l.feature;
    if (pred(f)) {{
      const gc = ZG[f.properties.z] || '#BB890E';
      l.setStyle({{ fillOpacity: 0.5, weight: 1.8, color: gc, opacity: 0.9 }});
    }} else {{
      l.setStyle({{ fillOpacity: 0.03, weight: 0.3, color: '#CDA646', opacity: 0.12 }});
    }}
  }});
}}

function highlightBorder(layerGroup, pred) {{
  // Brighten matching border, dim others
  layerGroup.eachLayer(l => {{
    if (pred(l.feature)) {{
      l.setStyle({{ weight: 4, opacity: 1, color: '#BB890E', dashArray: '' }});
      l.bringToFront();
      hlBorderLayer = l;
      hlBorderRef = layerGroup;
    }} else {{
      l.setStyle({{ opacity: 0.1 }});
    }}
  }});
}}

function clearHighlight() {{
  if (!hlActive) return;
  hlActive = false;
  lgaLayer.eachLayer(l => lgaLayer.resetStyle(l));
  districtLayer.eachLayer(l => districtLayer.resetStyle(l));
  stateLayer.eachLayer(l => stateLayer.resetStyle(l));
  zoneLayer.eachLayer(l => zoneLayer.resetStyle(l));
  hlBorderLayer = null;
  hlBorderRef = null;
}}

function selectLGA(props) {{
  clearHighlight();
  highlightLGAs(f => f.properties.n === props.n && f.properties.s === props.s);
  showLGAInfo(props);
}}

function selectDistrict(did) {{
  clearHighlight();
  highlightLGAs(f => f.properties.d === did);
  highlightBorder(districtLayer, f => f.properties.d === did);
  showDistrictInfo(did);
}}

function selectState(name) {{
  clearHighlight();
  highlightLGAs(f => f.properties.s === name);
  highlightBorder(stateLayer, f => f.properties.n === name);
  showStateInfo(name);
}}

function selectZone(az) {{
  clearHighlight();
  highlightLGAs(f => f.properties.z == az);
  highlightBorder(zoneLayer, f => f.properties.z == az);
  showZoneInfo(az);
}}

// ── Info panels ──
const GL = '<div class="glow-line"></div>';
function showLGAInfo(p) {{
  const d = p.d ? districtInfo[p.d] : null;
  let h = '<h2>' + p.n + '</h2>';
  h += '<div class="subtitle">Local Government Area</div>';
  h += GL;
  h += row('State', link(p.s, "selectState('" + esc(p.s) + "')"));
  h += row('Voting District', p.d ? link(p.d, "selectDistrict('" + esc(p.d) + "')") : '\u2014');
  h += row('Admin Zone', link('AZ' + p.z + ' \u2014 ' + (p.zn || ''), "selectZone(" + p.z + ")"));
  if (d) {{
    h += GL;
    h += '<div class="subtitle">District Details \u00b7 ' + p.d + '</div>';
    h += row('Population', fmt(d.population));
    h += row('Top Group', d.top1_group + ' (' + d.top1_pct + '%)');
    h += row('2nd Group', d.top2_group + ' (' + d.top2_pct + '%)');
    h += row('Religion', d.pct_muslim + '% M / ' + d.pct_christian + '% C / ' + d.pct_trad + '% T');
  }}
  showPanel(h);
}}

function showDistrictInfo(did) {{
  const d = districtInfo[did]; if (!d) return;
  let h = '<h2>' + did + '</h2>';
  h += '<div class="subtitle">Voting District \u00b7 ' + link(d.az_name, "selectZone(" + d.az + ")") + '</div>';
  h += GL;
  h += row('LGAs', d.num_lgas);
  h += row('Population', fmt(d.population));
  h += row('States', d.states.split(', ').map(s => link(s, "selectState('" + esc(s.trim()) + "')")).join(', '));
  h += row('Top Group', d.top1_group + ' (' + d.top1_pct + '%)');
  h += row('2nd Group', d.top2_group + ' (' + d.top2_pct + '%)');
  h += row('3rd Group', d.top3_group + ' (' + d.top3_pct + '%)');
  h += row('Religion', d.pct_muslim + '% M / ' + d.pct_christian + '% C / ' + d.pct_trad + '% T');
  h += '<div style="margin-top:8px;font-size:11px;color:rgba(58,42,8,0.35)">LGAs: ' + d.lga_list + '</div>';
  showPanel(h);
}}

function showStateInfo(name) {{
  const lgas = lgaData.features.filter(f => f.properties.s === name);
  const dists = new Set(lgas.map(f => f.properties.d).filter(Boolean));
  const zones = new Set(lgas.map(f => f.properties.z).filter(Boolean));
  let h = '<h2>' + name + '</h2>';
  h += '<div class="subtitle">State</div>';
  h += GL;
  h += row('LGAs', lgas.length);
  h += row('Voting Districts', dists.size);
  h += row('Admin Zones', [...zones].map(z => link('AZ' + z, 'selectZone(' + z + ')')).join(', '));
  h += '<div style="margin-top:8px;font-size:11px;color:rgba(58,42,8,0.35)">Districts: ' + [...dists].sort().map(d => link(d, "selectDistrict('" + esc(d) + "')")).join(', ') + '</div>';
  showPanel(h);
}}

function showZoneInfo(az) {{
  const info = zoneInfo[String(az)]; if (!info) return;
  let h = '<h2>AZ' + az + ' \u2014 ' + info.zone_name + '</h2>';
  h += '<div class="subtitle">Administrative Zone</div>';
  h += GL;
  h += row('Districts', info.num_districts);
  h += row('LGAs', info.num_lgas);
  h += row('Population', fmt(info.total_pop));
  h += row('States', info.states.split(', ').map(s => link(s, "selectState('" + esc(s.trim()) + "')")).join(', '));
  showPanel(h);
}}

function row(label, value) {{
  return '<div class="info-row"><span class="info-label">' + label + '</span><span class="info-value">' + value + '</span></div>';
}}
function link(text, onclick) {{
  return '<span class="nav-link" onclick="' + onclick + '">' + text + '</span>';
}}
function esc(s) {{ return s.replace(/'/g, "\\\\'"); }}
function showPanel(html) {{
  document.getElementById('infoPanelContent').innerHTML = html;
  document.getElementById('infoPanel').style.display = 'block';
}}

// ── Search ──
const SI = [];
lgaData.features.forEach(f => {{
  SI.push({{ name: f.properties.n, type: 'lga', detail: f.properties.s + ' \u00b7 ' + (f.properties.d || ''), props: f.properties }});
}});
for (const [did, info] of Object.entries(districtInfo)) {{
  SI.push({{ name: did, type: 'district', detail: info.az_name + ' \u00b7 ' + info.states, did: did }});
}}
stateData.features.forEach(f => {{
  SI.push({{ name: f.properties.n, type: 'state', detail: 'State', sn: f.properties.n }});
}});
for (const [az, info] of Object.entries(zoneInfo)) {{
  SI.push({{ name: 'AZ' + info.az + ' \u2014 ' + info.zone_name, type: 'zone', detail: info.states, az: info.az }});
}}

const sInput = document.getElementById('searchInput');
const sResults = document.getElementById('searchResults');

sInput.addEventListener('input', function() {{
  const q = this.value.trim().toLowerCase();
  if (q.length < 2) {{ sResults.style.display = 'none'; return; }}
  const matches = SI.filter(i => i.name.toLowerCase().includes(q) || i.detail.toLowerCase().includes(q)).slice(0, 20);
  if (!matches.length) {{
    sResults.innerHTML = '<div style="padding:10px 14px;color:rgba(58,42,8,0.35)">No results found</div>';
  }} else {{
    sResults.innerHTML = matches.map(m => '<div class="search-item" data-i="' + SI.indexOf(m) + '"><span class="name">' + m.name + '</span><span class="type type-' + m.type + '">' + m.type + '</span></div>').join('');
  }}
  sResults.style.display = 'block';
}});

sResults.addEventListener('click', function(e) {{
  const el = e.target.closest('.search-item'); if (!el) return;
  const entry = SI[parseInt(el.dataset.i)];
  sResults.style.display = 'none';
  sInput.value = entry.name;

  if (entry.type === 'lga') {{
    const ly = findLayer(lgaLayer, l => l.feature.properties.n === entry.props.n && l.feature.properties.s === entry.props.s);
    if (ly) map.fitBounds(ly.getBounds(), {{ maxZoom: 11, padding: [50,50] }});
    selectLGA(entry.props);
  }} else if (entry.type === 'district') {{
    const ly = findLayer(districtLayer, l => l.feature.properties.d === entry.did);
    if (ly) map.fitBounds(ly.getBounds(), {{ maxZoom: 10, padding: [50,50] }});
    selectDistrict(entry.did);
  }} else if (entry.type === 'state') {{
    const ly = findLayer(stateLayer, l => l.feature.properties.n === entry.sn);
    if (ly) map.fitBounds(ly.getBounds(), {{ maxZoom: 9, padding: [50,50] }});
    selectState(entry.sn);
  }} else if (entry.type === 'zone') {{
    const ly = findLayer(zoneLayer, l => l.feature.properties.z === entry.az);
    if (ly) map.fitBounds(ly.getBounds(), {{ maxZoom: 8, padding: [50,50] }});
    selectZone(entry.az);
  }}
}});

document.addEventListener('click', function(e) {{
  if (!e.target.closest('.search-panel')) sResults.style.display = 'none';
}});

function findLayer(group, pred) {{
  let found = null;
  group.eachLayer(l => {{ if (pred(l)) found = l; }});
  return found;
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    document.getElementById('infoPanel').style.display = 'none';
    sResults.style.display = 'none';
    clearHighlight();
  }}
}});
</script>
</body>
</html>
"""

with open('nigeria_2058_map.html', 'w', encoding='utf-8') as f:
    f.write(html)

import os
size_mb = os.path.getsize('nigeria_2058_map.html') / (1024*1024)
print(f"\nMap saved: nigeria_2058_map.html ({size_mb:.1f} MB)")
