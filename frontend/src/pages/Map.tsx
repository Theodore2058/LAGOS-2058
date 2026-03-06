import { useState, useEffect, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { Layer, PathOptions } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Party, ElectionResults, LGAResult } from '../types';
import { fetchParties } from '../api/parties';
import { runElection } from '../api/election';

type ColorMode = 'winner' | 'turnout' | 'margin';

/** Normalize LGA name for matching: lowercase, trim, collapse hyphens/slashes/spaces, strip parentheticals */
const normalizeLga = (name: string) =>
  name.toLowerCase().trim()
    .replace(/\s*\(.*?\)\s*/g, ' ')    // strip parenthetical (gbonyin)
    .replace(/[-/\s]+/g, ' ')           // collapse hyphens/slashes/spaces
    .replace(/\s+/g, ' ')
    .trim();

/**
 * Alias map for LGA names that differ between GeoJSON (adm2_name) and election data (LGA Name).
 * Keys are normalized GeoJSON names, values are normalized election-data names.
 */
const LGA_ALIASES: Record<string, string> = {
  'aiyekire': 'gbonyin',
  'atigbo': 'atisbo',
  'barikin ladi': 'barkin ladi',
  'bekwara': 'bekwarra',
  'birni kudu': 'birnin kudu',
  'birnin magaji': 'birnin magaji kiyaw',
  'egbado north': 'yewa north',
  'egbado south': 'yewa south',
  'ezinihitte': 'ezinihitte mbaise',
  'garum mallam': 'garun mallam',
  'ibeju lekki': 'ibeju lekki',
  'ifako ijaye': 'ifako ijaiye',
  'ile oluji okeigbo': 'ile oluji okeigbo',
  'ilejemeji': 'ilejemeje',
  'ilesha east': 'ilesa east',
  'ilesha west': 'ilesa west',
  'isiukwuato': 'isuikwuato',
  'kiri kasamma': 'kiri kasama',
  'markafi': 'makarfi',
  'muya': 'munya',
  'obia akpor': 'obio akpor',
  'olamabolo': 'olamaboro',
  'omumma': 'omuma',
  'osisioma ngwa': 'osisioma',
  'oturkpo': 'otukpo',
  'shagamu': 'sagamu',
  'shomgom': 'shongom',
  'tarmua': 'tarmuwa',
  'unuimo': 'onuimo',
  'yenegoa': 'yenagoa',
  'zango kataf': 'zangon kataf',
};

/** Resolve a GeoJSON LGA name to match election-data naming */
const resolveLga = (name: string): string => {
  const n = normalizeLga(name);
  return LGA_ALIASES[n] ?? n;
};

export default function MapPage() {
  const [parties, setParties] = useState<Party[]>([]);
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [results, setResults] = useState<ElectionResults | null>(null);
  const [colorMode, setColorMode] = useState<ColorMode>('winner');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedLga, setSelectedLga] = useState<LGAResult | null>(null);
  const [lgaSearch, setLgaSearch] = useState('');

  useEffect(() => {
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
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

  const handleRunElection = async () => {
    if (parties.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runElection({
        params: {
          q: 0.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, scale: 1.5,
          tau_0: 4.5, tau_1: 0.3, tau_2: 0.5, beta_econ: 0.3,
          kappa: 200, sigma_national: 0.10, sigma_regional: 0.15,
          sigma_turnout: 0.0, sigma_turnout_regional: 0.0,
        },
        parties,
        n_monte_carlo: 10,
        seed: 42,
      });
      setResults(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Election failed');
    }
    setLoading(false);
  };

  const getColor = useCallback((name: string) => parties.find(p => p.name === name)?.color ?? '#888', [parties]);

  const lgaMap = useMemo(() => {
    if (!results) return new Map<string, LGAResult>();
    const map = new Map<string, LGAResult>();
    for (const lga of results.lga_results) {
      map.set(normalizeLga(lga.lga), lga);
    }
    return map;
  }, [results]);

  /** Look up election result for a GeoJSON LGA name */
  const findLga = useCallback((geoName: string) => lgaMap.get(resolveLga(geoName)), [lgaMap]);

  // Competitive & search
  const competitiveLgas = useMemo(() => {
    if (!results) return 0;
    return results.lga_results.filter(lga => {
      const shares = Object.values(lga.vote_shares).sort((a, b) => b - a);
      return shares.length >= 2 && (shares[0] - shares[1]) < 0.05;
    }).length;
  }, [results]);

  const searchResults = useMemo(() => {
    if (!lgaSearch.trim() || !results) return [];
    const q = lgaSearch.toLowerCase();
    return results.lga_results
      .filter(lga => lga.lga.toLowerCase().includes(q) || lga.state.toLowerCase().includes(q))
      .sort((a, b) => a.lga.localeCompare(b.lga))
      .slice(0, 8);
  }, [lgaSearch, results]);

  const style = useCallback((feature?: GeoJSON.Feature): PathOptions => {
    if (!feature || !results) return { fillColor: '#334155', weight: 0.5, color: '#1e293b', fillOpacity: 0.7 };

    const lgaRaw = feature.properties?.adm2_name ?? feature.properties?.lga_name ?? feature.properties?.ADM2_EN ?? feature.properties?.NAME_2 ?? '';
    const lga = findLga(lgaRaw);

    if (!lga) return { fillColor: '#334155', weight: 0.5, color: '#1e293b', fillOpacity: 0.5 };

    let fillColor = '#334155';
    if (colorMode === 'winner') {
      fillColor = getColor(lga.winner);
    } else if (colorMode === 'turnout') {
      const t = lga.turnout;
      const r = Math.round(255 * (1 - t));
      const g = Math.round(255 * t);
      fillColor = `rgb(${r}, ${g}, 80)`;
    } else if (colorMode === 'margin') {
      const shares = Object.values(lga.vote_shares).sort((a, b) => b - a);
      const margin = shares.length >= 2 ? shares[0] - shares[1] : 1;
      const intensity = Math.min(margin * 5, 1);
      fillColor = `rgba(59, 130, 246, ${0.2 + intensity * 0.8})`;
    }

    return { fillColor, weight: 0.3, color: '#0f172a', fillOpacity: 0.85 };
  }, [results, colorMode, getColor, findLga]);

  const onEachFeature = useCallback((feature: GeoJSON.Feature, layer: Layer) => {
    const lgaName = (feature.properties?.adm2_name ?? feature.properties?.lga_name ?? feature.properties?.ADM2_EN ?? feature.properties?.NAME_2 ?? '');
    const stateName = feature.properties?.adm1_name ?? feature.properties?.ADM1_EN ?? '';
    const lga = findLga(lgaName);

    if (lga) {
      const top3 = Object.entries(lga.vote_shares).sort((a, b) => b[1] - a[1]).slice(0, 3);
      const maxShare = top3[0]?.[1] ?? 1;
      const barsHtml = top3.map(([name, share]) => {
        const color = parties.find(p => p.name === name)?.color ?? '#888';
        const pct = (share * 100).toFixed(1);
        const barW = Math.round((share / maxShare) * 100);
        return `<div style="display:flex;align-items:center;gap:4px;margin:1px 0"><span style="color:${color};font-weight:600;width:32px;font-size:10px">${name}</span><div style="flex:1;height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:${barW}%;background:${color};border-radius:3px"></div></div><span style="font-size:10px;width:36px;text-align:right">${pct}%</span></div>`;
      }).join('');
      const html = `<div style="min-width:140px"><div style="font-weight:700;font-size:11px;margin-bottom:2px">${lgaName}</div>${stateName ? `<div style="font-size:9px;color:#8b9bb4;margin-bottom:4px">${stateName}</div>` : ''}<div style="font-size:10px;color:#8b9bb4;margin-bottom:3px">Turnout: ${(lga.turnout * 100).toFixed(1)}%</div>${barsHtml}</div>`;
      layer.bindTooltip(html, { sticky: true, className: 'map-tooltip' });
    } else {
      layer.bindTooltip(`<div style="font-size:11px">${lgaName}${stateName ? `<br><span style="font-size:9px;color:#8b9bb4">${stateName}</span>` : ''}<br><span style="font-size:9px;color:#64748b">No election data</span></div>`, { sticky: true, className: 'map-tooltip' });
    }

    layer.on('click', () => {
      if (lga) setSelectedLga(lga);
    });
  }, [findLga, parties]);

  return (
    <div className="flex h-full">
      <div className="flex-1 relative">
        {!geoData ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-sm text-text-secondary">Loading map data...</p>
            </div>
          </div>
        ) : (
          <MapContainer center={[9.05, 7.49]} zoom={6} style={{ height: '100%', width: '100%', background: '#0f172a' }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
              attribution='&copy; OpenStreetMap contributors &copy; CARTO'
            />
            <GeoJSON data={geoData} style={style} onEachFeature={onEachFeature} key={colorMode + (results ? 'r' : '')} />
          </MapContainer>
        )}

        {/* Error overlay */}
        {error && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1001] bg-danger/20 border border-danger/30 backdrop-blur-sm text-danger px-4 py-2 rounded-lg text-sm shadow-lg flex items-center gap-2">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-danger/60 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors shrink-0" aria-label="Dismiss error">
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        {/* Loading overlay */}
        {loading && (
          <div className="absolute inset-0 bg-bg-primary/40 backdrop-blur-sm z-[1001] flex items-center justify-center">
            <div className="bg-bg-secondary/95 rounded-lg p-4 border border-bg-tertiary/50 text-center shadow-lg">
              <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-2" />
              <p className="text-xs text-text-secondary">Running election...</p>
            </div>
          </div>
        )}

        {/* Controls overlay */}
        <div className="absolute top-4 right-4 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-3 border border-bg-tertiary/50 z-[1000] shadow-lg shadow-black/20">
          <div className="flex gap-1.5 mb-2.5">
            {(['winner', 'turnout', 'margin'] as ColorMode[]).map(mode => (
              <button key={mode} onClick={() => setColorMode(mode)}
                className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${colorMode === mode ? 'bg-accent text-bg-primary shadow-sm shadow-accent/30' : 'bg-bg-tertiary hover:bg-bg-quaternary/50'}`}>
                {mode}
              </button>
            ))}
          </div>
          <button onClick={handleRunElection} disabled={loading || parties.length < 2}
            className="w-full px-3 py-1.5 text-xs bg-accent rounded-md hover:bg-accent-hover text-bg-primary font-medium disabled:opacity-50 shadow-sm shadow-accent/20 btn-accent">
            {loading ? 'Running...' : results ? 'Re-run Election' : 'Run Election for Map'}
          </button>
          {results && (
            <div className="mt-2 space-y-1 text-[10px] text-text-secondary">
              <div className="relative mb-1.5">
                <svg className="absolute left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-text-secondary/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
                <input value={lgaSearch} onChange={e => setLgaSearch(e.target.value)} placeholder="Search LGA or state..."
                  className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded px-2 pl-6 py-1 text-[10px] focus:border-accent transition-colors placeholder:text-text-secondary/30" />
                {lgaSearch && (
                  <button onClick={() => setLgaSearch('')} className="absolute right-1 top-1/2 -translate-y-1/2 text-text-secondary/40 hover:text-text-secondary">
                    <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                  </button>
                )}
              </div>
              {searchResults.length > 0 && (
                <div className="space-y-0.5 mb-1.5 max-h-32 overflow-y-auto">
                  {searchResults.map(lga => (
                    <button key={lga.lga} onClick={() => { setSelectedLga(lga); setLgaSearch(''); }}
                      className="w-full flex items-center gap-1.5 py-0.5 px-1 rounded hover:bg-bg-tertiary/50 text-left transition-colors">
                      <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: getColor(lga.winner) }} />
                      <span className="flex-1 truncate">{lga.lga}</span>
                      <span className="text-text-secondary/40">{lga.state}</span>
                    </button>
                  ))}
                </div>
              )}
              <div>{lgaMap.size}/{results.lga_results.length} LGAs mapped</div>
              <div>Turnout: {(results.national_turnout * 100).toFixed(1)}% | ENP: {results.enp.toFixed(2)}</div>
              {competitiveLgas > 0 && (
                <div className="text-warning">{competitiveLgas} swing LGAs (&lt;5pp margin)</div>
              )}
              <div className="border-t border-bg-tertiary/40 pt-1.5 mt-1.5 space-y-0.5">
                {Object.entries(results.national_vote_shares)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 5)
                  .map(([name, share]) => (
                    <div key={name} className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: getColor(name) }} />
                      <span className="w-10 font-mono font-medium" style={{ color: getColor(name) }}>{name}</span>
                      <div className="flex-1 bg-bg-tertiary rounded-full h-1 overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${share * 100 * 3}%`, backgroundColor: getColor(name), maxWidth: '100%' }} />
                      </div>
                      <span className="w-10 text-right font-mono">{(share * 100).toFixed(1)}%</span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        {/* Winner Legend */}
        {results && colorMode === 'winner' && (
          <div className="absolute bottom-4 right-4 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-2.5 border border-bg-tertiary/50 z-[1000] shadow-lg shadow-black/20 max-h-48 overflow-y-auto">
            <div className="text-[9px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">LGAs Won</div>
            {Object.entries(
              results.lga_results.reduce<Record<string, number>>((acc, lga) => {
                acc[lga.winner] = (acc[lga.winner] ?? 0) + 1;
                return acc;
              }, {})
            ).sort((a, b) => b[1] - a[1]).map(([name, count]) => (
              <div key={name} className="flex items-center gap-1.5 py-0.5 text-[10px]">
                <div className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: getColor(name) }} />
                <span className="font-medium w-10" style={{ color: getColor(name) }}>{name}</span>
                <span className="text-text-secondary">{count}</span>
              </div>
            ))}
          </div>
        )}

        {/* Turnout Legend */}
        {results && colorMode === 'turnout' && (
          <div className="absolute bottom-4 right-4 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-2.5 border border-bg-tertiary/50 z-[1000] shadow-lg shadow-black/20">
            <div className="text-[9px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Turnout</div>
            <div className="flex items-center gap-1 text-[10px]">
              <span className="text-text-secondary">Low</span>
              <div className="w-24 h-3 rounded-sm" style={{ background: 'linear-gradient(to right, rgb(255,0,80), rgb(128,128,80), rgb(0,255,80))' }} />
              <span className="text-text-secondary">High</span>
            </div>
          </div>
        )}

        {/* Margin Legend */}
        {results && colorMode === 'margin' && (
          <div className="absolute bottom-4 right-4 bg-bg-secondary/95 backdrop-blur-sm rounded-lg p-2.5 border border-bg-tertiary/50 z-[1000] shadow-lg shadow-black/20">
            <div className="text-[9px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Win Margin</div>
            <div className="flex items-center gap-1 text-[10px]">
              <span className="text-text-secondary">Close</span>
              <div className="w-24 h-3 rounded-sm" style={{ background: 'linear-gradient(to right, rgba(59,130,246,0.2), rgba(59,130,246,1))' }} />
              <span className="text-text-secondary">Safe</span>
            </div>
          </div>
        )}
      </div>

      {/* LGA detail panel */}
      {selectedLga && (() => {
        const shares = Object.entries(selectedLga.vote_shares).sort((a, b) => b[1] - a[1]);
        const winnerShare = shares[0]?.[1] ?? 0;
        const runnerUpShare = shares[1]?.[1] ?? 0;
        const margin = winnerShare - runnerUpShare;
        const competitive = margin < 0.05;
        return (
          <div className="w-72 bg-bg-secondary border-l border-bg-tertiary p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold">{selectedLga.lga}</h3>
              <button onClick={() => setSelectedLga(null)} className="text-text-secondary hover:text-text-primary p-1 rounded hover:bg-bg-tertiary/50 transition-colors" aria-label="Close LGA detail">
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="text-xs space-y-2">
              <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                <div><span className="text-text-secondary">State:</span> {selectedLga.state}</div>
                <div><span className="text-text-secondary">AZ:</span> {selectedLga.az}</div>
                <div><span className="text-text-secondary">Turnout:</span> {(selectedLga.turnout * 100).toFixed(1)}%</div>
                <div>
                  <span className="text-text-secondary">Margin:</span>{' '}
                  <span className={competitive ? 'text-warning font-medium' : ''}>{(margin * 100).toFixed(1)}pp</span>
                  {competitive && <span className="text-warning text-[9px] ml-0.5">swing</span>}
                </div>
              </div>
              <div className="bg-bg-tertiary/30 rounded-md p-2 flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(selectedLga.winner) }} />
                <div>
                  <span className="font-semibold" style={{ color: getColor(selectedLga.winner) }}>{selectedLga.winner}</span>
                  <span className="text-text-secondary ml-1">wins with {(winnerShare * 100).toFixed(1)}%</span>
                </div>
              </div>
              {shares[1] && (
                <div className="text-[10px] text-text-secondary">
                  Runner-up: <span style={{ color: getColor(shares[1][0]) }}>{shares[1][0]}</span> ({(runnerUpShare * 100).toFixed(1)}%)
                </div>
              )}
              <div className="border-t border-bg-tertiary pt-2 mt-2">
                <div className="text-text-secondary mb-1">All Parties:</div>
                {shares.map(([name, share]) => (
                  <div key={name} className="flex items-center gap-2 py-0.5">
                    <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: getColor(name) }} />
                    <span className="w-10 font-mono">{name}</span>
                    <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
                      <div className="h-1.5 rounded-full" style={{ width: `${share * 100}%`, backgroundColor: getColor(name) }} />
                    </div>
                    <span className="w-12 text-right">{(share * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
