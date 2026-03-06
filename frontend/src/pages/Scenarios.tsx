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

  const reload = () => listScenarios().then(setScenarios).catch(() => {});
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
    } catch { setError('Comparison failed'); }
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
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
        <h3 className="text-sm font-semibold mb-2">Save Current State</h3>
        <div className="flex gap-2">
          <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Scenario name"
            className="flex-1 bg-bg-tertiary border border-bg-tertiary rounded px-3 py-1.5 text-sm" />
          <button onClick={handleSave} className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white">Save</button>
        </div>
      </div>

      {/* List */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
        <h3 className="text-sm font-semibold mb-2">Saved Scenarios ({scenarios.length})</h3>
        {scenarios.length === 0 ? (
          <p className="text-xs text-text-secondary">No scenarios saved yet.</p>
        ) : (
          <div className="space-y-1">
            {scenarios.map(s => (
              <div key={s.name} className="flex items-center gap-3 text-sm py-1 border-b border-bg-tertiary/30">
                <span className="flex-1 font-mono">{s.name}</span>
                <span className="text-xs text-text-secondary">{s.n_parties} parties, {s.n_turns} turns</span>
                <button onClick={() => handleDelete(s.name)} className="text-xs text-danger/60 hover:text-danger">Delete</button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compare */}
      {scenarios.length >= 2 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <h3 className="text-sm font-semibold mb-2">Compare Scenarios</h3>
          <div className="flex gap-2 mb-3">
            <select value={compareA} onChange={e => setCompareA(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-tertiary rounded px-3 py-1.5 text-sm">
              <option value="">Scenario A</option>
              {scenarios.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
            <span className="text-text-secondary self-center">vs</span>
            <select value={compareB} onChange={e => setCompareB(e.target.value)}
              className="flex-1 bg-bg-tertiary border border-bg-tertiary rounded px-3 py-1.5 text-sm">
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
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
        <h3 className="text-sm font-semibold mb-2">Session Data</h3>
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
