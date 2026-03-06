import { useState, useEffect, useMemo, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import type { Party } from '../types';
import { fetchParties } from '../api/parties';
import { getCampaignHistory } from '../api/campaign';
import type { TurnResult } from '../api/campaign';

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

  if (history.length === 0) {
    return (
      <div className="p-8 max-w-2xl">
        <h2 className="text-2xl font-bold mb-6">Campaign Results</h2>
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="animate-spin w-10 h-10 border-[3px] border-accent/30 border-t-accent rounded-full mx-auto mb-4" />
              <p className="text-text-secondary font-medium">Loading campaign data...</p>
            </div>
          </div>
        ) : (
          <div className="bg-bg-secondary rounded-lg p-8 border border-bg-tertiary/50 text-center">
            <svg className="w-12 h-12 text-text-secondary/40 mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
              <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
            </svg>
            <p className="text-text-secondary mb-1">No campaign data available</p>
            <p className="text-xs text-text-secondary/60">Run a campaign from the Campaign page to see results here.</p>
          </div>
        )}
      </div>
    );
  }

  const final = history[history.length - 1];

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Campaign Results ({history.length} turns)</h2>

      {/* Final Summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1">Winner</p>
          <p className="text-xl font-bold" style={{ color: getColor(sortedFinal[0][0]) }}>{sortedFinal[0][0]}</p>
          <p className="text-sm text-text-secondary">{(sortedFinal[0][1] * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1">Runner-up</p>
          <p className="text-xl font-bold" style={{ color: getColor(sortedFinal[1]?.[0] ?? '') }}>{sortedFinal[1]?.[0]}</p>
          <p className="text-sm text-text-secondary">{((sortedFinal[1]?.[1] ?? 0) * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1">Final Turnout</p>
          <p className="text-xl font-bold">{(final.national_turnout * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1">Winner Seats</p>
          <p className="text-xl font-bold">{Math.round(final.seat_counts[sortedFinal[0][0]] ?? 0)} / 774</p>
        </div>
      </div>

      {/* Vote Share Evolution */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Vote Share Evolution (%)</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={voteData}>
            <XAxis dataKey="turn" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9', fontSize: 11 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {partyNames.map(name => (
              <Line key={name} type="monotone" dataKey={name} stroke={getColor(name)}
                strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Seat Evolution */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Seat Count Evolution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={seatData}>
            <XAxis dataKey="turn" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9', fontSize: 11 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {partyNames.map(name => (
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
              <XAxis dataKey="turn" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['auto', 'auto']} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9', fontSize: 11 }} />
              <Line type="monotone" dataKey="turnout" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Final Vote Share Bar */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">Final Vote Shares</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sortedFinal.map(([name, share]) => ({ name, share: Math.round(share * 10000) / 100 }))} layout="vertical">
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} width={50} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9', fontSize: 11 }} />
              <Bar dataKey="share">
                {sortedFinal.map(([name], i) => <Cell key={i} fill={getColor(name)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Action Log */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Action Log</h3>
        <div className="max-h-64 overflow-y-auto space-y-0">
          {history.map((h, idx) => {
            const hasContent = h.actions_resolved.length > 0 || h.synergies.length > 0 || h.scandals.length > 0;
            return (
            <div key={h.turn} className={`border-b border-bg-tertiary/30 py-2 px-2 -mx-2 rounded hover:bg-bg-tertiary/20 transition-colors ${idx % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
              <div className="text-xs font-semibold mb-1 text-accent font-mono">Turn {h.turn}</div>
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
