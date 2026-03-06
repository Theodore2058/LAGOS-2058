import { useState, useEffect } from 'react';
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

export default function PartyForm({ party, issueNames, ethnicGroups, religiousGroups, adminZones, onSave, onCancel, isNew }: Props) {
  const [form, setForm] = useState<Party>({ ...party });

  useEffect(() => {
    setForm({ ...party });
  }, [party]);

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
        <h3 className="text-lg font-semibold">{isNew ? 'New Party' : `Edit: ${party.name}`}</h3>
        <div className="flex gap-2">
          <button onClick={onCancel} className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Cancel</button>
          <button onClick={() => onSave(form)} className="px-3 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white">Save</button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-text-secondary block mb-1">Party Code</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value.toUpperCase() })}
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" placeholder="e.g. NRP" />
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
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Economic ({form.economic_positioning.toFixed(1)})</label>
          <input type="range" min={-1} max={1} step={0.1} value={form.economic_positioning}
            onChange={(e) => setForm({ ...form, economic_positioning: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
        </div>
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1">Color</label>
        <input type="color" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })}
          className="w-10 h-8 rounded cursor-pointer border-none bg-transparent" />
      </div>

      {/* Positions */}
      <div>
        <h4 className="text-sm font-semibold mb-2 text-text-secondary">Issue Positions (28 dimensions)</h4>
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
      </div>

      {/* Regional Strongholds */}
      <div>
        <h4 className="text-sm font-semibold mb-2 text-text-secondary">Regional Strongholds</h4>
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
      </div>
    </div>
  );
}
