import { useState, useEffect } from 'react';
import type { Party, EngineParams, ElectionResults } from '../types';
import { fetchParties } from '../api/parties';
import { runElection } from '../api/election';
import { ParamsEditor, DEFAULT_PARAMS } from './Params';
import ElectionDashboard from '../components/ElectionDashboard';

export default function Election() {
  const [parties, setParties] = useState<Party[]>([]);
  const [params, setParams] = useState<EngineParams>(DEFAULT_PARAMS);
  const [results, setResults] = useState<ElectionResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showParams, setShowParams] = useState(false);

  useEffect(() => { fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e)); }, []);

  const handleRun = async () => {
    if (parties.length < 2) {
      setError('Need at least 2 parties. Go to Parties page to add some.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const { n_monte_carlo, seed, ...engineParams } = params;
      const res = await runElection({ params: engineParams, parties, n_monte_carlo, seed });
      setResults(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Election failed');
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Static Election</h2>
        <div className="flex gap-2 items-center">
          <span className="text-sm text-text-secondary">{parties.length} parties loaded</span>
          <button onClick={() => setShowParams(!showParams)}
            className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors">
            {showParams ? 'Hide' : 'Show'} Parameters
          </button>
          <button onClick={handleRun} disabled={loading}
            className="px-4 py-1.5 text-sm bg-accent rounded-md hover:bg-accent-hover text-white font-medium disabled:opacity-50 shadow-sm shadow-accent/20">
            {loading ? 'Running...' : 'Run Election'}
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-3 bg-danger/20 text-danger rounded-md text-sm border border-danger/30">{error}</div>}

      {showParams && (
        <div className="mb-6 bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <ParamsEditor params={params} onChange={setParams} />
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin w-10 h-10 border-[3px] border-accent/30 border-t-accent rounded-full mx-auto mb-4" />
            <p className="text-text-secondary font-medium">Running election simulation...</p>
            <p className="text-xs text-text-secondary mt-1">This may take 10-60 seconds depending on MC runs</p>
          </div>
        </div>
      )}

      {results && !loading && <ElectionDashboard results={results} parties={parties} />}

      {!results && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <p className="text-text-secondary font-medium mb-1">Ready to simulate</p>
          <p className="text-xs text-text-secondary/60 max-w-md">
            Click <span className="text-accent font-medium">Run Election</span> to execute a one-shot election with Monte Carlo sampling.
            Use <span className="text-text-primary font-medium">Show Parameters</span> to tune the Merrill-Grofman model before running.
          </p>
        </div>
      )}
    </div>
  );
}
