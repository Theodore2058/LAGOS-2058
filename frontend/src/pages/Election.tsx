import { useState, useEffect } from 'react';
import type { Party, EngineParams, ElectionResults } from '../types';
import { fetchParties } from '../api/parties';
import { runElection } from '../api/election';
import { ParamsEditor } from './Params';
import ElectionDashboard from '../components/ElectionDashboard';

const DEFAULT_PARAMS: EngineParams = {
  q: 0.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, scale: 1.5,
  tau_0: 4.5, tau_1: 0.3, tau_2: 0.5, beta_econ: 0.3,
  kappa: 200, sigma_national: 0.10, sigma_regional: 0.15,
  sigma_turnout: 0.0, sigma_turnout_regional: 0.0,
  n_monte_carlo: 100, seed: null,
};

export default function Election() {
  const [parties, setParties] = useState<Party[]>([]);
  const [params, setParams] = useState<EngineParams>(DEFAULT_PARAMS);
  const [results, setResults] = useState<ElectionResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showParams, setShowParams] = useState(false);

  useEffect(() => { fetchParties().then(setParties); }, []);

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
            className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
            {showParams ? 'Hide' : 'Show'} Parameters
          </button>
          <button onClick={handleRun} disabled={loading}
            className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white disabled:opacity-50">
            {loading ? 'Running...' : 'Run Election'}
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-3 bg-danger/20 text-danger rounded text-sm">{error}</div>}

      {showParams && (
        <div className="mb-6 bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <ParamsEditor params={params} onChange={setParams} />
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
            <p className="text-text-secondary">Running election simulation...</p>
            <p className="text-xs text-text-secondary mt-1">This may take 10-60 seconds depending on MC runs</p>
          </div>
        </div>
      )}

      {results && !loading && <ElectionDashboard results={results} parties={parties} />}
    </div>
  );
}
