import { useState, useMemo } from 'react';
import type { LGAInfo } from '../api/config';
import { ADMIN_ZONES } from '../types';

export type TargetScope = 'lga' | 'regional' | 'none';

interface Props {
  lgas: LGAInfo[];
  selectedLGAs: number[];
  selectedAZs: number[];
  scope: TargetScope;
  onChange: (lgas: number[], azs: number[]) => void;
}

export default function TargetSelector({ lgas, selectedLGAs, selectedAZs, scope, onChange }: Props) {
  const [search, setSearch] = useState('');
  const [expandedState, setExpandedState] = useState<string | null>(null);

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
