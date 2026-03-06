import { NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getCampaignState } from '../api/campaign';

interface NavItem {
  to: string;
  label: string;
  icon: string;
  shortcut: string;
}

const SETUP_ITEMS: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4', shortcut: '1' },
  { to: '/parties', label: 'Parties', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z', shortcut: '2' },
  { to: '/params', label: 'Parameters', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.573-1.066z M15 12a3 3 0 11-6 0 3 3 0 016 0z', shortcut: '3' },
];

const SIM_ITEMS: NavItem[] = [
  { to: '/election', label: 'Election', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', shortcut: '4' },
  { to: '/campaign', label: 'Campaign', icon: 'M13 10V3L4 14h7v7l9-11h-7z', shortcut: '5' },
  { to: '/crises', label: 'Crises', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z', shortcut: '6' },
];

const ANALYSIS_ITEMS: NavItem[] = [
  { to: '/results', label: 'Results', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', shortcut: '7' },
  { to: '/map', label: 'Map', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7', shortcut: '8' },
  { to: '/scenarios', label: 'Scenarios', icon: 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2', shortcut: '9' },
];

const ALL_ITEMS = [...SETUP_ITEMS, ...SIM_ITEMS, ...ANALYSIS_ITEMS];

function NavIcon({ path }: { path: string }) {
  return (
    <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d={path} />
    </svg>
  );
}

function NavSection({ label, items, campaignTurn }: { label: string; items: NavItem[]; campaignTurn?: number | null }) {
  return (
    <div>
      <div className="px-3 pt-3 pb-1">
        <span className="text-[9px] uppercase tracking-[0.15em] text-text-secondary/50 font-medium">{label}</span>
      </div>
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-all duration-150 relative group/nav ${
              isActive
                ? 'bg-accent/10 text-accent font-medium before:absolute before:left-0 before:top-1 before:bottom-1 before:w-[3px] before:bg-accent before:rounded-full'
                : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/30'
            }`
          }
          aria-label={item.label}
        >
          <NavIcon path={item.icon} />
          <span className="tracking-wide flex-1">{item.label}</span>
          {item.to === '/campaign' && campaignTurn != null && campaignTurn > 0 && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-accent/15 text-accent font-mono">T{campaignTurn}</span>
          )}
          <span className="text-[10px] text-text-secondary/30 font-mono opacity-0 group-hover/nav:opacity-100 transition-opacity">{item.shortcut}</span>
        </NavLink>
      ))}
    </div>
  );
}

export default function Sidebar() {
  const navigate = useNavigate();
  const [campaignTurn, setCampaignTurn] = useState<number | null>(null);

  useEffect(() => {
    getCampaignState()
      .then(state => { if (state) setCampaignTurn(state.turn); })
      .catch(() => {});
  }, []);

  // Global number-key navigation (only when no input is focused)
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return;

      const idx = parseInt(e.key) - 1;
      if (idx >= 0 && idx < ALL_ITEMS.length) {
        e.preventDefault();
        navigate(ALL_ITEMS[idx].to);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [navigate]);

  return (
    <aside className="w-56 bg-bg-secondary border-r border-bg-tertiary/40 flex flex-col shrink-0 relative">
      {/* Header */}
      <div className="p-4 border-b border-accent/20">
        <h1 className="text-base font-bold tracking-[0.15em] text-accent uppercase" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
          LAGOS-2058
        </h1>
        <p className="text-[10px] text-text-secondary mt-0.5 tracking-[0.08em] uppercase">Game Master Console</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-1 px-2 overflow-y-auto space-y-1">
        <NavSection label="Setup" items={SETUP_ITEMS} />
        <NavSection label="Simulation" items={SIM_ITEMS} campaignTurn={campaignTurn} />
        <NavSection label="Analysis" items={ANALYSIS_ITEMS} />
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-bg-tertiary/40">
        <div className="text-[10px] text-text-secondary/50 tracking-wider uppercase text-center"
          style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
          v0.1.0 // WAR ROOM
        </div>
        <div className="text-[9px] text-text-secondary/30 text-center mt-1">
          Press 1-9 to navigate
        </div>
      </div>
    </aside>
  );
}
