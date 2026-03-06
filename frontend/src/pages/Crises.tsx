import { useState, useEffect } from 'react';
import type { CrisisInput } from '../types';
import { ADMIN_ZONES } from '../types';
import { fetchTemplates, fetchCrises, createCrisis, deleteCrisis } from '../api/crises';
import type { CrisisTemplate, StoredCrisis } from '../api/crises';
import { fetchIssueNames } from '../api/config';

const BLANK: CrisisInput = {
  name: '', turn: 1, affected_azs: null, affected_lgas: null,
  salience_shifts: {}, valence_effects: null, awareness_boost: null,
  tau_modifier: 0, description: '',
};

export default function Crises() {
  const [templates, setTemplates] = useState<CrisisTemplate[]>([]);
  const [crises, setCrises] = useState<StoredCrisis[]>([]);
  const [issueNames, setIssueNames] = useState<string[]>([]);
  const [editing, setEditing] = useState<CrisisInput>({ ...BLANK });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates().then(setTemplates).catch(e => console.error('Failed to fetch templates:', e));
    fetchCrises().then(setCrises).catch(e => console.error('Failed to fetch crises:', e));
    fetchIssueNames().then(setIssueNames).catch(e => console.error('Failed to fetch issue names:', e));
  }, []);

  const loadTemplate = (t: CrisisTemplate) => {
    setEditing({
      name: t.name,
      turn: 1,
      affected_azs: t.affected_azs,
      affected_lgas: null,
      salience_shifts: t.salience_shifts,
      valence_effects: t.valence_effects,
      awareness_boost: t.awareness_boost,
      tau_modifier: t.tau_modifier,
      description: t.description,
    });
  };

  const handleSave = async () => {
    if (!editing.name) { setError('Name required'); return; }
    try {
      const saved = await createCrisis(editing);
      setCrises(prev => [...prev, saved]);
      setEditing({ ...BLANK });
      setError(null);
    } catch (e) { console.error('Failed to save crisis:', e); setError('Failed to save crisis'); }
  };

  const handleDelete = async (id: number) => {
    await deleteCrisis(id);
    setCrises(prev => prev.filter(c => c.id !== id));
  };

  const toggleAz = (az: number) => {
    const current = editing.affected_azs ?? [];
    const next = current.includes(az) ? current.filter(a => a !== az) : [...current, az];
    setEditing({ ...editing, affected_azs: next.length > 0 ? next : null });
  };

  const updateSalience = (dimIdx: number, val: number) => {
    const shifts = { ...editing.salience_shifts };
    if (val === 0) { delete shifts[String(dimIdx)]; }
    else { shifts[String(dimIdx)] = val; }
    setEditing({ ...editing, salience_shifts: shifts });
  };

  return (
    <div className="flex h-full">
      {/* Timeline sidebar */}
      <div className="w-72 bg-bg-secondary border-r border-bg-tertiary flex flex-col shrink-0">
        <div className="p-3 border-b border-bg-tertiary">
          <h3 className="text-sm font-semibold">Crisis Timeline</h3>
        </div>
        <div className="flex-1 overflow-y-auto">
          {Array.from({ length: 12 }, (_, i) => i + 1).map(turn => {
            const turnCrises = crises.filter(c => c.turn === turn);
            return (
              <div key={turn} className={`px-3 py-2.5 border-b border-bg-tertiary/30 transition-colors ${turnCrises.length > 0 ? 'bg-danger/5 border-l-2 border-l-danger/40' : 'hover:bg-bg-tertiary/20'}`}>
                <div className="text-xs text-text-secondary mb-1 font-mono">Turn {turn}</div>
                {turnCrises.map(c => (
                  <div key={c.id} className="flex items-center gap-2 text-xs py-0.5">
                    <svg className="w-3 h-3 text-danger shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
                    <span className="flex-1 truncate">{c.name}</span>
                    <button onClick={() => handleDelete(c.id)} className="text-danger/60 hover:text-danger transition-colors">
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                    </button>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
        <div className="p-2 border-t border-bg-tertiary text-xs text-text-secondary text-center">
          {crises.length} crises scheduled
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <h2 className="text-2xl font-bold">Crisis Manager</h2>

        {error && <div className="p-3 bg-danger/20 text-danger rounded text-sm">{error}</div>}

        {/* Template selector */}
        <div>
          <label className="text-xs text-text-secondary block mb-1">Load from Template</label>
          <div className="flex flex-wrap gap-2">
            {templates.map(t => (
              <button key={t.name} onClick={() => loadTemplate(t)}
                className="px-3 py-1 text-xs bg-bg-tertiary border border-bg-quaternary/30 rounded-full hover:border-danger/40 hover:text-danger transition-colors" title={t.description}>
                {t.name}
              </button>
            ))}
          </div>
        </div>

        {/* Crisis form */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-text-secondary block mb-1">Name</label>
              <input value={editing.name} onChange={e => setEditing({ ...editing, name: e.target.value })}
                className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">Turn (1-12)</label>
              <input type="number" min={1} max={12} value={editing.turn}
                onChange={e => setEditing({ ...editing, turn: parseInt(e.target.value) || 1 })}
                className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">Tau Modifier ({editing.tau_modifier.toFixed(1)})</label>
              <input type="range" min={-1} max={1} step={0.1} value={editing.tau_modifier}
                onChange={e => setEditing({ ...editing, tau_modifier: parseFloat(e.target.value) })}
                className="w-full accent-accent" />
            </div>
          </div>

          <div>
            <label className="text-xs text-text-secondary block mb-1">Description</label>
            <textarea value={editing.description} onChange={e => setEditing({ ...editing, description: e.target.value })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors h-16" />
          </div>

          <div>
            <label className="text-xs text-text-secondary block mb-1">Affected Zones (empty = national)</label>
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(az => (
                <button key={az} onClick={() => toggleAz(az)}
                  className={`px-2 py-1 text-xs rounded ${editing.affected_azs?.includes(az) ? 'bg-accent text-white' : 'bg-bg-tertiary'}`}>
                  {ADMIN_ZONES[az]?.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Salience shifts */}
          <div>
            <label className="text-xs text-text-secondary block mb-1">Salience Shifts</label>
            <div className="max-h-48 overflow-y-auto space-y-0.5">
              {issueNames.map((name, idx) => {
                const val = editing.salience_shifts[String(idx)] ?? 0;
                return (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="w-40 text-xs text-text-secondary truncate">{name}</span>
                    <input type="range" min={-3} max={3} step={0.5} value={val}
                      onChange={e => updateSalience(idx, parseFloat(e.target.value))}
                      className="flex-1 h-1 accent-accent" />
                    <span className="w-8 text-xs text-center">{val !== 0 ? val.toFixed(1) : ''}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <button onClick={handleSave}
            className="px-4 py-2 bg-accent rounded hover:bg-accent-hover text-white text-sm">
            Add Crisis to Timeline
          </button>
        </div>
      </div>
    </div>
  );
}
