import { useState, useEffect, useCallback } from 'react';

type SheetTab = 'costs' | 'strategy' | 'reference';

const TABS: { key: SheetTab; label: string }[] = [
  { key: 'costs', label: 'PC & Actions' },
  { key: 'strategy', label: 'Strategy' },
  { key: 'reference', label: 'Reference' },
];

export default function CheatSheet() {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(false);
  const [tab, setTab] = useState<SheetTab>('costs');

  const handleClose = useCallback(() => {
    setVisible(false);
    setTimeout(() => setOpen(false), 200);
  }, []);

  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
    }
  }, [open]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) {
        handleClose();
      } else if (e.key === '?' && !open && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement)) {
        setOpen(true);
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [open, handleClose]);

  return (
    <>
      <button onClick={() => setOpen(!open)}
        className="fixed bottom-4 right-4 z-50 w-10 h-10 bg-accent rounded-full flex items-center justify-center text-bg-primary shadow-lg shadow-accent/25 hover:bg-accent-hover hover:shadow-accent/40 transition-all duration-200 text-lg font-bold btn-accent group/help"
        title="GM Cheat Sheet (press ?)"
        style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
        ?
        <span className="absolute bottom-full right-0 mb-2 px-2 py-1 text-[10px] bg-bg-secondary border border-bg-tertiary rounded text-text-secondary whitespace-nowrap opacity-0 group-hover/help:opacity-100 transition-opacity pointer-events-none">
          Press <kbd className="px-1 py-0.5 bg-bg-tertiary rounded text-[9px] font-mono">?</kbd> to open
        </span>
      </button>

      {open && (
        <div
          className={`fixed inset-0 z-40 flex items-center justify-center transition-all duration-200 ${visible ? 'bg-black/60 backdrop-blur-sm' : 'bg-black/0'}`}
          onClick={handleClose}
          role="dialog"
          aria-modal="true"
          aria-label="GM Cheat Sheet"
        >
          <div
            className={`bg-bg-secondary rounded-xl border border-bg-tertiary/50 w-[820px] max-h-[85vh] flex flex-col shadow-2xl shadow-black/40 transition-all duration-200 ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 pt-5 pb-3">
              <h2 className="text-lg font-bold tracking-wide uppercase" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>GM Cheat Sheet</h2>
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-text-secondary/40">ESC to close</span>
                <button onClick={handleClose}
                  aria-label="Close cheat sheet"
                  className="w-7 h-7 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50 transition-colors">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-bg-tertiary px-6">
              {TABS.map(t => (
                <button key={t.key} onClick={() => setTab(t.key)}
                  className={`px-4 py-2 text-sm transition-colors ${tab === t.key ? 'border-b-2 border-accent text-accent font-medium' : 'text-text-secondary hover:text-text-primary'}`}>
                  {t.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {tab === 'costs' && <CostsTab />}
              {tab === 'strategy' && <StrategyTab />}
              {tab === 'reference' && <ReferenceTab />}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function CostsTab() {
  return (
    <div className="grid grid-cols-2 gap-6 text-xs">
      <div>
        <h3 className="text-sm font-semibold mb-2 text-accent">Action Costs</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b border-bg-tertiary">
              <th className="text-left py-1 text-text-secondary/50 text-[10px] uppercase tracking-wider font-medium">Action</th>
              <th className="text-right py-1 text-text-secondary/50 text-[10px] uppercase tracking-wider font-medium">Base PC</th>
              <th className="text-right py-1 text-text-secondary/50 text-[10px] uppercase tracking-wider font-medium">Surcharges</th>
            </tr>
          </thead>
          <tbody>
            {[
              ['rally', '2', ''],
              ['advertising', '2', '+1 if budget>1.5, +2 if >2.0'],
              ['manifesto', '3', ''],
              ['ground_game', '3', '+1 if intensity>1.0, +2 if >1.5'],
              ['endorsement', '2', ''],
              ['ethnic_mobilization', '2', ''],
              ['patronage', '3', '+1 if scale>1.5, +2 if >2.0'],
              ['opposition_research', '2', ''],
              ['media', '1', ''],
              ['eto_engagement', '3', '+1 if score>3.0'],
              ['crisis_response', '2', ''],
              ['fundraising', '0', 'yields +3 PC'],
              ['poll', '1-5', '= poll tier'],
              ['pledge', '1', ''],
              ['eto_intelligence', '0', 'needs ETO >= 5.0'],
            ].map(([name, cost, note], i) => (
              <tr key={name} className={`border-b border-bg-tertiary/30 ${i % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
                <td className="py-1 font-mono">{name}</td>
                <td className="py-1 text-right font-mono text-accent">{cost}</td>
                <td className="py-1 text-right text-text-secondary/60">{note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">PC Economy</h3>
          <div className="space-y-1.5">
            {[
              ['Income', '7 PC/turn (unconditional)'],
              ['Hoarding cap', '18 PC (excess lost before income)'],
              ['Max actions', '3 per party per turn'],
              ['Fundraising', '+3 PC yield'],
              ['ETO dividend', '+1 PC per Economic ETO >= 8.0 (max 2/turn)'],
            ].map(([label, value]) => (
              <div key={label} className="flex gap-2">
                <span className="text-text-secondary/60 w-24 shrink-0">{label}</span>
                <span className="text-text-secondary">{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Effect Channels</h3>
          <div className="space-y-1.5">
            {[
              ['Awareness', 'How well-known party is (floor 0.60, cap 1.0, monotonic)'],
              ['Salience', 'Issue importance shifts (28 dimensions)'],
              ['Valence', 'Party image/competence perception'],
              ['Ceiling', 'Max potential support in a region'],
              ['Tau', 'Turnout sensitivity modifier'],
            ].map(([label, desc]) => (
              <div key={label} className="flex gap-2">
                <span className="text-accent/80 w-20 shrink-0 font-medium">{label}</span>
                <span className="text-text-secondary">{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StrategyTab() {
  return (
    <div className="grid grid-cols-2 gap-6 text-xs">
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Synergy Pairs</h3>
          <div className="space-y-1">
            {[
              ['Rally + Ground Game', '+1.5x awareness', 'success'],
              ['Advertising + Media', '+1.3x salience', 'teal'],
              ['Endorsement + Ethnic Mob', '+1.2x valence', 'warning'],
              ['ETO Engagement + Ground Game', '+1.4x ceiling', 'accent'],
            ].map(([pair, effect, color]) => (
              <div key={pair} className="flex items-center justify-between py-1 border-b border-bg-tertiary/30">
                <span className="text-text-secondary">{pair}</span>
                <span className={`font-mono text-${color}`}>{effect}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Campaign Phases</h3>
          <div className="space-y-1.5">
            {[
              ['T1-3', 'Foundation', 'Build awareness, establish presence'],
              ['T4-6', 'Expansion', 'Broaden reach, build coalitions'],
              ['T7-9', 'Intensification', 'Push salience, attack opponents'],
              ['T10-12', 'Final Push', 'Maximize turnout, close the deal'],
            ].map(([turns, name, desc]) => (
              <div key={turns} className="flex gap-2 items-start">
                <span className="font-mono text-accent/80 w-10 shrink-0">{turns}</span>
                <div>
                  <span className="font-medium text-text-primary">{name}</span>
                  <span className="text-text-secondary/60 ml-1.5">{desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Risk Mechanics</h3>
          <div className="space-y-1.5 text-text-secondary">
            <p><span className="text-warning font-medium">Cohesion:</span> 0-10 scale, +1 recovery/turn. Low cohesion reduces effect magnitudes.</p>
            <p><span className="text-danger font-medium">Exposure:</span> Accumulates from patronage & ethnic_mobilization. -0.1 decay/turn.</p>
            <p><span className="text-danger font-medium">Scandal:</span> Triggers when exposure &gt; 1.8. Severe valence penalty.</p>
            <p><span className="text-warning font-medium">Concentration:</span> 1/(1+0.15*N) diminishing returns for repeat actions.</p>
            <p><span className="text-text-secondary/60">Fatigue:</span> -20% effectiveness per consecutive same-action use.</p>
            <p><span className="text-text-secondary/60">EMA blend:</span> Alpha=0.65, same-key effects overwrite with blend.</p>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Presidential Spread</h3>
          <div className="text-text-secondary space-y-1">
            <p>To win, a candidate needs:</p>
            <p className="font-medium text-text-primary">1. National vote plurality</p>
            <p className="font-medium text-text-primary">2. 25%+ in at least 24 of 38 states</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ReferenceTab() {
  return (
    <div className="space-y-5 text-xs">
      <div>
        <h3 className="text-sm font-semibold mb-2 text-accent">Keyboard Shortcuts</h3>
        <div className="grid grid-cols-3 gap-2">
          {[
            ['1-9', 'Navigate pages'],
            ['?', 'Toggle this cheat sheet'],
            ['Esc', 'Close dialogs'],
            ['Ctrl+Enter', 'Run election / advance turn'],
            ['Ctrl+S', 'Save actions (Campaign)'],
          ].map(([key, desc]) => (
            <div key={key} className="flex items-center gap-2 py-1">
              <kbd className="px-1.5 py-0.5 bg-bg-tertiary border border-bg-quaternary/30 rounded text-[10px] font-mono text-accent min-w-[2rem] text-center">{key}</kbd>
              <span className="text-text-secondary">{desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 text-accent">28 Issue Dimensions</h3>
        <div className="grid grid-cols-4 gap-x-4 gap-y-0.5">
          {[
            '0: sharia_jurisdiction', '1: fiscal_autonomy', '2: chinese_relations', '3: bic_reform',
            '4: ethnic_quotas', '5: fertility_policy', '6: constitutional_structure', '7: resource_revenue',
            '8: housing', '9: education', '10: labor_automation', '11: military_role',
            '12: immigration', '13: language_policy', '14: womens_rights', '15: traditional_authority',
            '16: infrastructure', '17: land_tenure', '18: taxation', '19: agricultural_policy',
            '20: biological_enhancement', '21: trade_policy', '22: environmental_regulation', '23: media_freedom',
            '24: healthcare', '25: pada_status', '26: energy_policy', '27: az_restructuring',
          ].map(dim => (
            <span key={dim} className="text-text-secondary font-mono py-0.5">{dim}</span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Administrative Zones</h3>
          <div className="space-y-0.5">
            {[
              ['1', 'Lagos', 'Southwest urban'],
              ['2', 'Niger', 'Southwest rural'],
              ['3', 'Confluence', 'South-Central'],
              ['4', 'Littoral', 'South-South'],
              ['5', 'Eastern', 'Southeast'],
              ['6', 'Central', 'North-Central'],
              ['7', 'Chad', 'Northeast'],
              ['8', 'Savanna', 'Northwest'],
            ].map(([id, name, desc]) => (
              <div key={id} className="flex gap-2 items-center py-0.5">
                <span className="font-mono text-accent/60 w-4">{id}</span>
                <span className="font-medium w-24">{name}</span>
                <span className="text-text-secondary/60">{desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold mb-2 text-accent">Model Parameters</h3>
          <div className="space-y-0.5 text-text-secondary">
            {[
              ['tau_0', '4.5 (static) / 3.0 (campaign)'],
              ['beta_s', '3.0 — spatial sensitivity'],
              ['alpha_e', '3.0 — ethnic sensitivity'],
              ['alpha_r', '2.0 — religious sensitivity'],
              ['scale', '1.5 — overall vote spread'],
              ['economic_w', '0.3 — economic voting weight'],
              ['voter_rationality', '1.5 — how voters weigh issues'],
            ].map(([param, desc]) => (
              <div key={param} className="flex gap-2 py-0.5">
                <span className="font-mono text-accent/60 w-28 shrink-0">{param}</span>
                <span>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
