import { useMemo } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ResponsiveContainer } from 'recharts';
import type { Party } from '../types';

interface Props {
  parties: Party[];
  issueNames: string[];
}

export default function PartyComparison({ parties, issueNames }: Props) {
  if (parties.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <svg className="w-12 h-12 text-text-secondary/30 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
          <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4-4v2m8-4a4 4 0 100-8 4 4 0 000 8zm6 0a3 3 0 100-6 3 3 0 000 6z" />
        </svg>
        <p className="text-text-secondary mb-1">No parties selected</p>
        <p className="text-xs text-text-secondary/60">Check the boxes next to parties in the list to compare them.</p>
      </div>
    );
  }

  // Most divergent dimensions — highest std dev across selected parties
  const divergentDims = useMemo(() => {
    if (parties.length < 2) return [];
    return issueNames.map((name, idx) => {
      const vals = parties.map(p => p.positions[idx] ?? 0);
      const mean = vals.reduce((s, v) => s + v, 0) / vals.length;
      const variance = vals.reduce((s, v) => s + (v - mean) ** 2, 0) / vals.length;
      return { name, idx, stdDev: Math.sqrt(variance), mean };
    }).sort((a, b) => b.stdDev - a.stdDev).slice(0, 5);
  }, [parties, issueNames]);

  // Show at most 10 dimensions for readability in radar
  const step = Math.max(1, Math.floor(issueNames.length / 10));
  const selectedDims = issueNames.filter((_, i) => i % step === 0).slice(0, 12);
  const selectedIndices = selectedDims.map(name => issueNames.indexOf(name));

  const data = selectedDims.map((name, i) => {
    const entry: Record<string, unknown> = { dimension: name.replace(/_/g, ' ') };
    parties.forEach(p => {
      // Normalize from [-5,5] to [0,10] for radar
      entry[p.name] = (p.positions[selectedIndices[i]] ?? 0) + 5;
    });
    return entry;
  });

  return (
    <div className="space-y-5">
      {/* Party Attributes Summary */}
      <div>
        <h4 className="text-sm font-semibold mb-3 text-text-secondary">Party Attributes</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-bg-tertiary">
                <th className="text-left py-1.5 px-2 text-text-secondary">Attribute</th>
                {parties.map(p => (
                  <th key={p.name} className="text-center py-1.5 px-2 font-semibold" style={{ color: p.color }}>
                    <div className="flex items-center justify-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: p.color }} />
                      {p.name}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-bg-tertiary/30">
                <td className="py-1 px-2 text-text-secondary">Full Name</td>
                {parties.map(p => <td key={p.name} className="text-center py-1 px-2 text-text-primary">{p.full_name || '—'}</td>)}
              </tr>
              <tr className="border-b border-bg-tertiary/30 bg-bg-tertiary/10">
                <td className="py-1 px-2 text-text-secondary">Valence</td>
                {parties.map(p => (
                  <td key={p.name} className={`text-center py-1 px-2 font-mono ${p.valence > 0 ? 'text-success' : p.valence < 0 ? 'text-danger' : 'text-text-secondary'}`}>
                    {p.valence > 0 ? '+' : ''}{p.valence.toFixed(2)}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-bg-tertiary/30">
                <td className="py-1 px-2 text-text-secondary">Leader Ethnicity</td>
                {parties.map(p => <td key={p.name} className="text-center py-1 px-2">{p.leader_ethnicity || '—'}</td>)}
              </tr>
              <tr className="border-b border-bg-tertiary/30 bg-bg-tertiary/10">
                <td className="py-1 px-2 text-text-secondary">Religion</td>
                {parties.map(p => <td key={p.name} className="text-center py-1 px-2">{p.religious_alignment || '—'}</td>)}
              </tr>
              <tr className="border-b border-bg-tertiary/30">
                <td className="py-1 px-2 text-text-secondary">Econ Position</td>
                {parties.map(p => (
                  <td key={p.name} className="text-center py-1 px-2 font-mono">
                    {p.economic_positioning.toFixed(1)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Most Divergent Dimensions */}
      {divergentDims.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold mb-3 text-text-secondary">Most Divergent Issues</h4>
          <div className="space-y-1.5">
            {divergentDims.map(d => (
              <div key={d.name} className="flex items-center gap-3 text-xs">
                <span className="w-40 truncate text-text-secondary">{d.name}</span>
                <div className="flex-1 flex items-center gap-1">
                  {parties.map(p => {
                    const v = p.positions[d.idx] ?? 0;
                    const pct = ((v + 5) / 10) * 100;
                    return (
                      <div key={p.name} className="relative flex-1 h-4 bg-bg-tertiary/30 rounded-sm">
                        <div className="absolute top-0.5 w-2 h-3 rounded-sm" style={{
                          left: `${Math.max(0, Math.min(95, pct))}%`,
                          backgroundColor: p.color,
                        }} />
                      </div>
                    );
                  })}
                </div>
                <span className="text-text-secondary/40 font-mono w-10 text-right" title="Standard deviation">{d.stdDev.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Radar Chart */}
      <div>
        <h4 className="text-sm font-semibold mb-2 text-text-secondary">Position Comparison (normalized 0-10)</h4>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={data}>
            <PolarGrid stroke="#1f2937" />
            <PolarAngleAxis dataKey="dimension" tick={{ fill: '#8b9bb4', fontSize: 10 }} />
            <PolarRadiusAxis domain={[0, 10]} tick={{ fill: '#6b7a8d', fontSize: 9 }} />
            {parties.map(p => (
              <Radar key={p.name} name={p.name} dataKey={p.name}
                stroke={p.color} fill={p.color} fillOpacity={0.1} />
            ))}
            <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Heatmap table */}
      <div>
        <h4 className="text-sm font-semibold mb-2 text-text-secondary">Full Position Heatmap</h4>
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-bg-primary">
              <tr className="border-b border-bg-tertiary">
                <th className="text-left py-1 px-2 text-text-secondary">Dimension</th>
                {parties.map(p => (
                  <th key={p.name} className="text-center py-1 px-2" style={{ color: p.color }}>{p.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {issueNames.map((name, idx) => (
                <tr key={name} className={`border-b border-bg-tertiary/30 ${idx % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
                  <td className="py-0.5 px-2 text-text-secondary">{name}</td>
                  {parties.map(p => {
                    const v = p.positions[idx] ?? 0;
                    const bg = v > 0 ? `rgba(59,130,246,${Math.abs(v) / 8})` : v < 0 ? `rgba(239,68,68,${Math.abs(v) / 8})` : 'transparent';
                    return (
                      <td key={p.name} className="text-center py-0.5 px-2" style={{ backgroundColor: bg }}>
                        {v.toFixed(1)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
