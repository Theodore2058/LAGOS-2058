import { useState, useEffect, useMemo } from 'react';
import { saveScenario, listScenarios, deleteScenario, compareScenarios, exportSession, importSession } from '../api/scenarios';
import { useToast } from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';
import ErrorBanner from '../components/ErrorBanner';

interface ScenarioSummary {
  name: string;
  n_parties: number;
  n_turns: number;
}

interface CompareResult {
  scenario_a: string;
  scenario_b: string;
  delta: Record<string, { a: number; b: number; diff: number }>;
  seat_delta?: Record<string, { a: number; b: number; diff: number }>;
}

function DeltaBar({ diff, max, label }: { diff: number; max: number; label: string }) {
  const pct = max > 0 ? Math.min(Math.abs(diff) / max * 100, 100) : 0;
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-24 h-1.5 bg-bg-tertiary rounded-full relative overflow-hidden">
        <div
          className={`absolute top-0 h-full rounded-full ${diff > 0 ? 'bg-success right-1/2' : diff < 0 ? 'bg-danger left-1/2' : 'bg-text-secondary left-1/2'}`}
          style={{
            width: `${pct / 2}%`,
            ...(diff > 0 ? { right: '50%' } : { left: '50%' }),
          }}
        />
        <div className="absolute left-1/2 top-0 w-px h-full bg-text-secondary/30" />
      </div>
      <span className={`text-[10px] font-mono w-14 text-right ${diff > 0 ? 'text-success' : diff < 0 ? 'text-danger' : 'text-text-secondary/40'}`}>
        {label}
      </span>
    </div>
  );
}

export default function Scenarios() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [newName, setNewName] = useState('');
  const [compareA, setCompareA] = useState('');
  const [compareB, setCompareB] = useState('');
  const [comparison, setComparison] = useState<CompareResult | null>(null);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  const reload = () => listScenarios().then(setScenarios).catch(e => console.error('Failed to list scenarios:', e));
  useEffect(() => { reload(); }, []);

  const handleSave = async () => {
    if (!newName) return;
    setSaving(true);
    try {
      await saveScenario(newName);
      setNewName('');
      setError(null);
      reload();
      toast(`Saved scenario "${newName}"`, 'success');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save scenario');
    } finally { setSaving(false); }
  };

  const handleDelete = async (name: string) => {
    try {
      await deleteScenario(name);
      reload();
      if (compareA === name) setCompareA('');
      if (compareB === name) setCompareB('');
      if (comparison && (comparison.scenario_a === name || comparison.scenario_b === name)) setComparison(null);
      toast(`Deleted "${name}"`, 'success');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete scenario');
    }
  };

  const handleCompare = async () => {
    if (!compareA || !compareB || compareA === compareB) return;
    setComparing(true);
    try {
      const result = await compareScenarios(compareA, compareB);
      setComparison(result);
      setError(null);
    } catch (e) { console.error('Comparison failed:', e); setError('Comparison failed'); }
    finally { setComparing(false); }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        try {
          await importSession(file);
          reload();
          toast('Session imported', 'success');
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Import failed');
        }
      }
    };
    input.click();
  };

  const sortedVoteDelta = useMemo(() => {
    if (!comparison) return [];
    return Object.entries(comparison.delta).sort((a, b) => Math.abs(b[1].diff) - Math.abs(a[1].diff));
  }, [comparison]);

  const sortedSeatDelta = useMemo(() => {
    if (!comparison?.seat_delta) return [];
    return Object.entries(comparison.seat_delta).sort((a, b) => Math.abs(b[1].diff) - Math.abs(a[1].diff));
  }, [comparison]);

  const maxVoteDiff = useMemo(() => sortedVoteDelta.length > 0 ? Math.max(...sortedVoteDelta.map(([, d]) => Math.abs(d.diff))) : 0, [sortedVoteDelta]);
  const maxSeatDiff = useMemo(() => sortedSeatDelta.length > 0 ? Math.max(...sortedSeatDelta.map(([, d]) => Math.abs(d.diff))) : 0, [sortedSeatDelta]);

  return (
    <div className="p-6 max-w-4xl space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Scenarios</h2>
        <div className="flex gap-2">
          <button onClick={() => exportSession()}
            className="px-3 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
            Export
          </button>
          <button onClick={handleImport}
            className="px-3 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
            Import
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {/* Save */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" /><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></svg>
          Save Current State
        </h3>
        <p className="text-xs text-text-secondary mb-3">Snapshot the current parties, parameters, and campaign progress.</p>
        <div className="flex gap-2">
          <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Scenario name"
            onKeyDown={e => { if (e.key === 'Enter') handleSave(); }}
            className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors placeholder:text-text-secondary/30" />
          <button onClick={handleSave} disabled={saving || !newName}
            className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium btn-accent disabled:opacity-50 disabled:cursor-not-allowed">
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* List */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></svg>
          Saved Scenarios
          <span className="text-text-secondary/50 font-normal">({scenarios.length})</span>
        </h3>
        {scenarios.length === 0 ? (
          <div className="flex flex-col items-center py-8 text-center">
            <svg className="w-10 h-10 text-text-secondary/20 mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
            </svg>
            <p className="text-sm text-text-secondary">No scenarios saved yet</p>
            <p className="text-xs text-text-secondary/40 mt-1">Save the current game state to create your first scenario.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {scenarios.map(s => (
              <div key={s.name} className="bg-bg-tertiary/40 rounded-md p-3 border border-bg-quaternary/20 hover:border-accent/20 transition-colors group/card card-glow">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">{s.name}</div>
                    <div className="flex gap-2 mt-1.5">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-bg-quaternary/30 text-text-secondary">{s.n_parties} parties</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-bg-quaternary/30 text-text-secondary">{s.n_turns} turns</span>
                    </div>
                  </div>
                  <button onClick={() => setDeleteTarget(s.name)}
                    className="opacity-0 group-hover/card:opacity-100 text-danger/50 hover:text-danger p-1 rounded hover:bg-danger/10 transition-all shrink-0"
                    aria-label={`Delete scenario ${s.name}`}>
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" /><path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" /></svg>
                  </button>
                </div>
                {/* Turn progress bar */}
                <div className="mt-2">
                  <div className="h-1 bg-bg-quaternary/30 rounded-full overflow-hidden">
                    <div className="h-full bg-accent/40 rounded-full transition-all" style={{ width: `${Math.min((s.n_turns / 12) * 100, 100)}%` }} />
                  </div>
                  <div className="text-[9px] text-text-secondary/40 mt-0.5">{s.n_turns}/12 turns</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compare */}
      {scenarios.length >= 2 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <svg className="w-4 h-4 text-teal" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></svg>
            Compare Scenarios
          </h3>
          <div className="flex gap-2 items-center mb-3">
            <select value={compareA} onChange={e => setCompareA(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              <option value="">Select A...</option>
              {scenarios.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
            <span className="text-text-secondary/40 text-xs font-mono">vs</span>
            <select value={compareB} onChange={e => setCompareB(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              <option value="">Select B...</option>
              {scenarios.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
            <button onClick={handleCompare} disabled={comparing || !compareA || !compareB || compareA === compareB}
              className="px-4 py-1.5 text-sm bg-teal/20 text-teal rounded hover:bg-teal/30 transition-colors font-medium disabled:opacity-40 disabled:cursor-not-allowed">
              {comparing ? 'Comparing...' : 'Compare'}
            </button>
          </div>

          {compareA && compareB && compareA === compareB && (
            <p className="text-xs text-warning">Select two different scenarios to compare.</p>
          )}

          {comparison && (
            <div className="space-y-4 mt-4">
              {/* Vote Share Delta */}
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Vote Share Delta</h4>
                  <div className="flex-1 h-px bg-bg-tertiary" />
                </div>
                <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-3 gap-y-0.5 text-xs">
                  <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider">Party</div>
                  <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right">{comparison.scenario_a}</div>
                  <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right">{comparison.scenario_b}</div>
                  <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right col-span-2">Delta</div>
                  {sortedVoteDelta.map(([party, d]) => (
                    <div key={party} className="contents">
                      <div className="py-0.5 truncate">{party}</div>
                      <div className="py-0.5 text-right text-text-secondary">{(d.a * 100).toFixed(1)}%</div>
                      <div className="py-0.5 text-right text-text-secondary">{(d.b * 100).toFixed(1)}%</div>
                      <div className="py-0.5 col-span-2 flex justify-end">
                        <DeltaBar diff={d.diff} max={maxVoteDiff} label={`${d.diff > 0 ? '+' : ''}${(d.diff * 100).toFixed(2)}%`} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Seat Delta */}
              {sortedSeatDelta.length > 0 && (
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Seat Delta</h4>
                    <div className="flex-1 h-px bg-bg-tertiary" />
                  </div>
                  <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-3 gap-y-0.5 text-xs">
                    <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider">Party</div>
                    <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right">{comparison.scenario_a}</div>
                    <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right">{comparison.scenario_b}</div>
                    <div className="text-text-secondary/40 text-[10px] uppercase tracking-wider text-right col-span-2">Delta</div>
                    {sortedSeatDelta.map(([party, d]) => (
                      <div key={party} className="contents">
                        <div className="py-0.5 truncate">{party}</div>
                        <div className="py-0.5 text-right text-text-secondary">{Math.round(d.a)}</div>
                        <div className="py-0.5 text-right text-text-secondary">{Math.round(d.b)}</div>
                        <div className="py-0.5 col-span-2 flex justify-end">
                          <DeltaBar diff={d.diff} max={maxSeatDiff} label={`${d.diff > 0 ? '+' : ''}${Math.round(d.diff)}`} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <ConfirmModal
        open={!!deleteTarget}
        title="Delete Scenario"
        message={`Permanently delete scenario "${deleteTarget}"? This cannot be undone.`}
        confirmLabel="Delete"
        confirmDanger
        onConfirm={() => {
          if (deleteTarget) handleDelete(deleteTarget);
          setDeleteTarget(null);
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
