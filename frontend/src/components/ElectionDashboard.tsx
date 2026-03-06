import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { Party, ElectionResults } from '../types';
import { ADMIN_ZONES } from '../types';

interface Props {
  results: ElectionResults;
  parties: Party[];
}

function getPartyColor(parties: Party[], name: string): string {
  return parties.find(p => p.name === name)?.color ?? '#888888';
}

export default function ElectionDashboard({ results, parties }: Props) {
  const sortedParties = Object.entries(results.national_vote_shares)
    .sort((a, b) => b[1] - a[1]);

  const winner = sortedParties[0];
  const winnerColor = getPartyColor(parties, winner[0]);

  // Vote share bar chart data
  const voteData = sortedParties.map(([name, share]) => ({
    name,
    share: Math.round(share * 10000) / 100,
    color: getPartyColor(parties, name),
  }));

  // Seat data
  const seatData = Object.entries(results.seat_counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, seats]) => ({
      name,
      seats: Math.round(seats * 10) / 10,
      std: results.seat_std[name] ?? 0,
      color: getPartyColor(parties, name),
    }));

  return (
    <div className="space-y-6">
      {/* Summary Bar */}
      <div className="grid grid-cols-5 gap-4">
        <SummaryCard label="Winner" value={winner[0]} color={winnerColor} />
        <SummaryCard label="Win Probability" value={`${Math.round((results.win_probability[winner[0]] ?? 0) * 100)}%`} />
        <SummaryCard label="Winner Seats" value={`${Math.round(results.seat_counts[winner[0]] ?? 0)} / 774`} />
        <SummaryCard label="Turnout" value={`${(results.national_turnout * 100).toFixed(1)}%`} />
        <SummaryCard label="ENP" value={results.enp.toFixed(2)} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Vote Share Bar Chart */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">National Vote Shares (%)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={voteData} layout="vertical">
              <XAxis type="number" tick={{ fill: '#8b9bb4', fontSize: 10 }} domain={[0, 'auto']} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#8b9bb4', fontSize: 11 }} width={50} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 12 }} />
              <Bar dataKey="share" name="Vote %">
                {voteData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Seat Allocation */}
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">Seat Allocation (774 LGAs)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={seatData} layout="vertical">
              <XAxis type="number" tick={{ fill: '#8b9bb4', fontSize: 10 }} domain={[0, 'auto']} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#8b9bb4', fontSize: 11 }} width={50} />
              <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', color: '#e8e0d4', fontSize: 12 }}
                formatter={(value: number | undefined, _name: string | undefined, props: { payload?: { std?: number } }) =>
                  [`${Number(value ?? 0).toFixed(1)} (±${Number(props?.payload?.std ?? 0).toFixed(1)})`, 'Seats']} />
              <Bar dataKey="seats" name="Mean Seats">
                {seatData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Presidential Spread */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Presidential Spread Check (need 25% in 24+ states)</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(results.spread_check)
            .sort((a, b) => b[1].states_above_25 - a[1].states_above_25)
            .map(([name, sc]) => (
              <div key={name} className="flex items-center gap-3 py-1">
                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: getPartyColor(parties, name) }} />
                <span className="w-12 text-xs font-mono">{name}</span>
                <div className="flex-1 bg-bg-tertiary rounded-full h-2 relative">
                  <div className="h-2 rounded-full transition-all"
                    style={{
                      width: `${(sc.states_above_25 / 38) * 100}%`,
                      backgroundColor: sc.met ? '#22c55e' : getPartyColor(parties, name),
                    }} />
                  <div className="absolute top-0 h-2 w-px bg-warning" style={{ left: `${(24 / 38) * 100}%` }} />
                </div>
                <span className={`text-xs w-10 text-right ${sc.met ? 'text-success' : 'text-text-secondary'}`}>
                  {sc.states_above_25}/38
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Zonal Breakdown */}
      <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 overflow-x-auto">
        <h3 className="text-sm font-semibold mb-3 text-text-secondary">Zonal Breakdown</h3>
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-bg-tertiary">
              <th className="text-left py-1.5 px-2">Zone</th>
              <th className="text-right py-1.5 px-2">Turnout</th>
              {sortedParties.slice(0, 8).map(([name]) => (
                <th key={name} className="text-right py-1.5 px-2" style={{ color: getPartyColor(parties, name) }}>{name}</th>
              ))}
              <th className="text-right py-1.5 px-2">Winner</th>
            </tr>
          </thead>
          <tbody>
            {results.zonal_results.map((z, i) => (
              <tr key={z.az} className={`border-b border-bg-tertiary/30 hover:bg-bg-tertiary/20 transition-colors ${i % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
                <td className="py-1.5 px-2 font-medium">{z.az_name || ADMIN_ZONES[z.az]}</td>
                <td className="text-right py-1 px-2">{(z.turnout * 100).toFixed(1)}%</td>
                {sortedParties.slice(0, 8).map(([name]) => (
                  <td key={name} className="text-right py-1 px-2">{((z.vote_shares[name] ?? 0) * 100).toFixed(1)}%</td>
                ))}
                <td className="text-right py-1 px-2 font-semibold" style={{ color: getPartyColor(parties, z.winner) }}>
                  {z.winner}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Swing LGAs */}
      {results.swing_lgas.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-3 text-text-secondary">Swing LGAs (margin &lt; 5%)</h3>
          <div className="max-h-64 overflow-y-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-bg-tertiary sticky top-0 bg-bg-secondary">
                  <th className="text-left py-1.5 px-2">LGA</th>
                  <th className="text-left py-1.5 px-2">State</th>
                  <th className="text-right py-1.5 px-2">Margin</th>
                  <th className="text-left py-1.5 px-2">Top Parties</th>
                </tr>
              </thead>
              <tbody>
                {results.swing_lgas.slice(0, 50).map((s, i) => (
                  <tr key={i} className={`border-b border-bg-tertiary/30 hover:bg-bg-tertiary/20 transition-colors ${i % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
                    <td className="py-1 px-2 font-medium">{s.lga}</td>
                    <td className="py-1 px-2">{s.state}</td>
                    <td className="text-right py-1 px-2">{(s.margin * 100).toFixed(2)}%</td>
                    <td className="py-1 px-2">{s.top_parties.join(' vs ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
      <p className="text-[10px] text-text-secondary mb-1.5 uppercase tracking-[0.12em] font-medium">{label}</p>
      <p className="text-xl font-bold" style={{ ...(color ? { color } : {}), fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>{value}</p>
    </div>
  );
}
