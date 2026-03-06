import { useState, useEffect, useMemo } from 'react';
import type { Party } from '../types';
import PositionSlider from './PositionSlider';
import { ISSUE_DESCRIPTIONS } from '../utils/issueDescriptions';

interface Props {
  party: Party;
  issueNames: string[];
  ethnicGroups: string[];
  religiousGroups: string[];
  adminZones: { id: number; name: string }[];
  onSave: (party: Party) => void;
  onCancel: () => void;
  isNew: boolean;
}

const AZ_IDS = [1, 2, 3, 4, 5, 6, 7, 8];

const COLOR_PRESETS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4', '#f97316', '#14b8a6', '#6366f1',
  '#84cc16', '#e11d48', '#0ea5e9', '#a855f7',
];

const POSITION_PRESETS: { label: string; positions: number[] }[] = [
  { label: 'Centrist', positions: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] },
  { label: 'Progressive', positions: [-2,-1,1,2,-3,2,-2,1,2,-1,3,2,-1,2,-2,1,2,-1,3,1,-2,2,1,-1,2,1,-1,2] },
  { label: 'Conservative', positions: [3,2,-1,-2,3,-2,3,-1,-2,2,-3,-1,2,-2,3,-1,-2,2,-3,-1,3,-2,-1,2,-2,-1,2,-2] },
  { label: 'Islamist', positions: [5,3,-2,-3,4,-3,4,-2,-3,3,-4,-2,3,-3,4,-2,-3,3,-4,-2,4,-3,-2,3,-3,-2,3,-3] },
];

export default function PartyForm({ party, issueNames, ethnicGroups, religiousGroups, adminZones, onSave, onCancel, isNew }: Props) {
  const [form, setForm] = useState<Party>({ ...party });
  const [positionsOpen, setPositionsOpen] = useState(true);
  const [strongholdsOpen, setStrongholdsOpen] = useState(true);

  useEffect(() => {
    setForm({ ...party });
  }, [party]);

  const isDirty = useMemo(() => {
    return JSON.stringify(form) !== JSON.stringify(party);
  }, [form, party]);

  const nameValid = form.name.trim().length > 0;

  const updatePosition = (idx: number, val: number) => {
    const newPos = [...form.positions];
    newPos[idx] = Math.round(val * 10) / 10;
    setForm({ ...form, positions: newPos });
  };

  const toggleStronghold = (azId: number) => {
    const key = String(azId);
    const current = form.regional_strongholds || {};
    if (key in current) {
      const { [key]: _, ...rest } = current;
      setForm({ ...form, regional_strongholds: Object.keys(rest).length ? rest : null });
    } else {
      setForm({ ...form, regional_strongholds: { ...current, [key]: 0.2 } });
    }
  };

  const updateStrongholdValue = (azId: number, val: number) => {
    const current = form.regional_strongholds || {};
    setForm({ ...form, regional_strongholds: { ...current, [String(azId)]: val } });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: form.color }} />
          <h3 className="text-lg font-semibold">{isNew ? 'New Party' : `Edit: ${party.name}`}</h3>
          {isDirty && <span className="w-2 h-2 rounded-full bg-warning animate-pulse" title="Unsaved changes" />}
        </div>
        <div className="flex gap-2">
          <button onClick={onCancel} className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Cancel</button>
          <button onClick={() => onSave(form)} disabled={!nameValid}
            className="px-3 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium btn-accent disabled:opacity-50">
            {isDirty ? 'Save *' : 'Save'}
          </button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-text-secondary block mb-1">Party Code <span className="text-danger">*</span></label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value.toUpperCase() })}
            className={`w-full bg-bg-tertiary border rounded-md px-3 py-1.5 text-sm focus:ring-1 transition-colors ${nameValid ? 'border-bg-quaternary/50 focus:border-accent focus:ring-accent/30' : 'border-danger/50 focus:border-danger focus:ring-danger/30'}`}
            placeholder="e.g. NRP" />
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Full Name</label>
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" placeholder="e.g. Nigerian Renaissance Party" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div>
          <label className="text-xs text-text-secondary block mb-1">Leader Ethnicity</label>
          <select value={form.leader_ethnicity} onChange={(e) => setForm({ ...form, leader_ethnicity: e.target.value })}
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            <option value="">-- Select --</option>
            {ethnicGroups.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Religious Alignment</label>
          <select value={form.religious_alignment} onChange={(e) => setForm({ ...form, religious_alignment: e.target.value })}
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            <option value="">-- Select --</option>
            {religiousGroups.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Valence ({form.valence.toFixed(1)})</label>
          <input type="range" min={-2} max={2} step={0.1} value={form.valence}
            onChange={(e) => setForm({ ...form, valence: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
          <div className="flex justify-between text-[9px] text-text-secondary/40 -mt-0.5">
            <span>Weak</span><span>Strong</span>
          </div>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Economic ({form.economic_positioning.toFixed(1)})</label>
          <input type="range" min={-1} max={1} step={0.1} value={form.economic_positioning}
            onChange={(e) => setForm({ ...form, economic_positioning: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
          <div className="flex justify-between text-[9px] text-text-secondary/40 -mt-0.5">
            <span>Left</span><span>Right</span>
          </div>
        </div>
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1">Color</label>
        <div className="flex items-center gap-2">
          <div className="flex gap-1 flex-wrap">
            {COLOR_PRESETS.map(c => (
              <button key={c} onClick={() => setForm({ ...form, color: c })}
                className={`w-5 h-5 rounded-sm transition-all ${form.color === c ? 'ring-2 ring-accent ring-offset-1 ring-offset-bg-primary scale-110' : 'hover:scale-110'}`}
                style={{ backgroundColor: c }} />
            ))}
          </div>
          <input type="color" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })}
            className="w-8 h-6 rounded cursor-pointer border-none bg-transparent shrink-0" title="Custom color" />
        </div>
      </div>

      {/* Positions */}
      <div className="border-t border-bg-tertiary/30 pt-4">
        <button onClick={() => setPositionsOpen(o => !o)}
          className="flex items-center gap-2 w-full text-left mb-2 group/section">
          <svg className={`w-3 h-3 text-text-secondary transition-transform ${positionsOpen ? 'rotate-90' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M9 18l6-6-6-6" /></svg>
          <h4 className="text-sm font-semibold text-text-secondary">Issue Positions (28 dimensions)</h4>
          {!positionsOpen && (
            <span className="text-[10px] text-text-secondary/40 ml-auto">
              {form.positions.filter(v => Math.abs(v) > 0.5).length} strong positions
            </span>
          )}
        </button>
        {positionsOpen && (
          <>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex gap-1">
                {POSITION_PRESETS.map(p => (
                  <button key={p.label} onClick={() => setForm({ ...form, positions: p.positions })}
                    className="px-2 py-0.5 text-[10px] bg-bg-tertiary rounded hover:bg-bg-tertiary/80 text-text-secondary transition-colors">
                    {p.label}
                  </button>
                ))}
              </div>
              <div className="flex gap-1 ml-auto">
                <button onClick={() => setForm({ ...form, positions: new Array(28).fill(0) })}
                  className="px-2 py-0.5 text-[10px] bg-bg-tertiary rounded hover:bg-bg-tertiary/80 text-text-secondary">
                  Reset
                </button>
                <button onClick={() => setForm({ ...form, positions: form.positions.map(() => Math.round((Math.random() * 2 - 1) * 10) / 10) })}
                  className="px-2 py-0.5 text-[10px] bg-bg-tertiary rounded hover:bg-bg-tertiary/80 text-text-secondary">
                  Random
                </button>
              </div>
            </div>
            {/* Position summary bar */}
            <div className="flex gap-px mb-2 h-2 rounded-full overflow-hidden bg-bg-tertiary">
              {form.positions.map((v, i) => (
                <div key={i} className="flex-1" style={{ backgroundColor: v > 0.3 ? '#22c55e' : v < -0.3 ? '#ef4444' : '#334155', opacity: 0.5 + Math.abs(v) * 0.5 }}
                  title={`${issueNames[i] ?? i}: ${v.toFixed(1)}`} />
              ))}
            </div>
            <div className="bg-bg-primary rounded-lg p-3 max-h-96 overflow-y-auto space-y-0.5">
              {issueNames.map((name, idx) => (
                <PositionSlider
                  key={name}
                  dimension={`${idx}. ${name}`}
                  value={form.positions[idx] ?? 0}
                  description={ISSUE_DESCRIPTIONS[name]}
                  onChange={(v) => updatePosition(idx, v)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Regional Strongholds */}
      <div className="border-t border-bg-tertiary/30 pt-4">
        <button onClick={() => setStrongholdsOpen(o => !o)}
          className="flex items-center gap-2 w-full text-left mb-2 group/section">
          <svg className={`w-3 h-3 text-text-secondary transition-transform ${strongholdsOpen ? 'rotate-90' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M9 18l6-6-6-6" /></svg>
          <h4 className="text-sm font-semibold text-text-secondary">Regional Strongholds</h4>
          {!strongholdsOpen && form.regional_strongholds && (
            <span className="text-[10px] text-text-secondary/40 ml-auto">
              {Object.keys(form.regional_strongholds).length} active
            </span>
          )}
        </button>
        {strongholdsOpen && (
          <div className="grid grid-cols-2 gap-2">
            {AZ_IDS.map(azId => {
              const az = adminZones.find(z => z.id === azId);
              const key = String(azId);
              const active = form.regional_strongholds && key in form.regional_strongholds;
              const val = active ? form.regional_strongholds![key] : 0;
              return (
                <div key={azId} className="flex items-center gap-2">
                  <input type="checkbox" checked={!!active} onChange={() => toggleStronghold(azId)}
                    className="accent-accent" />
                  <span className="text-xs w-44 truncate">{az?.name ?? `AZ ${azId}`}</span>
                  {active && (
                    <input type="number" min={-1} max={1} step={0.05} value={val}
                      onChange={(e) => updateStrongholdValue(azId, parseFloat(e.target.value) || 0)}
                      className="w-16 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
