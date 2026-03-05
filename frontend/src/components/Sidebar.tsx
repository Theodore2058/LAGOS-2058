import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '◉' },
  { to: '/parties', label: 'Parties', icon: '⚑' },
  { to: '/params', label: 'Parameters', icon: '⚙' },
  { to: '/election', label: 'Election', icon: '✓' },
  { to: '/campaign', label: 'Campaign', icon: '▶' },
  { to: '/crises', label: 'Crises', icon: '!' },
  { to: '/results', label: 'Results', icon: '◧' },
  { to: '/map', label: 'Map', icon: '◰' },
  { to: '/scenarios', label: 'Scenarios', icon: '◫' },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-bg-secondary border-r border-bg-tertiary flex flex-col shrink-0">
      <div className="p-4 border-b border-bg-tertiary">
        <h1 className="text-lg font-bold tracking-wide text-accent">LAGOS-2058</h1>
        <p className="text-xs text-text-secondary mt-1">Game Master Console</p>
      </div>
      <nav className="flex-1 py-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? 'bg-accent/15 text-accent border-r-2 border-accent'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50'
              }`
            }
          >
            <span className="text-base w-5 text-center">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-bg-tertiary text-xs text-text-secondary">
        v0.1.0
      </div>
    </aside>
  );
}
