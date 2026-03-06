import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { fetchParties } from '../api/parties';
import { getCampaignState } from '../api/campaign';
import type { CampaignStateResponse } from '../api/campaign';

const QUICK_START = [
  { to: '/parties', step: '01', title: 'Set Up Parties', desc: 'Create parties or load the 14 example parties', color: '#d4a843' },
  { to: '/params', step: '02', title: 'Configure Parameters', desc: 'Tune the Merrill-Grofman model parameters', color: '#2dd4bf' },
  { to: '/election', step: '03', title: 'Run Static Election', desc: 'One-shot election with Monte Carlo simulation', color: '#22c55e' },
  { to: '/campaign', step: '04', title: 'Run Campaign', desc: '12-turn campaign with actions, crises, and strategy', color: '#f59e0b' },
];

export default function Dashboard() {
  const [health, setHealth] = useState<string>('checking...');
  const [partyCount, setPartyCount] = useState(0);
  const [campaign, setCampaign] = useState<CampaignStateResponse | null>(null);
  const [partyColors, setPartyColors] = useState<Record<string, string>>({});

  useEffect(() => {
    api.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('offline'));
    fetchParties().then(p => {
      setPartyCount(p.length);
      setPartyColors(Object.fromEntries(p.map(pp => [pp.name, pp.color])));
    }).catch(e => console.error('Failed to fetch parties:', e));
    getCampaignState().then(setCampaign).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      {/* Title */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-[0.08em] uppercase"
          style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
          LAGOS-2058
        </h2>
        <p className="text-text-secondary text-sm tracking-wide">Game Master Console</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-[10px] text-text-secondary mb-1.5 uppercase tracking-[0.12em] font-medium">API Status</p>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${health === 'ok' ? 'bg-success animate-pulse' : 'bg-danger'}`} />
            <p className={`text-lg font-bold tracking-wider uppercase ${health === 'ok' ? 'text-success' : 'text-danger'}`}
              style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
              {health}
            </p>
          </div>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-[10px] text-text-secondary mb-1.5 uppercase tracking-[0.12em] font-medium">Parties Loaded</p>
          <p className="text-lg font-bold" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>{partyCount}</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-[10px] text-text-secondary mb-1.5 uppercase tracking-[0.12em] font-medium">LGAs</p>
          <p className="text-lg font-bold" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>774</p>
        </div>
      </div>

      {/* Active Campaign */}
      {campaign && campaign.turn >= 1 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-accent/20 mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[10px] font-semibold uppercase tracking-[0.12em] text-accent">Active Campaign</h3>
            <span className="text-xs text-text-secondary font-mono">Turn {campaign.turn} / {campaign.n_turns}</span>
          </div>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
              <div className="h-1.5 rounded-full bg-accent transition-all" style={{ width: `${Math.min(((campaign.turn - 1) / campaign.n_turns) * 100, 100)}%` }} />
            </div>
            <span className="text-xs font-medium text-accent">{campaign.phase}</span>
          </div>
          {(() => {
            const sorted = [...campaign.party_statuses].sort((a, b) => b.seats - a.seats || b.vote_share - a.vote_share);
            const top3 = sorted.slice(0, 3);
            return (
              <div className="flex gap-4">
                {top3.map((ps, i) => {
                  const color = partyColors[ps.name] ?? '#888';
                  return (
                    <div key={ps.name} className="flex items-center gap-2 text-xs">
                      <span className="font-mono text-text-secondary w-3">{i + 1}.</span>
                      <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
                      <span className="font-semibold" style={{ color }}>{ps.name}</span>
                      <span className="text-text-secondary">{ps.seats > 0 ? `${ps.seats.toFixed(0)} seats` : `${(ps.vote_share * 100).toFixed(1)}%`}</span>
                    </div>
                  );
                })}
                <Link to="/campaign" className="ml-auto text-xs text-accent hover:underline">Resume &rarr;</Link>
              </div>
            );
          })()}
        </div>
      )}

      {/* Quick Start */}
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/40 mb-8">
        <h3 className="text-[10px] font-semibold mb-4 uppercase tracking-[0.12em] text-text-secondary">Quick Start</h3>
        <div className="grid grid-cols-2 gap-3">
          {QUICK_START.map(item => (
            <Link key={item.to} to={item.to}
              className="group flex gap-3 p-3 rounded-lg border border-bg-tertiary/30 hover:border-accent/30 hover:bg-bg-tertiary/20 transition-all duration-150 card-glow"
            >
              <div className="w-8 h-8 rounded-md flex items-center justify-center text-xs font-bold shrink-0"
                style={{ backgroundColor: item.color + '15', color: item.color, fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
                {item.step}
              </div>
              <div>
                <p className="text-sm font-semibold group-hover:text-accent transition-colors">{item.title}</p>
                <p className="text-xs text-text-secondary mt-0.5">{item.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* System Info */}
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/40 text-xs text-text-secondary space-y-2">
        <h3 className="text-[10px] font-semibold text-text-primary mb-3 uppercase tracking-[0.12em]">System Info</h3>
        <p>Model: Merrill-Grofman spatial voting, 28 issue dimensions</p>
        <p>Voter types: 174,960 (ethnic x religious x demographic profiles)</p>
        <p>Administrative zones: 8 | States: 38 | LGAs: 774</p>
        <p>Campaign: 5 effect channels, 14 action types, PC economy</p>
        <p className="mt-3 pt-2 border-t border-bg-tertiary/30">Press the <span className="text-accent font-medium">?</span> button for the GM Cheat Sheet</p>
      </div>
    </div>
  );
}
