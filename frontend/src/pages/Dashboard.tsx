import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { fetchParties } from '../api/parties';
import type { Party } from '../types';
import { getCampaignState } from '../api/campaign';
import type { CampaignStateResponse } from '../api/campaign';

const QUICK_START = [
  { to: '/parties', step: '01', title: 'Set Up Parties', desc: 'Create parties or load the 14 example parties', color: '#d4a843', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
  { to: '/params', step: '02', title: 'Configure Parameters', desc: 'Tune the Merrill-Grofman model parameters', color: '#2dd4bf', icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4' },
  { to: '/election', step: '03', title: 'Run Static Election', desc: 'One-shot election with Monte Carlo simulation', color: '#22c55e', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { to: '/campaign', step: '04', title: 'Run Campaign', desc: '12-turn campaign with actions, crises, and strategy', color: '#f59e0b', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { to: '/map', step: '05', title: 'View Map', desc: 'Choropleth map with winner, turnout, and margin views', color: '#3b82f6', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { to: '/results', step: '06', title: 'Campaign Results', desc: 'Detailed results with charts and CSV export', color: '#a855f7', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z' },
];

const SHORTCUTS = [
  { key: '1-9', desc: 'Navigate pages' },
  { key: '?', desc: 'GM Cheat Sheet' },
  { key: 'Esc', desc: 'Close dialogs' },
  { key: 'Ctrl+Enter', desc: 'Run election / advance turn' },
  { key: 'Ctrl+S', desc: 'Save campaign' },
];

const MODEL_STATS = [
  { label: 'Voter Types', value: '174,960', sub: 'ethnic × religious × demographic' },
  { label: 'Issue Dimensions', value: '28', sub: 'spatial voting model' },
  { label: 'Admin Zones', value: '8', sub: 'geopolitical zones' },
  { label: 'States + FCT', value: '38', sub: 'federal divisions' },
  { label: 'LGAs', value: '774', sub: 'local government areas' },
  { label: 'Action Types', value: '14', sub: 'campaign actions' },
  { label: 'Effect Channels', value: '5', sub: 'awareness, salience, valence, ceiling, tau' },
  { label: 'PC per Turn', value: '7', sub: 'political capital income' },
];

export default function Dashboard() {
  const [health, setHealth] = useState<string>('checking...');
  const [parties, setParties] = useState<Party[]>([]);
  const [campaign, setCampaign] = useState<CampaignStateResponse | null>(null);

  useEffect(() => {
    api.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('offline'));
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
    getCampaignState().then(setCampaign).catch(() => {});
  }, []);

  const partyColors: Record<string, string> = Object.fromEntries(parties.map(p => [p.name, p.color]));
  const partyCount = parties.length;

  return (
    <div className="p-8 max-w-5xl">
      {/* Title */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-[0.08em] uppercase"
          style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
          LAGOS-2058
        </h2>
        <p className="text-text-secondary text-sm tracking-wide">Game Master Console — Merrill-Grofman Election Simulator</p>
      </div>

      {/* Status Row */}
      <div className="grid grid-cols-4 gap-4 mb-8">
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
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 card-glow">
          <p className="text-[10px] text-text-secondary mb-1.5 uppercase tracking-[0.12em] font-medium">Campaign</p>
          {campaign && campaign.turn >= 1 ? (
            <Link to="/campaign" className="text-lg font-bold text-accent hover:underline" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
              T{campaign.turn}/{campaign.n_turns}
            </Link>
          ) : (
            <p className="text-lg font-bold text-text-secondary/50" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>—</p>
          )}
        </div>
      </div>

      {/* Active Campaign */}
      {campaign && campaign.turn >= 1 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-accent/20 mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[10px] font-semibold uppercase tracking-[0.12em] text-accent">Active Campaign</h3>
            <span className="text-xs text-text-secondary font-mono">Turn {campaign.turn} / {campaign.n_turns} — {campaign.phase}</span>
          </div>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
              <div className="h-1.5 rounded-full bg-accent transition-all" style={{ width: `${Math.min(((campaign.turn - 1) / campaign.n_turns) * 100, 100)}%` }} />
            </div>
          </div>
          {(() => {
            const sorted = [...campaign.party_statuses].sort((a, b) => b.seats - a.seats || b.vote_share - a.vote_share);
            const top5 = sorted.slice(0, 5);
            return (
              <div className="flex gap-4 flex-wrap">
                {top5.map((ps, i) => {
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
                <Link to="/campaign" className="ml-auto text-xs text-accent hover:underline font-medium">Resume &rarr;</Link>
              </div>
            );
          })()}
        </div>
      )}

      {/* Party Strip */}
      {parties.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/40 mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[10px] font-semibold uppercase tracking-[0.12em] text-text-secondary">{parties.length} Parties Loaded</h3>
            <Link to="/parties" className="text-[10px] text-accent hover:underline font-medium">Edit &rarr;</Link>
          </div>
          <div className="flex gap-1">
            {parties.map(p => (
              <div key={p.name} className="flex-1 group/strip relative" title={`${p.name}${p.full_name ? ` — ${p.full_name}` : ''}`}>
                <div className="h-2 rounded-sm transition-all group-hover/strip:h-4" style={{ backgroundColor: p.color }} />
                <span className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[8px] font-mono text-text-secondary/50 opacity-0 group-hover/strip:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  {p.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Start */}
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/40 mb-8">
        <h3 className="text-[10px] font-semibold mb-4 uppercase tracking-[0.12em] text-text-secondary">Quick Start</h3>
        <div className="grid grid-cols-3 gap-3">
          {QUICK_START.map(item => (
            <Link key={item.to} to={item.to}
              className="group flex gap-3 p-3 rounded-lg border border-bg-tertiary/30 hover:border-accent/30 hover:bg-bg-tertiary/20 transition-all duration-150 card-glow"
            >
              <div className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
                style={{ backgroundColor: item.color + '15' }}>
                <svg className="w-4 h-4" style={{ color: item.color }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}><path d={item.icon} /></svg>
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold group-hover:text-accent transition-colors">{item.title}</p>
                <p className="text-[11px] text-text-secondary mt-0.5 leading-tight">{item.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Model Stats */}
        <div className="bg-bg-secondary rounded-lg p-5 border border-bg-tertiary/40">
          <h3 className="text-[10px] font-semibold text-text-primary mb-4 uppercase tracking-[0.12em]">Model Architecture</h3>
          <div className="grid grid-cols-2 gap-3">
            {MODEL_STATS.map(stat => (
              <div key={stat.label} className="flex items-start gap-2">
                <span className="text-lg font-bold text-accent leading-none mt-0.5" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
                  {stat.value}
                </span>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-text-primary leading-tight">{stat.label}</p>
                  <p className="text-[10px] text-text-secondary leading-tight">{stat.sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shortcuts & Tips */}
        <div className="bg-bg-secondary rounded-lg p-5 border border-bg-tertiary/40">
          <h3 className="text-[10px] font-semibold text-text-primary mb-4 uppercase tracking-[0.12em]">Keyboard Shortcuts</h3>
          <div className="grid grid-cols-2 gap-2">
            {SHORTCUTS.map(s => (
              <div key={s.key} className="flex items-center gap-2">
                <kbd className="px-1.5 py-0.5 bg-bg-tertiary rounded text-[10px] font-mono text-accent border border-bg-quaternary/30 min-w-[3.5rem] text-center shrink-0">{s.key}</kbd>
                <span className="text-xs text-text-secondary">{s.desc}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 pt-4 border-t border-bg-tertiary/30">
            <h4 className="text-[10px] font-semibold text-text-primary mb-2 uppercase tracking-[0.12em]">Tips</h4>
            <div className="space-y-1.5 text-xs text-text-secondary">
              <p>Campaign turns auto-save to history for the Results page</p>
              <p>Use the Map page to visualize geographic patterns</p>
              <p>Export CSV from Results for external analysis</p>
              <p>Save scenarios to compare different campaign strategies</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
