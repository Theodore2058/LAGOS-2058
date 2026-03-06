import { useState, useMemo } from 'react';
import type { LGAInfo, VotingDistrict } from '../api/config';
import { ADMIN_ZONES } from '../types';

export type TargetScope = 'lga' | 'regional' | 'district' | 'none';

interface Props {
  lgas: LGAInfo[];
  districts?: VotingDistrict[];
  selectedLGAs: number[];
  selectedAZs: number[];
  selectedDistricts: string[];
  scope: TargetScope;
  onChange: (lgas: number[], azs: number[]) => void;
  onDistrictChange?: (districts: string[]) => void;
}

export default function TargetSelector({ lgas, districts, selectedLGAs, selectedAZs, selectedDistricts, scope, onChange, onDistrictChange }: Props) {
  const [search, setSearch] = useState('');
  const [expandedState, setExpandedState] = useState<string | null>(null);
  const [expandedAz, setExpandedAz] = useState<number | null>(null);

  // Group LGAs by state
  const byState = useMemo(() => {
    const map = new Map<string, LGAInfo[]>();
    for (const lga of lgas) {
      const list = map.get(lga.state) ?? [];
      list.push(lga);
      map.set(lga.state, list);
    }
    return map;
  }, [lgas]);

  const states = useMemo(() => [...byState.keys()].sort(), [byState]);

  // Filtered states/LGAs for search
  const filteredStates = useMemo(() => {
    if (!search) return states;
    const q = search.toLowerCase();
    return states.filter(s => {
      if (s.toLowerCase().includes(q)) return true;
      return byState.get(s)?.some(l => l.name.toLowerCase().includes(q));
    });
  }, [states, byState, search]);

  if (scope === 'none') return null;

  // District scope: pick voting districts grouped by AZ
  if (scope === 'district' && districts && onDistrictChange) {
    const byAz = useMemo(() => {
      const map = new Map<number, VotingDistrict[]>();
      for (const d of districts) {
        const list = map.get(d.az) ?? [];
        list.push(d);
        map.set(d.az, list);
      }
      return map;
    }, [districts]);

    const toggleDistrict = (id: string) => {
      const next = selectedDistricts.includes(id)
        ? selectedDistricts.filter(d => d !== id)
        : [...selectedDistricts, id];
      onDistrictChange(next);
    };

    const toggleAzDistricts = (az: number) => {
      const azDistricts = byAz.get(az) ?? [];
      const azIds = azDistricts.map(d => d.district_id);
      const allSelected = azIds.every(id => selectedDistricts.includes(id));
      if (allSelected) {
        onDistrictChange(selectedDistricts.filter(id => !azIds.includes(id)));
      } else {
        onDistrictChange([...new Set([...selectedDistricts, ...azIds])]);
      }
    };

    const totalLGAs = selectedDistricts.reduce((sum, id) => {
      const d = districts.find(d => d.district_id === id);
      return sum + (d?.n_lgas ?? 0);
    }, 0);

    const filteredDistricts = useMemo(() => {
      if (!search) return districts;
      const q = search.toLowerCase();
      return districts.filter(d =>
        d.district_id.toLowerCase().includes(q) ||
        d.az_name.toLowerCase().includes(q) ||
        d.states.toLowerCase().includes(q) ||
        d.top_group.toLowerCase().includes(q) ||
        d.lga_names.some(n => n.toLowerCase().includes(q))
      );
    }, [districts, search]);

    return (
      <div>
        <label className="text-xs text-text-secondary block mb-1">
          Target Districts (empty = national) — {selectedDistricts.length > 0 ? `${selectedDistricts.length} district${selectedDistricts.length > 1 ? 's' : ''} (${totalLGAs} LGAs)` : 'none selected'}
        </label>

        {/* AZ quick-select row */}
        <div className="flex flex-wrap gap-1.5 mb-2">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(az => {
            const azDistricts = byAz.get(az) ?? [];
            if (azDistricts.length === 0) return null;
            const allSelected = azDistricts.every(d => selectedDistricts.includes(d.district_id));
            const someSelected = azDistricts.some(d => selectedDistricts.includes(d.district_id));
            return (
              <button key={az} onClick={() => toggleAzDistricts(az)} type="button"
                className={`px-2 py-1 text-xs rounded transition-colors duration-150 ${allSelected ? 'bg-accent text-bg-primary' : someSelected ? 'bg-accent/30 text-accent' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}
                title={`${azDistricts.length} districts in ${ADMIN_ZONES[az]}`}>
                {ADMIN_ZONES[az]?.split(' ')[0] ?? `AZ ${az}`}
              </button>
            );
          })}
        </div>

        {/* Search */}
        <input type="text" value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search districts, states, or ethnic groups..."
          className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1 text-xs mb-2 focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />

        {/* District list grouped by AZ */}
        <div className="max-h-56 overflow-y-auto space-y-0.5 border border-bg-tertiary/30 rounded-md p-1">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(az => {
            const azDistricts = (byAz.get(az) ?? []).filter(d => filteredDistricts.includes(d));
            if (azDistricts.length === 0) return null;
            const allSelected = azDistricts.every(d => selectedDistricts.includes(d.district_id));
            const someSelected = azDistricts.some(d => selectedDistricts.includes(d.district_id));
            const isExpanded = expandedAz === az;

            return (
              <div key={az}>
                <div className="flex items-center gap-1.5 py-0.5 px-1 rounded hover:bg-bg-tertiary/30 cursor-pointer"
                  onClick={() => setExpandedAz(isExpanded ? null : az)}>
                  <span className="text-[10px] text-text-secondary w-3">{isExpanded ? '\u25BC' : '\u25B6'}</span>
                  <button type="button" onClick={e => { e.stopPropagation(); toggleAzDistricts(az); }}
                    className={`w-3 h-3 rounded-sm border text-[8px] flex items-center justify-center shrink-0 transition-colors ${allSelected ? 'bg-accent border-accent text-bg-primary' : someSelected ? 'bg-accent/30 border-accent/50' : 'border-bg-quaternary/50'}`}>
                    {allSelected ? '\u2713' : someSelected ? '\u2212' : ''}
                  </button>
                  <span className="text-xs font-medium flex-1">{ADMIN_ZONES[az]}</span>
                  <span className="text-[10px] text-text-secondary">{azDistricts.filter(d => selectedDistricts.includes(d.district_id)).length}/{azDistricts.length}</span>
                </div>
                {isExpanded && (
                  <div className="pl-4 space-y-0">
                    {azDistricts.map(d => (
                      <div key={d.district_id}
                        className="flex items-center gap-1.5 py-0.5 px-1 rounded hover:bg-bg-tertiary/20 cursor-pointer"
                        onClick={() => toggleDistrict(d.district_id)}>
                        <div className={`w-3 h-3 rounded-sm border text-[8px] flex items-center justify-center shrink-0 transition-colors ${selectedDistricts.includes(d.district_id) ? 'bg-accent border-accent text-bg-primary' : 'border-bg-quaternary/50'}`}>
                          {selectedDistricts.includes(d.district_id) ? '\u2713' : ''}
                        </div>
                        <span className="text-xs font-mono text-accent/80">{d.district_id}</span>
                        <span className="text-[10px] text-text-secondary truncate flex-1" title={d.lga_names.join(', ')}>
                          {d.n_lgas} LGAs &middot; {d.top_group} {d.top_group_pct.toFixed(0)}% &middot; {d.states}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Regional: pick by AZ or state (converts to AZ list for backend)
  if (scope === 'regional') {
    const toggleAz = (az: number) => {
      const next = selectedAZs.includes(az)
        ? selectedAZs.filter(a => a !== az)
        : [...selectedAZs, az];
      onChange([], next);
    };

    const toggleState = (state: string) => {
      const stateLGAs = byState.get(state) ?? [];
      const stateIndices = stateLGAs.map(l => l.index);
      const allSelected = stateIndices.every(i => selectedLGAs.includes(i));
      if (allSelected) {
        onChange(selectedLGAs.filter(i => !stateIndices.includes(i)), selectedAZs);
      } else {
        const merged = [...new Set([...selectedLGAs, ...stateIndices])];
        onChange(merged, selectedAZs);
      }
    };

    return (
      <div>
        <label className="text-xs text-text-secondary block mb-1">Target Region (empty = national)</label>
        {/* AZ quick-select */}
        <div className="flex flex-wrap gap-1.5 mb-2">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(az => (
            <button key={az} onClick={() => toggleAz(az)} type="button"
              className={`px-2 py-1 text-xs rounded transition-colors duration-150 ${selectedAZs.includes(az) ? 'bg-accent text-bg-primary' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}>
              {ADMIN_ZONES[az]?.split(' ')[0] ?? `AZ ${az}`}
            </button>
          ))}
        </div>
        {/* State quick-select (collapsed by default) */}
        <details className="text-xs">
          <summary className="text-text-secondary cursor-pointer hover:text-text-primary transition-colors mb-1">
            Or select by state ({states.length} states)
          </summary>
          <div className="flex flex-wrap gap-1 mt-1 max-h-32 overflow-y-auto">
            {states.map(s => {
              const stateLGAs = byState.get(s) ?? [];
              const count = stateLGAs.length;
              const allSelected = stateLGAs.every(l => selectedLGAs.includes(l.index));
              return (
                <button key={s} onClick={() => toggleState(s)} type="button"
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors duration-150 ${allSelected ? 'bg-accent text-bg-primary' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}
                  title={`${count} LGAs`}>
                  {s}
                </button>
              );
            })}
          </div>
        </details>
      </div>
    );
  }

  // LGA scope: pick individual LGAs with search and state grouping
  const toggleLGA = (idx: number) => {
    const next = selectedLGAs.includes(idx)
      ? selectedLGAs.filter(i => i !== idx)
      : [...selectedLGAs, idx];
    onChange(next, []);
  };

  const toggleAllInState = (state: string) => {
    const stateLGAs = byState.get(state) ?? [];
    const stateIndices = stateLGAs.map(l => l.index);
    const allSelected = stateIndices.every(i => selectedLGAs.includes(i));
    if (allSelected) {
      onChange(selectedLGAs.filter(i => !stateIndices.includes(i)), []);
    } else {
      onChange([...new Set([...selectedLGAs, ...stateIndices])], []);
    }
  };

  const selectAZLGAs = (az: number) => {
    const azLGAs = lgas.filter(l => l.az === az).map(l => l.index);
    const allSelected = azLGAs.every(i => selectedLGAs.includes(i));
    if (allSelected) {
      onChange(selectedLGAs.filter(i => !azLGAs.includes(i)), []);
    } else {
      onChange([...new Set([...selectedLGAs, ...azLGAs])], []);
    }
  };

  return (
    <div>
      <label className="text-xs text-text-secondary block mb-1">
        Target LGAs (empty = national) — {selectedLGAs.length > 0 ? `${selectedLGAs.length} selected` : 'none selected'}
      </label>

      {/* AZ quick-select row */}
      <div className="flex flex-wrap gap-1.5 mb-2">
        {[1, 2, 3, 4, 5, 6, 7, 8].map(az => {
          const azLGAs = lgas.filter(l => l.az === az);
          const allSelected = azLGAs.length > 0 && azLGAs.every(l => selectedLGAs.includes(l.index));
          const someSelected = azLGAs.some(l => selectedLGAs.includes(l.index));
          return (
            <button key={az} onClick={() => selectAZLGAs(az)} type="button"
              className={`px-2 py-1 text-xs rounded transition-colors duration-150 ${allSelected ? 'bg-accent text-bg-primary' : someSelected ? 'bg-accent/30 text-accent' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}
              title={`Select all ${azLGAs.length} LGAs in ${ADMIN_ZONES[az]}`}>
              {ADMIN_ZONES[az]?.split(' ')[0] ?? `AZ ${az}`}
            </button>
          );
        })}
      </div>

      {/* Search */}
      <input type="text" value={search} onChange={e => setSearch(e.target.value)}
        placeholder="Search LGAs or states..."
        className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1 text-xs mb-2 focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />

      {/* State/LGA list */}
      <div className="max-h-48 overflow-y-auto space-y-0.5 border border-bg-tertiary/30 rounded-md p-1">
        {filteredStates.map(state => {
          const stateLGAs = byState.get(state) ?? [];
          const filtered = search
            ? stateLGAs.filter(l => l.name.toLowerCase().includes(search.toLowerCase()) || state.toLowerCase().includes(search.toLowerCase()))
            : stateLGAs;
          if (filtered.length === 0) return null;
          const allSelected = stateLGAs.every(l => selectedLGAs.includes(l.index));
          const someSelected = stateLGAs.some(l => selectedLGAs.includes(l.index));
          const isExpanded = expandedState === state;

          return (
            <div key={state}>
              <div className="flex items-center gap-1.5 py-0.5 px-1 rounded hover:bg-bg-tertiary/30 cursor-pointer"
                onClick={() => setExpandedState(isExpanded ? null : state)}>
                <span className="text-[10px] text-text-secondary w-3">{isExpanded ? '\u25BC' : '\u25B6'}</span>
                <button type="button" onClick={e => { e.stopPropagation(); toggleAllInState(state); }}
                  className={`w-3 h-3 rounded-sm border text-[8px] flex items-center justify-center shrink-0 transition-colors ${allSelected ? 'bg-accent border-accent text-bg-primary' : someSelected ? 'bg-accent/30 border-accent/50' : 'border-bg-quaternary/50'}`}>
                  {allSelected ? '\u2713' : someSelected ? '\u2212' : ''}
                </button>
                <span className="text-xs font-medium flex-1">{state}</span>
                <span className="text-[10px] text-text-secondary">{stateLGAs.filter(l => selectedLGAs.includes(l.index)).length}/{stateLGAs.length}</span>
              </div>
              {isExpanded && (
                <div className="pl-6 space-y-0">
                  {filtered.map(lga => (
                    <div key={lga.index}
                      className="flex items-center gap-1.5 py-0.5 px-1 rounded hover:bg-bg-tertiary/20 cursor-pointer"
                      onClick={() => toggleLGA(lga.index)}>
                      <div className={`w-3 h-3 rounded-sm border text-[8px] flex items-center justify-center shrink-0 transition-colors ${selectedLGAs.includes(lga.index) ? 'bg-accent border-accent text-bg-primary' : 'border-bg-quaternary/50'}`}>
                        {selectedLGAs.includes(lga.index) ? '\u2713' : ''}
                      </div>
                      <span className="text-xs">{lga.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
