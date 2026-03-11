import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { Layer, PathOptions, Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { union as turfUnion } from '@turf/union';
import type { Party } from '../types';
import type { DistrictResultCompact, LGAResultCompact } from '../api/campaign';

/** Normalize LGA name for matching */
const normalizeLga = (name: string) =>
  name.toLowerCase().trim()
    .replace(/\s*\(.*?\)\s*/g, ' ')
    .replace(/[-/\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const LGA_ALIASES: Record<string, string> = {
  'aiyekire': 'gbonyin', 'atigbo': 'atisbo', 'barikin ladi': 'barkin ladi',
  'bekwara': 'bekwarra', 'birni kudu': 'birnin kudu',
  'birnin magaji': 'birnin magaji kiyaw', 'egbado north': 'yewa north',
  'egbado south': 'yewa south', 'ezinihitte': 'ezinihitte mbaise',
  'garum mallam': 'garun mallam', 'ifako ijaye': 'ifako ijaiye',
  'ilejemeji': 'ilejemeje', 'ilesha east': 'ilesa east',
  'ilesha west': 'ilesa west', 'isiukwuato': 'isuikwuato',
  'kiri kasamma': 'kiri kasama', 'markafi': 'makarfi', 'muya': 'munya',
  'obia akpor': 'obio akpor', 'olamabolo': 'olamaboro', 'omumma': 'omuma',
  'osisioma ngwa': 'osisioma', 'oturkpo': 'otukpo', 'shagamu': 'sagamu',
  'shomgom': 'shongom', 'tarmua': 'tarmuwa', 'unuimo': 'onuimo',
  'yenegoa': 'yenagoa', 'zango kataf': 'zangon kataf',
};

const resolveLga = (name: string): string => {
  const n = normalizeLga(name);
  return LGA_ALIASES[n] ?? n;
};

type ColorMode = 'district_winner' | 'lga_winner' | 'turnout' | 'margin';

interface Props {
  parties: Party[];
  districtResults: DistrictResultCompact[];
  lgaResults: LGAResultCompact[];
  seatCounts: Record<string, number>;
  nationalShares: Record<string, number>;
  totalSeats: number;
  nationalTurnout: number;
}

export default function DistrictResultsMap({
  parties, districtResults, lgaResults, seatCounts, nationalShares,
  totalSeats, nationalTurnout,
}: Props) {
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [colorMode, setColorMode] = useState<ColorMode>('district_winner');
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictResultCompact | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  useEffect(() => {
    fetch('/static/geojson/nga_lga_enriched.geojson')
      .then(r => r.json())
      .then(setGeoData)
      .catch(() => {
        fetch('/static/geojson/nga_admin2.geojson')
          .then(r => r.json())
          .then(setGeoData)
          .catch(e => console.error('Failed to load GeoJSON:', e));
      });
  }, []);

  const getColor = useCallback((name: string) =>
    parties.find(p => p.name === name)?.color ?? '#888', [parties]);

  // Build lookup maps
  const lgaMap = useMemo(() => {
    const map = new Map<string, LGAResultCompact>();
    for (const lga of lgaResults) map.set(normalizeLga(lga.lga), lga);
    return map;
  }, [lgaResults]);

  const districtMap = useMemo(() => {
    const map = new Map<string, DistrictResultCompact>();
    for (const d of districtResults) map.set(d.district_id, d);
    return map;
  }, [districtResults]);

  const findLga = useCallback((geoName: string) => lgaMap.get(resolveLga(geoName)), [lgaMap]);

  // Build district boundary GeoJSON — dissolve LGA polygons via turf union
  const districtBoundaries = useMemo(() => {
    if (!geoData) return null;
    const groups = new Map<string, GeoJSON.Feature[]>();
    for (const feature of geoData.features) {
      const did = feature.properties?.district_id ?? '';
      if (!did) continue;
      if (!groups.has(did)) groups.set(did, []);
      groups.get(did)!.push(feature);
    }
    const features: GeoJSON.Feature[] = [];
    for (const [did, lgas] of groups) {
      if (lgas.length === 1) {
        // Single LGA district — use as-is
        features.push({ ...lgas[0], properties: { district_id: did } });
      } else {
        // Union all LGA polygons to dissolve internal boundaries
        // turf v7 union takes a FeatureCollection
        try {
          const fc: GeoJSON.FeatureCollection<GeoJSON.Polygon | GeoJSON.MultiPolygon> = {
            type: 'FeatureCollection',
            features: lgas as GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon>[],
          };
          const merged = turfUnion(fc, { properties: { district_id: did } });
          if (merged) {
            features.push(merged);
          }
        } catch {
          // Fallback: MultiPolygon without dissolve
          const coordinates: GeoJSON.Position[][][][] = [];
          for (const f of lgas) {
            if (f.geometry.type === 'Polygon') {
              coordinates.push((f.geometry as GeoJSON.Polygon).coordinates as unknown as GeoJSON.Position[][][]);
            } else if (f.geometry.type === 'MultiPolygon') {
              for (const poly of (f.geometry as GeoJSON.MultiPolygon).coordinates) {
                coordinates.push(poly as unknown as GeoJSON.Position[][][]);
              }
            }
          }
          features.push({
            type: 'Feature',
            properties: { district_id: did },
            geometry: { type: 'MultiPolygon', coordinates },
          });
        }
      }
    }
    return { type: 'FeatureCollection', features } as GeoJSON.FeatureCollection;
  }, [geoData]);

  // Sorted parties by seats for legend
  const sortedParties = useMemo(() =>
    Object.entries(seatCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, seats]) => ({
        name,
        seats: Math.round(seats),
        share: nationalShares[name] ?? 0,
        color: getColor(name),
        // Count districts won
        districtsWon: districtResults.filter(d => d.winner === name).length,
      })),
    [seatCounts, nationalShares, getColor, districtResults]);

  const majorityLine = Math.ceil(totalSeats / 2);
  const maxSeats = sortedParties[0]?.seats ?? 1;

  const style = useCallback((feature?: GeoJSON.Feature): PathOptions => {
    if (!feature) return { fillColor: '#334155', weight: 0.5, color: '#1e293b', fillOpacity: 0.7 };

    const lgaRaw = feature.properties?.adm2_name ?? feature.properties?.lga_name ?? '';
    const districtId = feature.properties?.district_id ?? '';
    const lga = findLga(lgaRaw);
    const district = districtMap.get(districtId);

    if (colorMode === 'district_winner') {
      if (!district) return { fillColor: '#1e293b', weight: 0, color: 'transparent', fillOpacity: 0.4 };
      const winnerColor = getColor(district.winner);
      // Hide internal LGA borders — district outlines come from the overlay layer
      return {
        fillColor: winnerColor,
        weight: 0,
        color: 'transparent',
        fillOpacity: 0.8,
      };
    }

    if (!lga) return { fillColor: '#334155', weight: 0.3, color: '#1e293b', fillOpacity: 0.5 };

    if (colorMode === 'lga_winner') {
      return { fillColor: getColor(lga.winner), weight: 0.3, color: '#0f172a', fillOpacity: 0.85 };
    }

    if (colorMode === 'turnout') {
      const t = lga.turnout;
      const r = Math.round(255 * (1 - t));
      const g = Math.round(255 * t);
      return { fillColor: `rgb(${r}, ${g}, 80)`, weight: 0.3, color: '#0f172a', fillOpacity: 0.85 };
    }

    if (colorMode === 'margin') {
      const shares = Object.values(lga.vote_shares).sort((a, b) => b - a);
      const margin = shares.length >= 2 ? shares[0] - shares[1] : 1;
      const intensity = Math.min(margin * 5, 1);
      return { fillColor: `rgba(59, 130, 246, ${0.2 + intensity * 0.8})`, weight: 0.3, color: '#0f172a', fillOpacity: 0.85 };
    }

    return { fillColor: '#334155', weight: 0.3, color: '#0f172a', fillOpacity: 0.7 };
  }, [colorMode, findLga, districtMap, getColor, selectedDistrict]);

  const onEachFeature = useCallback((feature: GeoJSON.Feature, layer: Layer) => {
    const lgaName = feature.properties?.adm2_name ?? '';
    const stateName = feature.properties?.adm1_name ?? '';
    const districtId = feature.properties?.district_id ?? '';
    const lga = findLga(lgaName);
    const district = districtMap.get(districtId);

    if (colorMode === 'district_winner' && district) {
      const top3 = Object.entries(district.vote_shares).sort((a, b) => b[1] - a[1]).slice(0, 4);
      const maxShare = top3[0]?.[1] ?? 1;
      const barsHtml = top3.map(([name, share]) => {
        const color = getColor(name);
        const pct = (share * 100).toFixed(1);
        const barW = Math.round((share / maxShare) * 100);
        const seats = district.seat_allocation[name] ?? 0;
        return `<div style="display:flex;align-items:center;gap:4px;margin:1px 0"><span style="color:${color};font-weight:600;width:32px;font-size:10px">${name}</span><div style="flex:1;height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:${barW}%;background:${color};border-radius:3px"></div></div><span style="font-size:10px;width:36px;text-align:right">${pct}%</span><span style="font-size:10px;width:20px;text-align:right;font-weight:700;color:${color}">${seats}</span></div>`;
      }).join('');
      const html = `<div style="min-width:180px"><div style="font-weight:700;font-size:11px;margin-bottom:1px">${districtId}</div><div style="font-size:9px;color:#8b9bb4;margin-bottom:3px">${district.az_name} · ${district.seats} seats</div><div style="font-size:9px;color:#64748b;margin-bottom:2px">${lgaName}, ${stateName}</div>${barsHtml}</div>`;
      layer.bindTooltip(html, { sticky: true, className: 'map-tooltip' });
    } else if (lga) {
      const top3 = Object.entries(lga.vote_shares).sort((a, b) => b[1] - a[1]).slice(0, 3);
      const maxShare = top3[0]?.[1] ?? 1;
      const barsHtml = top3.map(([name, share]) => {
        const color = getColor(name);
        const pct = (share * 100).toFixed(1);
        const barW = Math.round((share / maxShare) * 100);
        return `<div style="display:flex;align-items:center;gap:4px;margin:1px 0"><span style="color:${color};font-weight:600;width:32px;font-size:10px">${name}</span><div style="flex:1;height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:${barW}%;background:${color};border-radius:3px"></div></div><span style="font-size:10px;width:36px;text-align:right">${pct}%</span></div>`;
      }).join('');
      const html = `<div style="min-width:140px"><div style="font-weight:700;font-size:11px;margin-bottom:2px">${lgaName}</div>${stateName ? `<div style="font-size:9px;color:#8b9bb4;margin-bottom:3px">${stateName}${districtId ? ` · ${districtId}` : ''}</div>` : ''}${barsHtml}</div>`;
      layer.bindTooltip(html, { sticky: true, className: 'map-tooltip' });
    } else {
      layer.bindTooltip(`<div style="font-size:11px">${lgaName}<br><span style="font-size:9px;color:#64748b">No data</span></div>`, { sticky: true, className: 'map-tooltip' });
    }

    layer.on('click', () => {
      if (district) setSelectedDistrict(prev => prev?.district_id === districtId ? null : district);
    });
  }, [findLga, districtMap, getColor, colorMode]);

  if (!geoData) {
    return (
      <div className="flex items-center justify-center h-96 bg-bg-secondary rounded-lg border border-bg-tertiary/50">
        <div className="text-center">
          <div className="animate-spin w-6 h-6 border-2 border-accent border-t-transparent rounded-full mx-auto mb-2" />
          <p className="text-xs text-text-secondary">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary rounded-lg border border-bg-tertiary/50 overflow-hidden">
      {/* German-style results legend bar */}
      <div className="px-4 py-3 border-b border-bg-tertiary/50">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-bold tracking-wide">
            Election Results
            <span className="text-text-secondary font-normal ml-2 text-xs">
              {totalSeats} seats · 150 districts · {(nationalTurnout * 100).toFixed(1)}% turnout
            </span>
          </h3>
          <div className="flex gap-1">
            {(['district_winner', 'lga_winner', 'turnout', 'margin'] as ColorMode[]).map(mode => (
              <button key={mode} onClick={() => setColorMode(mode)}
                className={`px-2 py-0.5 text-[10px] rounded font-medium transition-colors ${
                  colorMode === mode ? 'bg-accent text-bg-primary' : 'bg-bg-tertiary hover:bg-bg-quaternary/50 text-text-secondary'
                }`}>
                {mode === 'district_winner' ? 'Districts' : mode === 'lga_winner' ? 'LGAs' : mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Party result bars — Bundestag style */}
        <div className="space-y-1">
          {sortedParties.filter(p => p.seats > 0).map(p => (
            <div key={p.name} className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: p.color }} />
              <span className="text-[11px] font-semibold w-12 shrink-0" style={{ color: p.color }}>{p.name}</span>
              <div className="flex-1 flex items-center gap-1.5 min-w-0">
                {/* Vote share bar */}
                <div className="flex-1 h-4 bg-bg-tertiary/50 rounded-sm overflow-hidden relative">
                  <div className="h-full rounded-sm transition-all" style={{
                    width: `${(p.share / (sortedParties[0]?.share || 1)) * 100}%`,
                    backgroundColor: p.color,
                    opacity: 0.7,
                  }} />
                  <span className="absolute inset-y-0 left-1.5 flex items-center text-[9px] font-mono font-bold text-white drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)]">
                    {(p.share * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <span className="text-[10px] font-mono text-text-secondary w-6 text-right shrink-0" title="Districts won">
                {p.districtsWon}
              </span>
              <span className="text-[11px] font-mono font-bold w-8 text-right shrink-0" style={{ color: p.color }}>
                {p.seats}
              </span>
            </div>
          ))}
        </div>

        {/* Column labels */}
        <div className="flex items-center gap-2 mt-1 text-[8px] text-text-secondary/50 uppercase tracking-wider">
          <span className="w-2.5" />
          <span className="w-12">Party</span>
          <span className="flex-1">Vote Share</span>
          <span className="w-6 text-right">Dist</span>
          <span className="w-8 text-right">Seats</span>
        </div>

        {/* Majority line */}
        <div className="flex items-center gap-2 mt-1.5 pt-1.5 border-t border-bg-tertiary/30">
          <span className="text-[9px] text-text-secondary">
            Majority: {majorityLine} seats
          </span>
          {sortedParties[0] && sortedParties[0].seats >= majorityLine && (
            <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-success/10 text-success">
              {sortedParties[0].name} majority
            </span>
          )}
          {sortedParties[0] && sortedParties[0].seats < majorityLine && (
            <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-warning/10 text-warning">
              No majority — coalition needed
            </span>
          )}
        </div>
      </div>

      {/* Map */}
      <div className="relative" style={{ height: 480 }}>
        <MapContainer
          ref={mapRef}
          center={[9.05, 7.49]}
          zoom={6}
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
            attribution='&copy; OSM &copy; CARTO'
          />
          {/* District mode: render merged district polygons only (no LGA boundaries) */}
          {colorMode === 'district_winner' && districtBoundaries ? (
            <GeoJSON
              data={districtBoundaries}
              style={(feature) => {
                const did = feature?.properties?.district_id ?? '';
                const district = districtMap.get(did);
                if (!district) return { fillColor: '#1e293b', weight: 0.5, color: '#0f172a', fillOpacity: 0.4 };
                const isSelected = selectedDistrict?.district_id === did;
                return {
                  fillColor: getColor(district.winner),
                  fillOpacity: isSelected ? 0.95 : 0.85,
                  weight: isSelected ? 2.5 : 0.6,
                  color: isSelected ? '#fff' : 'rgba(15,23,42,0.5)',
                  opacity: 1,
                };
              }}
              onEachFeature={(feature, layer) => {
                const did = feature.properties?.district_id ?? '';
                const district = districtMap.get(did);
                if (district) {
                  const top3 = Object.entries(district.vote_shares).sort((a, b) => b[1] - a[1]).slice(0, 4);
                  const maxShare = top3[0]?.[1] ?? 1;
                  const barsHtml = top3.map(([name, share]) => {
                    const color = getColor(name);
                    const pct = (share * 100).toFixed(1);
                    const barW = Math.round((share / maxShare) * 100);
                    const seats = district.seat_allocation[name] ?? 0;
                    return `<div style="display:flex;align-items:center;gap:4px;margin:1px 0"><span style="color:${color};font-weight:600;width:32px;font-size:10px">${name}</span><div style="flex:1;height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:${barW}%;background:${color};border-radius:3px"></div></div><span style="font-size:10px;width:36px;text-align:right">${pct}%</span><span style="font-size:10px;width:20px;text-align:right;font-weight:700;color:${color}">${seats}</span></div>`;
                  }).join('');
                  layer.bindTooltip(
                    `<div style="min-width:180px"><div style="font-weight:700;font-size:11px;margin-bottom:1px">${did}</div><div style="font-size:9px;color:#8b9bb4;margin-bottom:3px">${district.az_name} · ${district.seats} seats</div>${barsHtml}</div>`,
                    { sticky: true, className: 'map-tooltip' }
                  );
                }
                layer.on('click', () => {
                  if (district) setSelectedDistrict(prev => prev?.district_id === did ? null : district);
                });
              }}
              key={'districts-' + (selectedDistrict?.district_id ?? '')}
            />
          ) : (
            /* LGA mode / turnout / margin: render individual LGA polygons */
            <GeoJSON
              data={geoData}
              style={style}
              onEachFeature={onEachFeature}
              key={colorMode + (selectedDistrict?.district_id ?? '')}
            />
          )}
        </MapContainer>

        {/* District detail panel (when a district is clicked) */}
        {selectedDistrict && (
          <div className="absolute top-3 right-3 w-64 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-3 border border-bg-tertiary/50 z-[1000] shadow-lg shadow-black/20">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-bold">{selectedDistrict.district_id}</h4>
              <button onClick={() => setSelectedDistrict(null)}
                className="text-text-secondary hover:text-text-primary p-0.5 rounded hover:bg-bg-tertiary/50">
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="text-[10px] text-text-secondary mb-2">
              {selectedDistrict.az_name} · {selectedDistrict.seats} seats
            </div>
            <div className="space-y-1">
              {Object.entries(selectedDistrict.vote_shares)
                .sort((a, b) => b[1] - a[1])
                .filter(([, v]) => v > 0.01)
                .slice(0, 8)
                .map(([name, share]) => {
                  const color = getColor(name);
                  const seats = selectedDistrict.seat_allocation[name] ?? 0;
                  return (
                    <div key={name} className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: color }} />
                      <span className="text-[10px] font-mono w-10" style={{ color }}>{name}</span>
                      <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
                        <div className="h-1.5 rounded-full" style={{
                          width: `${share * 100}%`,
                          backgroundColor: color,
                        }} />
                      </div>
                      <span className="text-[10px] w-10 text-right font-mono">{(share * 100).toFixed(1)}%</span>
                      {seats > 0 && (
                        <span className="text-[10px] w-4 text-right font-bold font-mono" style={{ color }}>{seats}</span>
                      )}
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* Turnout Legend */}
        {colorMode === 'turnout' && (
          <div className="absolute bottom-3 right-3 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-2 border border-bg-tertiary/50 z-[1000]">
            <div className="text-[9px] text-text-secondary uppercase tracking-wider mb-1 font-medium">Turnout</div>
            <div className="flex items-center gap-1 text-[10px]">
              <span className="text-text-secondary">Low</span>
              <div className="w-20 h-2.5 rounded-sm" style={{ background: 'linear-gradient(to right, rgb(255,0,80), rgb(128,128,80), rgb(0,255,80))' }} />
              <span className="text-text-secondary">High</span>
            </div>
          </div>
        )}

        {/* Margin Legend */}
        {colorMode === 'margin' && (
          <div className="absolute bottom-3 right-3 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-2 border border-bg-tertiary/50 z-[1000]">
            <div className="text-[9px] text-text-secondary uppercase tracking-wider mb-1 font-medium">Win Margin</div>
            <div className="flex items-center gap-1 text-[10px]">
              <span className="text-text-secondary">Close</span>
              <div className="w-20 h-2.5 rounded-sm" style={{ background: 'linear-gradient(to right, rgba(59,130,246,0.2), rgba(59,130,246,1))' }} />
              <span className="text-text-secondary">Safe</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
