import { useEffect, useState } from 'react';
import api from '../api/client';

export default function Dashboard() {
  const [health, setHealth] = useState<string>('checking...');

  useEffect(() => {
    api.get('/health').then(r => setHealth(r.data.status)).catch(() => setHealth('offline'));
  }, []);

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary">
        <p className="text-text-secondary">
          API Status: <span className={health === 'ok' ? 'text-success' : 'text-danger'}>{health}</span>
        </p>
        <p className="text-text-secondary mt-4">
          Welcome to the LAGOS-2058 Game Master Console. Use the sidebar to manage parties,
          configure parameters, run elections, and manage campaigns.
        </p>
      </div>
    </div>
  );
}
