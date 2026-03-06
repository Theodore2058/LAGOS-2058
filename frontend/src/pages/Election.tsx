import { useState, useEffect, useCallback, useRef } from 'react';
import type { Party, EngineParams, ElectionResults } from '../types';
import { fetchParties } from '../api/parties';
import { runElection } from '../api/election';
import { ParamsEditor, DEFAULT_PARAMS } from './Params';
import ElectionDashboard from '../components/ElectionDashboard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { useToast } from '../components/Toast';
import { useKeyboard } from '../hooks/useKeyboard';

interface RunRecord {
  id: number;
  winner: string;
  winnerShare: number;
  seats: number;
  turnout: number;
  enp: number;
  elapsed: number;
  mc: number;
}

export default function Election() {
  const [parties, setParties] = useState<Party[]>([]);
  const [params, setParams] = useState<EngineParams>(DEFAULT_PARAMS);
  const [results, setResults] = useState<ElectionResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showParams, setShowParams] = useState(false);
  const [runCount, setRunCount] = useState(0);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const [runHistory, setRunHistory] = useState<RunRecord[]>([]);
  const { toast } = useToast();
  const startTimeRef = useRef<number>(0);

  useEffect(() => { fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e)); }, []);

  const handleRun = async () => {
    if (parties.length < 2) {
      setError('Need at least 2 parties. Go to Parties page to add some.');
      return;
    }
    setLoading(true);
    setError(null);
    startTimeRef.current = performance.now();
    try {
      const { n_monte_carlo, seed, ...engineParams } = params;
      const res = await runElection({ params: engineParams, parties, n_monte_carlo, seed });
      const ms = performance.now() - startTimeRef.current;
      setResults(res);
      const newCount = runCount + 1;
      setRunCount(newCount);
      setElapsed(ms);
      const sortedShares = Object.entries(res.national_vote_shares).sort((a, b) => b[1] - a[1]);
      const winnerName = sortedShares[0]?.[0] ?? '';
      setRunHistory(prev => [{
        id: newCount,
        winner: winnerName,
        winnerShare: sortedShares[0]?.[1] ?? 0,
        seats: Math.round(res.seat_counts[winnerName] ?? 0),
        turnout: res.national_turnout,
        enp: res.enp,
        elapsed: ms,
        mc: n_monte_carlo,
      }, ...prev].slice(0, 5));
      toast(`Election complete in ${(ms / 1000).toFixed(1)}s`, 'success');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Election failed');
    }
    setLoading(false);
  };

  const handleRunRef = useCallback(() => {
    if (!loading && parties.length >= 2) handleRun();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, parties.length]);
  useKeyboard({ 'ctrl+enter': handleRunRef }, [handleRunRef]);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          Static Election
          {runCount > 0 && <span className="text-sm text-text-secondary font-normal ml-2">run #{runCount}</span>}
        </h2>
        <div className="flex gap-2 items-center">
          <button onClick={() => setShowParams(!showParams)}
            className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.573-1.066z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {showParams ? 'Hide' : 'Show'} Parameters
          </button>
          <button onClick={handleRun} disabled={loading} title="Run election (Ctrl+Enter)"
            className="px-4 py-1.5 text-sm bg-accent rounded-md hover:bg-accent-hover text-bg-primary font-medium disabled:opacity-50 btn-accent flex items-center gap-2">
            {loading && <div className="animate-spin w-3.5 h-3.5 border-2 border-bg-primary/40 border-t-bg-primary rounded-full" />}
            {loading ? 'Running...' : results ? 'Re-run Election' : 'Run Election'}
          </button>
        </div>
      </div>

      {/* Quick settings bar */}
      <div className="flex items-center gap-4 text-xs">
        <span className="text-text-secondary">{parties.length} parties</span>
        <span className="text-text-secondary/20">|</span>
        <div className="flex items-center gap-1.5">
          <label className="text-text-secondary">MC runs:</label>
          <select value={params.n_monte_carlo}
            onChange={e => setParams({ ...params, n_monte_carlo: parseInt(e.target.value) })}
            className="bg-bg-tertiary border border-bg-quaternary/50 rounded px-1.5 py-0.5 text-xs focus:border-accent transition-colors">
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
        <div className="flex items-center gap-1.5">
          <label className="text-text-secondary">Seed:</label>
          <input type="number" value={params.seed ?? 42}
            onChange={e => setParams({ ...params, seed: parseInt(e.target.value) || 42 })}
            className="w-16 bg-bg-tertiary border border-bg-quaternary/50 rounded px-1.5 py-0.5 text-xs focus:border-accent transition-colors" />
        </div>
        {elapsed != null && (
          <>
            <span className="text-text-secondary/20">|</span>
            <span className="text-text-secondary/50 font-mono">{(elapsed / 1000).toFixed(1)}s</span>
          </>
        )}
        <span className="text-text-secondary/30 ml-auto font-mono text-[10px]">Ctrl+Enter</span>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {showParams && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <ParamsEditor params={params} onChange={setParams} />
        </div>
      )}

      {/* Run History */}
      {runHistory.length > 1 && !loading && (
        <div className="bg-bg-secondary rounded-lg p-3 border border-bg-tertiary/50">
          <h3 className="text-[10px] text-text-secondary/50 uppercase tracking-wider font-medium mb-2">Run History</h3>
          <div className="flex gap-3 overflow-x-auto">
            {runHistory.map((r, i) => (
              <div key={r.id} className={`flex items-center gap-3 px-3 py-1.5 rounded text-xs shrink-0 ${i === 0 ? 'bg-accent/10 border border-accent/20' : 'bg-bg-tertiary/30'}`}>
                <span className="text-text-secondary/40 font-mono">#{r.id}</span>
                <span className="font-medium" style={{ color: parties.find(p => p.name === r.winner)?.color }}>{r.winner}</span>
                <span className="text-text-secondary">{(r.winnerShare * 100).toFixed(1)}%</span>
                <span className="text-text-secondary/40">{r.seats}s</span>
                <span className="text-text-secondary/40">ENP {r.enp.toFixed(2)}</span>
                <span className="text-text-secondary/30 font-mono text-[10px]">{(r.elapsed / 1000).toFixed(1)}s</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && <LoadingSpinner message={`Running ${params.n_monte_carlo} MC runs × ${parties.length} parties × 774 LGAs...`} size="lg" />}

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
            Adjust <span className="text-text-primary font-medium">MC runs</span> above for accuracy vs speed tradeoff.
          </p>
        </div>
      )}
    </div>
  );
}
