import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { fetchParties } from '../api/parties';

export default function Dashboard() {
  const [health, setHealth] = useState<string>('checking...');
  const [partyCount, setPartyCount] = useState(0);

  useEffect(() => {
    api.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('offline'));
    fetchParties().then(p => setPartyCount(p.length)).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <h2 className="text-2xl font-bold mb-2">LAGOS-2058</h2>
      <p className="text-text-secondary mb-6">Game Master Console</p>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <p className="text-xs text-text-secondary mb-1">API Status</p>
          <p className={`text-lg font-bold ${health === 'ok' ? 'text-success' : 'text-danger'}`}>{health}</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <p className="text-xs text-text-secondary mb-1">Parties Loaded</p>
          <p className="text-lg font-bold">{partyCount}</p>
        </div>
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <p className="text-xs text-text-secondary mb-1">LGAs</p>
          <p className="text-lg font-bold">774</p>
        </div>
      </div>

      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary mb-6">
        <h3 className="text-sm font-semibold mb-3">Quick Start</h3>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/parties" className="block p-3 bg-bg-tertiary/50 rounded hover:bg-bg-tertiary transition-colors">
            <p className="text-sm font-semibold">1. Set Up Parties</p>
            <p className="text-xs text-text-secondary">Create parties or load the 14 example parties</p>
          </Link>
          <Link to="/params" className="block p-3 bg-bg-tertiary/50 rounded hover:bg-bg-tertiary transition-colors">
            <p className="text-sm font-semibold">2. Configure Parameters</p>
            <p className="text-xs text-text-secondary">Tune the Merrill-Grofman model parameters</p>
          </Link>
          <Link to="/election" className="block p-3 bg-bg-tertiary/50 rounded hover:bg-bg-tertiary transition-colors">
            <p className="text-sm font-semibold">3. Run Static Election</p>
            <p className="text-xs text-text-secondary">One-shot election with Monte Carlo simulation</p>
          </Link>
          <Link to="/campaign" className="block p-3 bg-bg-tertiary/50 rounded hover:bg-bg-tertiary transition-colors">
            <p className="text-sm font-semibold">4. Run Campaign</p>
            <p className="text-xs text-text-secondary">12-turn campaign with actions, crises, and strategy</p>
          </Link>
        </div>
      </div>

      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary text-xs text-text-secondary space-y-2">
        <h3 className="text-sm font-semibold text-text-primary mb-2">System Info</h3>
        <p>Model: Merrill-Grofman spatial voting, 28 issue dimensions</p>
        <p>Voter types: 174,960 (ethnic x religious x demographic profiles)</p>
        <p>Administrative zones: 8 | States: 38 | LGAs: 774</p>
        <p>Campaign: 5 effect channels, 14 action types, PC economy</p>
        <p className="mt-2">Press the <span className="text-accent">?</span> button for the GM Cheat Sheet</p>
      </div>
    </div>
  );
}
