import { useState, useEffect } from 'react';
import { saveScenario, listScenarios, deleteScenario, compareScenarios, exportSession, importSession } from '../api/scenarios';

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

export default function Scenarios() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [newName, setNewName] = useState('');
  const [compareA, setCompareA] = useState('');
  const [compareB, setCompareB] = useState('');
  const [comparison, setComparison] = useState<CompareResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = () => listScenarios().then(setScenarios).catch(e => console.error('Failed to list scenarios:', e));
  useEffect(() => { reload(); }, []);

  const handleSave = async () => {
    if (!newName) return;
    await saveScenario(newName);
    setNewName('');
    reload();
  };

  const handleDelete = async (name: string) => {
    await deleteScenario(name);
    reload();
  };

  const handleCompare = async () => {
    if (!compareA || !compareB) return;
    try {
      const result = await compareScenarios(compareA, compareB);
      setComparison(result);
    } catch (e) { console.error('Comparison failed:', e); setError('Comparison failed'); }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        await importSession(file);
        reload();
      }
    };
    input.click();
  };

  return (
    <div className="p-8 max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold">Scenarios</h2>

      {error && <div className="p-3 bg-danger/20 text-danger rounded text-sm">{error}</div>}

      {/* Save */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" /><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></svg>
          Save Current State
        </h3>
        <div className="flex gap-2">
          <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Scenario name"
            className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
          <button onClick={handleSave} className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white">Save</button>
        </div>
      </div>

      {/* List */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></svg>
          Saved Scenarios ({scenarios.length})
        </h3>
        {scenarios.length === 0 ? (
          <div className="flex flex-col items-center py-6 text-center">
            <svg className="w-8 h-8 text-text-secondary/30 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
            </svg>
            <p className="text-xs text-text-secondary">No scenarios saved yet.</p>
            <p className="text-[10px] text-text-secondary/50 mt-0.5">Use the form above to save the current game state.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {scenarios.map(s => (
              <div key={s.name} className="flex items-center gap-3 text-sm py-2 px-2 -mx-2 rounded hover:bg-bg-tertiary/20 transition-colors border-b border-bg-tertiary/30">
                <span className="flex-1 font-mono">{s.name}</span>
                <span className="text-xs text-text-secondary">{s.n_parties} parties, {s.n_turns} turns</span>
                <button onClick={() => handleDelete(s.name)} className="text-danger/60 hover:text-danger p-1 rounded hover:bg-danger/10 transition-colors" aria-label={`Delete scenario ${s.name}`}>
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" /><path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" /></svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compare */}
      {scenarios.length >= 2 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <svg className="w-4 h-4 text-text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></svg>
            Compare Scenarios
          </h3>
          <div className="flex gap-2 mb-3">
            <select value={compareA} onChange={e => setCompareA(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              <option value="">Scenario A</option>
              {scenarios.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
            <span className="text-text-secondary self-center">vs</span>
            <select value={compareB} onChange={e => setCompareB(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-3 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              <option value="">Scenario B</option>
              {scenarios.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
            <button onClick={handleCompare}
              className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white">Compare</button>
          </div>

          {comparison && (
            <div>
              <h4 className="text-xs text-text-secondary mb-1">Vote Share Delta</h4>
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-bg-tertiary">
                    <th className="text-left py-1">Party</th>
                    <th className="text-right py-1">{comparison.scenario_a}</th>
                    <th className="text-right py-1">{comparison.scenario_b}</th>
                    <th className="text-right py-1">Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparison.delta)
                    .sort((a, b) => Math.abs(b[1].diff) - Math.abs(a[1].diff))
                    .map(([party, d]) => (
                      <tr key={party} className="border-b border-bg-tertiary/30">
                        <td className="py-0.5">{party}</td>
                        <td className="text-right">{(d.a * 100).toFixed(1)}%</td>
                        <td className="text-right">{(d.b * 100).toFixed(1)}%</td>
                        <td className={`text-right ${d.diff > 0 ? 'text-success' : d.diff < 0 ? 'text-danger' : ''}`}>
                          {d.diff > 0 ? '+' : ''}{(d.diff * 100).toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Export/Import */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
          Session Data
        </h3>
        <div className="flex gap-2">
          <button onClick={() => exportSession()}
            className="px-4 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Export Session</button>
          <button onClick={handleImport}
            className="px-4 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Import Session</button>
        </div>
      </div>
    </div>
  );
}
