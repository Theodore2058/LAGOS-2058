import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { fetchParties } from '../api/parties';

const QUICK_START = [
  { to: '/parties', step: '1', title: 'Set Up Parties', desc: 'Create parties or load the 14 example parties', color: '#3b82f6' },
  { to: '/params', step: '2', title: 'Configure Parameters', desc: 'Tune the Merrill-Grofman model parameters', color: '#8b5cf6' },
  { to: '/election', step: '3', title: 'Run Static Election', desc: 'One-shot election with Monte Carlo simulation', color: '#22c55e' },
  { to: '/campaign', step: '4', title: 'Run Campaign', desc: '12-turn campaign with actions, crises, and strategy', color: '#f59e0b' },
];

export default function Dashboard() {
  const [health, setHealth] = useState<string>('checking...');
  const [partyCount, setPartyCount] = useState(0);

  useEffect(() => {
    api.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('offline'));
    fetchParties().then(p => setPartyCount(p.length)).catch(e => console.error('Failed to fetch parties:', e));
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <h2 className="text-2xl font-bold mb-1">LAGOS-2058</h2>
      <p className="text-text-secondary mb-8">Game Master Console</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1.5 uppercase tracking-wider">API Status</p>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${health === 'ok' ? 'bg-success animate-pulse' : 'bg-danger'}`} />
            <p className={`text-lg font-bold ${health === 'ok' ? 'text-success' : 'text-danger'}`}>{health}</p>
          </div>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1.5 uppercase tracking-wider">Parties Loaded</p>
          <p className="text-lg font-bold">{partyCount}</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors">
          <p className="text-xs text-text-secondary mb-1.5 uppercase tracking-wider">LGAs</p>
          <p className="text-lg font-bold">774</p>
        </div>
      </div>

      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/50 mb-8">
        <h3 className="text-sm font-semibold mb-4 uppercase tracking-wider text-text-secondary">Quick Start</h3>
        <div className="grid grid-cols-2 gap-3">
          {QUICK_START.map(item => (
            <Link key={item.to} to={item.to}
              className="group flex gap-3 p-3 rounded-lg border border-bg-tertiary/30 hover:border-bg-quaternary/50 hover:bg-bg-tertiary/20 transition-all duration-150"
            >
              <div className="w-8 h-8 rounded-md flex items-center justify-center text-sm font-bold shrink-0 text-white"
                style={{ backgroundColor: item.color + '20', color: item.color }}>
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

      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/50 text-xs text-text-secondary space-y-2">
        <h3 className="text-sm font-semibold text-text-primary mb-3 uppercase tracking-wider">System Info</h3>
        <p>Model: Merrill-Grofman spatial voting, 28 issue dimensions</p>
        <p>Voter types: 174,960 (ethnic x religious x demographic profiles)</p>
        <p>Administrative zones: 8 | States: 38 | LGAs: 774</p>
        <p>Campaign: 5 effect channels, 14 action types, PC economy</p>
        <p className="mt-3 pt-2 border-t border-bg-tertiary/30">Press the <span className="text-accent font-medium">?</span> button for the GM Cheat Sheet</p>
      </div>
    </div>
  );
}
