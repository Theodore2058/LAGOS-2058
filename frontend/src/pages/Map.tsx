import { useState, useEffect, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { Layer, PathOptions } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Party, ElectionResults, LGAResult } from '../types';
import { fetchParties } from '../api/parties';
import { runElection } from '../api/election';

type ColorMode = 'winner' | 'turnout' | 'margin';

export default function MapPage() {
  const [parties, setParties] = useState<Party[]>([]);
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [results, setResults] = useState<ElectionResults | null>(null);
  const [colorMode, setColorMode] = useState<ColorMode>('winner');
  const [loading, setLoading] = useState(false);
  const [selectedLga, setSelectedLga] = useState<LGAResult | null>(null);

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
      console.error('Election failed:', e);
    }
    setLoading(false);
  };

  const getColor = useCallback((name: string) => parties.find(p => p.name === name)?.color ?? '#888', [parties]);

  const lgaMap = useMemo(() => {
    if (!results) return new Map<string, LGAResult>();
    const map = new Map<string, LGAResult>();
    for (const lga of results.lga_results) {
      map.set(lga.lga.toLowerCase().trim(), lga);
    }
    return map;
  }, [results]);

  const style = useCallback((feature?: GeoJSON.Feature): PathOptions => {
    if (!feature || !results) return { fillColor: '#334155', weight: 0.5, color: '#1e293b', fillOpacity: 0.7 };

    const lgaName = (feature.properties?.lga_name ?? feature.properties?.ADM2_EN ?? feature.properties?.NAME_2 ?? '').toLowerCase().trim();
    const lga = lgaMap.get(lgaName);

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
  }, [results, colorMode, getColor, lgaMap]);

  const onEachFeature = useCallback((feature: GeoJSON.Feature, layer: Layer) => {
    const lgaName = (feature.properties?.lga_name ?? feature.properties?.ADM2_EN ?? feature.properties?.NAME_2 ?? '');
    const lga = lgaMap.get(lgaName.toLowerCase().trim());

    let tooltip = lgaName;
    if (lga) {
      tooltip = `${lgaName}\nWinner: ${lga.winner}\nTurnout: ${(lga.turnout * 100).toFixed(1)}%`;
    }
    layer.bindTooltip(tooltip, { sticky: true, className: 'text-xs' });

    layer.on('click', () => {
      if (lga) setSelectedLga(lga);
    });
  }, [lgaMap]);

  return (
    <div className="flex h-full">
      <div className="flex-1 relative">
        {!geoData ? (
          <div className="flex items-center justify-center h-full text-text-secondary">Loading map data...</div>
        ) : (
          <MapContainer center={[9.05, 7.49]} zoom={6} style={{ height: '100%', width: '100%', background: '#0f172a' }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
              attribution='&copy; OpenStreetMap contributors &copy; CARTO'
            />
            <GeoJSON data={geoData} style={style} onEachFeature={onEachFeature} key={colorMode + (results ? 'r' : '')} />
          </MapContainer>
        )}

        {/* Controls overlay */}
        <div className="absolute top-4 right-4 bg-bg-secondary/90 rounded-lg p-3 border border-bg-tertiary z-[1000]">
          <div className="flex gap-2 mb-2">
            {(['winner', 'turnout', 'margin'] as ColorMode[]).map(mode => (
              <button key={mode} onClick={() => setColorMode(mode)}
                className={`px-2 py-1 text-xs rounded ${colorMode === mode ? 'bg-accent text-white' : 'bg-bg-tertiary'}`}>
                {mode}
              </button>
            ))}
          </div>
          <button onClick={handleRunElection} disabled={loading || parties.length < 2}
            className="w-full px-3 py-1.5 text-xs bg-accent rounded hover:bg-accent-hover text-white disabled:opacity-50">
            {loading ? 'Running...' : results ? 'Re-run Election' : 'Run Election for Map'}
          </button>
        </div>
      </div>

      {/* LGA detail panel */}
      {selectedLga && (
        <div className="w-72 bg-bg-secondary border-l border-bg-tertiary p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">{selectedLga.lga}</h3>
            <button onClick={() => setSelectedLga(null)} className="text-text-secondary hover:text-text-primary text-xs">x</button>
          </div>
          <div className="text-xs space-y-2">
            <div><span className="text-text-secondary">State:</span> {selectedLga.state}</div>
            <div><span className="text-text-secondary">AZ:</span> {selectedLga.az}</div>
            <div><span className="text-text-secondary">Turnout:</span> {(selectedLga.turnout * 100).toFixed(1)}%</div>
            <div><span className="text-text-secondary">Winner:</span>{' '}
              <span style={{ color: getColor(selectedLga.winner) }}>{selectedLga.winner}</span>
            </div>
            <div className="border-t border-bg-tertiary pt-2 mt-2">
              <div className="text-text-secondary mb-1">Vote Shares:</div>
              {Object.entries(selectedLga.vote_shares)
                .sort((a, b) => b[1] - a[1])
                .map(([name, share]) => (
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
      )}
    </div>
  );
}
