import { useState, useEffect, useMemo } from 'react';
import type { CrisisInput, Party } from '../types';
import { ADMIN_ZONES } from '../types';
import { fetchTemplates, fetchCrises, createCrisis, deleteCrisis } from '../api/crises';
import type { CrisisTemplate, StoredCrisis } from '../api/crises';
import { fetchIssueNames } from '../api/config';
import { fetchParties } from '../api/parties';
import { useToast } from '../components/Toast';
import ErrorBanner from '../components/ErrorBanner';

const BLANK: CrisisInput = {
  name: '', turn: 1, affected_azs: null, affected_lgas: null,
  salience_shifts: {}, valence_effects: null, awareness_boost: null,
  tau_modifier: 0, description: '',
};

const TEMPLATE_CATEGORIES: Record<string, string> = {
  'Economic Shock': 'Economic',
  'WAFTA Trade Disruption': 'Economic',
  'Infrastructure Failure': 'Economic',
  'Ethnic Violence': 'Security',
  'Security Crisis': 'Security',
  'Natural Disaster': 'Security',
  'Corruption Scandal': 'Political',
  'Pada Controversy': 'Political',
  'Religious Tension': 'Social',
};

const SEVERITY_COLORS = {
  low: { bg: 'bg-success/10', text: 'text-success', label: 'Low' },
  medium: { bg: 'bg-warning/10', text: 'text-warning', label: 'Medium' },
  high: { bg: 'bg-danger/10', text: 'text-danger', label: 'High' },
};

function getSeverity(t: CrisisTemplate): keyof typeof SEVERITY_COLORS {
  const salienceMag = Object.values(t.salience_shifts).reduce((s, v) => s + Math.abs(v), 0);
  const valenceMag = t.valence_effects ? Object.values(t.valence_effects).reduce((s, v) => s + Math.abs(v), 0) : 0;
  const tauMag = Math.abs(t.tau_modifier);
  const total = salienceMag + valenceMag * 2 + tauMag * 3;
  if (total >= 5) return 'high';
  if (total >= 2) return 'medium';
  return 'low';
}

export default function Crises() {
  const [templates, setTemplates] = useState<CrisisTemplate[]>([]);
  const [crises, setCrises] = useState<StoredCrisis[]>([]);
  const [issueNames, setIssueNames] = useState<string[]>([]);
  const [parties, setParties] = useState<Party[]>([]);
  const [editing, setEditing] = useState<CrisisInput>({ ...BLANK });
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchTemplates().then(setTemplates).catch(e => console.error('Failed to fetch templates:', e));
    fetchCrises().then(setCrises).catch(e => console.error('Failed to fetch crises:', e));
    fetchIssueNames().then(setIssueNames).catch(e => console.error('Failed to fetch issue names:', e));
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
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
      toast(`Added crisis "${saved.name}" to turn ${saved.turn}`, 'success');
    } catch (e) { console.error('Failed to save crisis:', e); setError('Failed to save crisis'); }
  };

  const handleDelete = async (id: number) => {
    try {
      const crisis = crises.find(c => c.id === id);
      await deleteCrisis(id);
      setCrises(prev => prev.filter(c => c.id !== id));
      toast(`Removed crisis${crisis ? ` "${crisis.name}"` : ''}`, 'success');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete crisis');
    }
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

  const updateValence = (partyName: string, val: number) => {
    const effects = { ...(editing.valence_effects ?? {}) };
    if (val === 0) { delete effects[partyName]; }
    else { effects[partyName] = val; }
    setEditing({ ...editing, valence_effects: Object.keys(effects).length > 0 ? effects : null });
  };

  const updateAwareness = (partyName: string, val: number) => {
    const boosts = { ...(editing.awareness_boost ?? {}) };
    if (val === 0) { delete boosts[partyName]; }
    else { boosts[partyName] = val; }
    setEditing({ ...editing, awareness_boost: Object.keys(boosts).length > 0 ? boosts : null });
  };

  const isDirty = editing.name !== '' || editing.description !== '' || editing.tau_modifier !== 0
    || Object.keys(editing.salience_shifts).length > 0 || editing.valence_effects !== null
    || editing.awareness_boost !== null || editing.affected_azs !== null;

  const activeSalienceCount = Object.keys(editing.salience_shifts).length;
  const activeValenceCount = Object.keys(editing.valence_effects ?? {}).length;
  const activeAwarenessCount = Object.keys(editing.awareness_boost ?? {}).length;

  const effectSummary = useMemo(() => {
    const items: string[] = [];
    if (editing.tau_modifier !== 0) items.push(`Tau ${editing.tau_modifier > 0 ? '+' : ''}${editing.tau_modifier.toFixed(1)}`);
    if (activeSalienceCount > 0) items.push(`${activeSalienceCount} salience shift${activeSalienceCount > 1 ? 's' : ''}`);
    if (activeValenceCount > 0) items.push(`${activeValenceCount} valence effect${activeValenceCount > 1 ? 's' : ''}`);
    if (activeAwarenessCount > 0) items.push(`${activeAwarenessCount} awareness boost${activeAwarenessCount > 1 ? 's' : ''}`);
    const scope = editing.affected_azs ? `${editing.affected_azs.length} AZ${editing.affected_azs.length > 1 ? 's' : ''}` : 'national';
    return { items, scope };
  }, [editing, activeSalienceCount, activeValenceCount, activeAwarenessCount]);

  return (
    <div className="flex h-full">
      {/* Timeline sidebar */}
      <div className="w-72 bg-bg-secondary border-r border-bg-tertiary flex flex-col shrink-0">
        <div className="p-3 border-b border-bg-tertiary">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <svg className="w-4 h-4 text-danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
            Crisis Timeline
          </h3>
          {/* Mini turn heatmap */}
          <div className="flex gap-0.5 mt-2">
            {Array.from({ length: 12 }, (_, i) => {
              const count = crises.filter(c => c.turn === i + 1).length;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-0.5" title={`T${i + 1}: ${count} crisis${count !== 1 ? 'es' : ''}`}>
                  <div className={`w-full h-1.5 rounded-sm ${count > 1 ? 'bg-danger' : count === 1 ? 'bg-danger/50' : 'bg-bg-tertiary/50'}`} />
                  <span className="text-[7px] text-text-secondary/30">{i + 1}</span>
                </div>
              );
            })}
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {Array.from({ length: 12 }, (_, i) => i + 1).map(turn => {
            const turnCrises = crises.filter(c => c.turn === turn);
            return (
              <div key={turn} className={`px-3 py-2.5 border-b border-bg-tertiary/30 transition-colors ${turnCrises.length > 0 ? 'bg-danger/5 border-l-2 border-l-danger/40' : 'hover:bg-bg-tertiary/20'}`}>
                <div className="text-xs text-text-secondary mb-1 font-mono">Turn {turn}</div>
                {turnCrises.map(c => (
                  <div key={c.id} className="flex items-center gap-2 text-xs py-0.5 group/crisis">
                    <svg className="w-3 h-3 text-danger shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
                    <span className="flex-1 truncate" title={c.description || c.name}>{c.name}</span>
                    <button onClick={() => handleDelete(c.id)} className="opacity-0 group-hover/crisis:opacity-100 text-danger/60 hover:text-danger transition-all" aria-label={`Delete crisis ${c.name}`}>
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                    </button>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
        <div className="p-2 border-t border-bg-tertiary text-xs text-text-secondary text-center">
          {crises.length} crisis{crises.length !== 1 ? 'es' : ''} scheduled
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Crisis Manager</h2>
          {isDirty && (
            <button onClick={() => setEditing({ ...BLANK })}
              className="px-3 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center gap-1.5">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M3 12a9 9 0 109-9 9.75 9.75 0 00-6.74 2.74L3 8" /><path d="M3 3v5h5" /></svg>
              Reset Form
            </button>
          )}
        </div>

        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        {/* Template selector */}
        <div>
          <label className="text-[10px] text-text-secondary block mb-2 uppercase tracking-[0.1em] font-medium">Load from Template</label>
          {(() => {
            const grouped = templates.reduce<Record<string, CrisisTemplate[]>>((acc, t) => {
              const cat = TEMPLATE_CATEGORIES[t.name] ?? 'Other';
              (acc[cat] ??= []).push(t);
              return acc;
            }, {});
            return (
              <div className="space-y-3">
                {Object.entries(grouped).map(([cat, tpls]) => (
                  <div key={cat}>
                    <div className="text-[9px] text-text-secondary/40 uppercase tracking-wider mb-1.5 font-medium">{cat}</div>
                    <div className="grid grid-cols-3 gap-2">
                      {tpls.map(t => {
                        const activeShifts = Object.keys(t.salience_shifts).length;
                        const hasValence = t.valence_effects && Object.keys(t.valence_effects).length > 0;
                        const hasAwareness = t.awareness_boost && Object.keys(t.awareness_boost).length > 0;
                        const sev = getSeverity(t);
                        const sevStyle = SEVERITY_COLORS[sev];
                        return (
                          <button key={t.name} onClick={() => loadTemplate(t)}
                            className="text-left px-3 py-2 bg-bg-tertiary border border-bg-quaternary/30 rounded-md hover:border-danger/40 hover:bg-bg-tertiary/70 transition-colors group">
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-medium group-hover:text-danger transition-colors flex-1 truncate">{t.name}</span>
                              <span className={`text-[8px] px-1 py-px rounded ${sevStyle.bg} ${sevStyle.text} shrink-0`}>{sevStyle.label}</span>
                            </div>
                            <div className="text-[10px] text-text-secondary leading-tight mt-0.5 line-clamp-2">{t.description}</div>
                            <div className="flex flex-wrap gap-1 mt-1.5">
                              {t.tau_modifier !== 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-bg-quaternary/30 text-text-secondary">tau {t.tau_modifier > 0 ? '+' : ''}{t.tau_modifier}</span>}
                              {activeShifts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-bg-quaternary/30 text-text-secondary">{activeShifts} issue{activeShifts > 1 ? 's' : ''}</span>}
                              {hasValence && <span className="text-[9px] px-1 py-0.5 rounded bg-danger/10 text-danger/80">valence</span>}
                              {hasAwareness && <span className="text-[9px] px-1 py-0.5 rounded bg-teal/10 text-teal">awareness</span>}
                              {t.affected_azs && <span className="text-[9px] px-1 py-0.5 rounded bg-bg-quaternary/30 text-text-secondary">{t.affected_azs.length} AZ{t.affected_azs.length > 1 ? 's' : ''}</span>}
                              {!t.affected_azs && <span className="text-[9px] px-1 py-0.5 rounded bg-warning/10 text-warning">national</span>}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
        </div>

        {/* Crisis form */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-text-secondary block mb-1">Name</label>
              <input value={editing.name} onChange={e => setEditing({ ...editing, name: e.target.value })}
                placeholder="e.g. Fuel Subsidy Removal"
                className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors placeholder:text-text-secondary/30" />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">Turn (1-12)</label>
              <input type="number" min={1} max={12} value={editing.turn}
                onChange={e => setEditing({ ...editing, turn: parseInt(e.target.value) || 1 })}
                className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Tau Modifier
                <span className={`ml-1 font-mono ${editing.tau_modifier !== 0 ? 'text-accent' : 'text-text-secondary/40'}`}>
                  ({editing.tau_modifier > 0 ? '+' : ''}{editing.tau_modifier.toFixed(1)})
                </span>
              </label>
              <input type="range" min={-1} max={1} step={0.1} value={editing.tau_modifier}
                onChange={e => setEditing({ ...editing, tau_modifier: parseFloat(e.target.value) })}
                className="w-full accent-accent" />
              <div className="flex justify-between text-[9px] text-text-secondary/40 mt-0.5">
                <span>-1.0 suppress</span><span>0</span><span>+1.0 boost</span>
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs text-text-secondary block mb-1">Description</label>
            <textarea value={editing.description} onChange={e => setEditing({ ...editing, description: e.target.value })}
              placeholder="What happens in this crisis?"
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors h-16 placeholder:text-text-secondary/30" />
          </div>

          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Affected Zones
              <span className="text-text-secondary/40 ml-1">{editing.affected_azs ? `(${editing.affected_azs.length} selected)` : '(empty = national)'}</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(az => (
                <button key={az} onClick={() => toggleAz(az)}
                  className={`px-2 py-1 text-xs rounded transition-colors duration-150 ${editing.affected_azs?.includes(az) ? 'bg-accent text-bg-primary' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}>
                  {ADMIN_ZONES[az]?.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Salience shifts */}
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Salience Shifts
              {activeSalienceCount > 0 && <span className="text-accent ml-1">({activeSalienceCount} active)</span>}
            </label>
            <div className="max-h-48 overflow-y-auto space-y-0.5">
              {issueNames.map((name, idx) => {
                const val = editing.salience_shifts[String(idx)] ?? 0;
                return (
                  <div key={idx} className={`flex items-center gap-2 px-1 rounded ${val !== 0 ? 'bg-accent/5' : ''}`}>
                    <span className={`w-40 text-xs truncate ${val !== 0 ? 'text-text-primary' : 'text-text-secondary'}`}>{name}</span>
                    <input type="range" min={-3} max={3} step={0.5} value={val}
                      onChange={e => updateSalience(idx, parseFloat(e.target.value))}
                      className="flex-1 h-1 accent-accent" />
                    <span className={`w-8 text-xs text-center font-mono ${val > 0 ? 'text-success' : val < 0 ? 'text-danger' : ''}`}>
                      {val !== 0 ? (val > 0 ? '+' : '') + val.toFixed(1) : ''}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Valence effects - per party */}
          {parties.length > 0 && (
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Valence Effects
                {activeValenceCount > 0 && <span className="text-danger ml-1">({activeValenceCount} active)</span>}
                <span className="text-text-secondary/40 ml-1">— how crisis shifts party image</span>
              </label>
              <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 max-h-48 overflow-y-auto">
                {parties.map(p => {
                  const val = editing.valence_effects?.[p.name] ?? 0;
                  return (
                    <div key={p.name} className={`flex items-center gap-2 px-1 rounded ${val !== 0 ? 'bg-danger/5' : ''}`}>
                      <span className={`w-20 text-xs truncate ${val !== 0 ? 'text-text-primary' : 'text-text-secondary'}`}>{p.name}</span>
                      <input type="range" min={-2} max={2} step={0.25} value={val}
                        onChange={e => updateValence(p.name, parseFloat(e.target.value))}
                        className="flex-1 h-1 accent-danger" />
                      <span className={`w-8 text-xs text-center font-mono ${val > 0 ? 'text-success' : val < 0 ? 'text-danger' : ''}`}>
                        {val !== 0 ? (val > 0 ? '+' : '') + val.toFixed(2) : ''}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Awareness boost - per party */}
          {parties.length > 0 && (
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Awareness Boost
                {activeAwarenessCount > 0 && <span className="text-teal ml-1">({activeAwarenessCount} active)</span>}
                <span className="text-text-secondary/40 ml-1">— crisis media exposure per party</span>
              </label>
              <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 max-h-48 overflow-y-auto">
                {parties.map(p => {
                  const val = editing.awareness_boost?.[p.name] ?? 0;
                  return (
                    <div key={p.name} className={`flex items-center gap-2 px-1 rounded ${val !== 0 ? 'bg-teal/5' : ''}`}>
                      <span className={`w-20 text-xs truncate ${val !== 0 ? 'text-text-primary' : 'text-text-secondary'}`}>{p.name}</span>
                      <input type="range" min={0} max={0.3} step={0.01} value={val}
                        onChange={e => updateAwareness(p.name, parseFloat(e.target.value))}
                        className="flex-1 h-1 accent-teal" />
                      <span className={`w-8 text-xs text-center font-mono ${val > 0 ? 'text-teal' : ''}`}>
                        {val !== 0 ? '+' + val.toFixed(2) : ''}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Effect summary */}
          {isDirty && effectSummary.items.length > 0 && (
            <div className="bg-bg-tertiary/50 rounded-md p-3 border border-bg-quaternary/20">
              <div className="text-[10px] uppercase tracking-[0.1em] text-text-secondary/60 mb-1.5 font-medium">Effect Summary</div>
              <div className="flex flex-wrap gap-1.5">
                {effectSummary.items.map((item, i) => (
                  <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-bg-quaternary/40 text-text-secondary">{item}</span>
                ))}
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${editing.affected_azs ? 'bg-accent/10 text-accent' : 'bg-warning/10 text-warning'}`}>
                  {effectSummary.scope}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-bg-quaternary/40 text-text-secondary">turn {editing.turn}</span>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3">
            <button onClick={handleSave}
              className="px-4 py-2 bg-accent rounded hover:bg-accent-hover text-bg-primary text-sm font-medium btn-accent">
              Add Crisis to Timeline
            </button>
            {editing.name && (
              <p className="text-xs text-text-secondary">Crisis &ldquo;{editing.name}&rdquo; will fire on turn {editing.turn}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
