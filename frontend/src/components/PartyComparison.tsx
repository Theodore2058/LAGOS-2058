import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ResponsiveContainer } from 'recharts';
import type { Party } from '../types';

interface Props {
  parties: Party[];
  issueNames: string[];
}

export default function PartyComparison({ parties, issueNames }: Props) {
  if (parties.length === 0) {
    return <p className="text-text-secondary text-sm">Select parties to compare.</p>;
  }

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
    <div>
      <h4 className="text-sm font-semibold mb-2 text-text-secondary">Position Comparison (normalized 0-10)</h4>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="dimension" tick={{ fill: '#94a3b8', fontSize: 10 }} />
          <PolarRadiusAxis domain={[0, 10]} tick={{ fill: '#64748b', fontSize: 9 }} />
          {parties.map(p => (
            <Radar key={p.name} name={p.name} dataKey={p.name}
              stroke={p.color} fill={p.color} fillOpacity={0.1} />
          ))}
          <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
        </RadarChart>
      </ResponsiveContainer>

      {/* Heatmap table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-bg-tertiary">
              <th className="text-left py-1 px-2 text-text-secondary">Dimension</th>
              {parties.map(p => (
                <th key={p.name} className="text-center py-1 px-2" style={{ color: p.color }}>{p.name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {issueNames.map((name, idx) => (
              <tr key={name} className="border-b border-bg-tertiary/30">
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
  );
}
