import { useState, useEffect, useMemo, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import type { Party } from '../types';
import { fetchParties } from '../api/parties';
import { getCampaignHistory } from '../api/campaign';
import type { TurnResult } from '../api/campaign';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

export default function Results() {
  const [parties, setParties] = useState<Party[]>([]);
  const [history, setHistory] = useState<TurnResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
    setLoading(true);
    getCampaignHistory()
      .then(setHistory)
      .catch(e => console.error('Failed to fetch campaign history:', e))
      .finally(() => setLoading(false));
  }, []);

  const getColor = useCallback((name: string) => parties.find(p => p.name === name)?.color ?? '#888', [parties]);

  const partyNames = useMemo(() => history.length > 0 ? Object.keys(history[0].national_vote_shares) : [], [history]);
  const topPartyNames = useMemo(() => {
    if (history.length === 0) return [];
    const last = history[history.length - 1];
    return Object.entries(last.national_vote_shares).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([n]) => n);
  }, [history]);

  const voteData = useMemo(() => history.map(h => {
    const entry: Record<string, unknown> = { turn: h.turn };
    for (const [name, share] of Object.entries(h.national_vote_shares)) {
      entry[name] = Math.round(share * 10000) / 100;
    }
    return entry;
  }), [history]);

  const seatData = useMemo(() => history.map(h => {
    const entry: Record<string, unknown> = { turn: h.turn };
    for (const [name, seats] of Object.entries(h.seat_counts)) {
      entry[name] = Math.round(seats * 10) / 10;
    }
    return entry;
  }), [history]);

  const turnoutData = useMemo(() => history.map(h => ({
    turn: h.turn,
    turnout: Math.round(h.national_turnout * 10000) / 100,
  })), [history]);

  const sortedFinal = useMemo(() => {
    if (history.length === 0) return [];
    const final = history[history.length - 1];
    return Object.entries(final.national_vote_shares).sort((a, b) => b[1] - a[1]);
  }, [history]);

  // Swing: compare first turn to last turn (must be before early return - hooks rule)
  const swingData = useMemo(() => {
    if (history.length < 2) return [];
    const first = history[0].national_vote_shares;
    const last = history[history.length - 1].national_vote_shares;
    return Object.keys(last).map(name => ({
      name,
      first: (first[name] ?? 0) * 100,
      last: (last[name] ?? 0) * 100,
      swing: ((last[name] ?? 0) - (first[name] ?? 0)) * 100,
    })).sort((a, b) => b.swing - a.swing);
  }, [history]);

  // Campaign stats (must be before early return - hooks rule)
  const totalActions = useMemo(() => history.reduce((sum, h) => sum + h.actions_resolved.length, 0), [history]);
  const totalSynergies = useMemo(() => history.reduce((sum, h) => sum + h.synergies.length, 0), [history]);
  const totalScandals = useMemo(() => history.reduce((sum, h) => sum + h.scandals.length, 0), [history]);
  const totalPC = useMemo(() => history.reduce((sum, h) => sum + h.actions_resolved.reduce((s, a) => s + Number(a.cost ?? 0), 0), 0), [history]);

  if (history.length === 0) {
    return (
      <div className="p-8 max-w-2xl">
        <h2 className="text-2xl font-bold mb-6">Campaign Results</h2>
        {loading ? (
          <LoadingSpinner message="Loading campaign data..." size="md" />
        ) : (
          <EmptyState
            icon="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"
            title="No campaign data available"
            description="Run a campaign from the Campaign page to see results here."
          />
        )}
      </div>
    );
  }

  const final = history[history.length - 1];

  const margin = sortedFinal.length >= 2
    ? ((sortedFinal[0][1] - sortedFinal[1][1]) * 100).toFixed(1)
    : '0';

  const winnerSeats = Math.round(final.seat_counts[sortedFinal[0][0]] ?? 0);
  const hasMajority = winnerSeats > 387;

  const exportCSV = () => {
    const header = ['Turn', 'Turnout', ...partyNames.map(n => `${n}_VoteShare`), ...partyNames.map(n => `${n}_Seats`)];
    const rows = history.map(h => [
      h.turn,
      (h.national_turnout * 100).toFixed(2),
      ...partyNames.map(n => ((h.national_vote_shares[n] ?? 0) * 100).toFixed(2)),
      ...partyNames.map(n => Math.round(h.seat_counts[n] ?? 0)),
    ]);
    const csv = [header.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `campaign_results_${history.length}turns.csv`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Campaign Results <span className="text-text-secondary font-normal text-base">({history.length} turns)</span></h2>
        <button onClick={exportCSV} className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
          Export CSV
        </button>
      </div>

      {/* Final Summary */}
      <div className="grid grid-cols-5 gap-3">
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-xs text-text-secondary mb-1">Winner</p>
          <p className="text-xl font-bold" style={{ color: getColor(sortedFinal[0][0]) }}>{sortedFinal[0][0]}</p>
          <p className="text-sm text-text-secondary">{(sortedFinal[0][1] * 100).toFixed(1)}% vote share</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-xs text-text-secondary mb-1">Runner-up</p>
          <p className="text-xl font-bold" style={{ color: getColor(sortedFinal[1]?.[0] ?? '') }}>{sortedFinal[1]?.[0]}</p>
          <p className="text-sm text-text-secondary">{((sortedFinal[1]?.[1] ?? 0) * 100).toFixed(1)}%  |  margin: {margin}pp</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-xs text-text-secondary mb-1">Winner Seats</p>
          <p className="text-xl font-bold">{winnerSeats} / 774</p>
          <p className={`text-sm font-medium ${hasMajority ? 'text-success' : 'text-warning'}`}>{hasMajority ? 'Majority' : 'No majority'}</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-xs text-text-secondary mb-1">Final Turnout</p>
          <p className="text-xl font-bold">{(final.national_turnout * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-xs text-text-secondary mb-1">Campaign Stats</p>
          <div className="space-y-0.5 text-xs">
            <p><span className="text-text-secondary">{totalActions}</span> actions ({totalPC} PC)</p>
            <p className="text-success">{totalSynergies} synergies</p>
            <p className="text-danger">{totalScandals} scandals</p>
          </div>
        </div>
      </div>

      {/* Vote Share Evolution */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Vote Share Evolution (%) <span className="font-normal">— top 8 parties</span></h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={voteData}>
            <XAxis dataKey="turn" tick={{ fill: '#8b9bb4', fontSize: 11 }} />
            <YAxis tick={{ fill: '#8b9bb4', fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 11 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {topPartyNames.map(name => (
              <Line key={name} type="monotone" dataKey={name} stroke={getColor(name)}
                strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Seat Evolution */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Seat Count Evolution <span className="font-normal">— top 8 parties</span></h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={seatData}>
            <XAxis dataKey="turn" tick={{ fill: '#8b9bb4', fontSize: 11 }} />
            <YAxis tick={{ fill: '#8b9bb4', fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 11 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {topPartyNames.map(name => (
              <Line key={name} type="monotone" dataKey={name} stroke={getColor(name)}
                strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Turnout Evolution */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">National Turnout (%)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={turnoutData}>
              <XAxis dataKey="turn" tick={{ fill: '#8b9bb4', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8b9bb4', fontSize: 10 }} domain={['auto', 'auto']} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 11 }} />
              <Line type="monotone" dataKey="turnout" stroke="#2dd4bf" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Final Vote Share Bar */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">Final Vote Shares</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sortedFinal.map(([name, share]) => ({ name, share: Math.round(share * 10000) / 100 }))} layout="vertical">
              <XAxis type="number" tick={{ fill: '#8b9bb4', fontSize: 10 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#8b9bb4', fontSize: 10 }} width={50} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 11 }} />
              <Bar dataKey="share">
                {sortedFinal.map(([name], i) => <Cell key={i} fill={getColor(name)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Swing Analysis */}
      {swingData.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">Vote Share Swing <span className="font-normal">— Turn 1 vs Turn {history.length}</span></h3>
          <div className="grid grid-cols-2 gap-x-6 gap-y-1">
            {swingData.slice(0, 8).map(d => (
              <div key={d.name} className="flex items-center gap-2 py-0.5">
                <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: getColor(d.name) }} />
                <span className="text-xs w-12 truncate">{d.name}</span>
                <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full relative overflow-hidden">
                  {d.swing >= 0 ? (
                    <div className="absolute left-1/2 h-full bg-success/60 rounded-r-full" style={{ width: `${Math.min(50, Math.abs(d.swing) * 5)}%` }} />
                  ) : (
                    <div className="absolute right-1/2 h-full bg-danger/60 rounded-l-full" style={{ width: `${Math.min(50, Math.abs(d.swing) * 5)}%` }} />
                  )}
                </div>
                <span className={`text-xs font-mono w-16 text-right ${d.swing > 0 ? 'text-success' : d.swing < 0 ? 'text-danger' : 'text-text-secondary'}`}>
                  {d.swing > 0 ? '+' : ''}{d.swing.toFixed(1)}pp
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Log */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">
          Action Log
          <span className="font-normal text-text-secondary/50 ml-2">{totalActions} actions across {history.length} turns</span>
        </h3>
        <div className="max-h-80 overflow-y-auto space-y-0">
          {history.map((h, idx) => {
            const hasContent = h.actions_resolved.length > 0 || h.synergies.length > 0 || h.scandals.length > 0;
            const turnPC = h.actions_resolved.reduce((s, a) => s + Number(a.cost ?? 0), 0);
            return (
            <div key={h.turn} className={`border-b border-bg-tertiary/30 py-2 px-2 -mx-2 rounded hover:bg-bg-tertiary/20 transition-colors ${idx % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-accent font-mono">Turn {h.turn}</span>
                {hasContent && (
                  <span className="text-[10px] text-text-secondary/40">
                    {h.actions_resolved.length} action{h.actions_resolved.length !== 1 ? 's' : ''}
                    {turnPC > 0 && <span className="ml-1">({turnPC} PC)</span>}
                    {h.synergies.length > 0 && <span className="text-success ml-1">+{h.synergies.length} syn</span>}
                    {h.scandals.length > 0 && <span className="text-danger ml-1">{h.scandals.length} scn</span>}
                  </span>
                )}
              </div>
              {h.actions_resolved.map((a, i) => (
                <div key={i} className="text-xs text-text-secondary ml-3">
                  <span style={{ color: getColor(String(a.party)) }}>{String(a.party)}</span>
                  {' '}{String(a.action_type)} ({String(a.cost)} PC)
                </div>
              ))}
              {h.synergies.map((s, i) => (
                <div key={`syn-${i}`} className="text-xs text-success ml-3">
                  SYNERGY: {String(s.party)} +{Number(s.magnitude).toFixed(2)}
                </div>
              ))}
              {h.scandals.map((s, i) => (
                <div key={`sc-${i}`} className="text-xs text-danger ml-3">
                  SCANDAL: {String(s.party)}
                </div>
              ))}
              {!hasContent && <div className="text-xs text-text-secondary/40 ml-3 italic">No actions</div>}
            </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
