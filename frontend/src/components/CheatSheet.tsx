import { useState, useEffect } from 'react';

export default function CheatSheet() {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
    }
  }, [open]);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => setOpen(false), 200);
  };

  return (
    <>
      <button onClick={() => setOpen(!open)}
        className="fixed bottom-4 right-4 z-50 w-10 h-10 bg-accent rounded-full flex items-center justify-center text-white shadow-lg shadow-accent/20 hover:bg-accent-hover hover:shadow-accent/30 transition-all duration-200 text-lg font-medium"
        title="GM Cheat Sheet">
        ?
      </button>

      {open && (
        <div
          className={`fixed inset-0 z-40 flex items-center justify-center transition-all duration-200 ${visible ? 'bg-black/60 backdrop-blur-sm' : 'bg-black/0'}`}
          onClick={handleClose}
        >
          <div
            className={`bg-bg-secondary rounded-xl border border-bg-tertiary/50 w-[800px] max-h-[80vh] overflow-y-auto p-6 shadow-2xl shadow-black/40 transition-all duration-200 ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold">GM Cheat Sheet</h2>
              <button onClick={handleClose}
                className="w-7 h-7 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-6 text-xs">
              {/* PC Costs */}
              <div>
                <h3 className="text-sm font-semibold mb-2 text-accent">PC Costs</h3>
                <table className="w-full">
                  <tbody>
                    {[
                      ['rally', '2'], ['advertising', '2 (+1 if budget>1.5, +2 if >2.0)'],
                      ['manifesto', '3'], ['ground_game', '3 (+1 if intensity>1.0, +2 if >1.5)'],
                      ['endorsement', '2'], ['ethnic_mobilization', '2'],
                      ['patronage', '3 (+1 if scale>1.5, +2 if >2.0)'], ['opposition_research', '2'],
                      ['media', '1'], ['eto_engagement', '3 (+1 if score>3.0)'],
                      ['crisis_response', '2'], ['fundraising', '0 (yields +3 PC)'],
                      ['poll', '1-5 (= tier)'], ['pledge', '1'],
                      ['eto_intelligence', '0 (needs ETO >= 5.0)'],
                    ].map(([name, cost]) => (
                      <tr key={name} className="border-b border-bg-tertiary/30 hover:bg-bg-tertiary/20">
                        <td className="py-1 font-mono">{name}</td>
                        <td className="py-1 text-right text-text-secondary">{cost}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* PC System */}
              <div>
                <h3 className="text-sm font-semibold mb-2 text-accent">PC System</h3>
                <div className="space-y-1 text-text-secondary">
                  <p>Income: 7 PC/turn (unconditional)</p>
                  <p>Hoarding cap: 18 PC (excess lost before income)</p>
                  <p>Fundraising yield: +3 PC</p>
                  <p>{'ETO dividend: +1 PC per Economic ETO >= 8.0 (max 2/turn)'}</p>
                </div>

                <h3 className="text-sm font-semibold mb-2 mt-4 text-accent">Synergy Pairs</h3>
                <div className="space-y-1 text-text-secondary">
                  <p>Rally + Ground Game = +1.5x awareness</p>
                  <p>Advertising + Media = +1.3x salience</p>
                  <p>Endorsement + Ethnic Mob = +1.2x valence</p>
                  <p>ETO Engagement + Ground Game = +1.4x ceiling</p>
                </div>

                <h3 className="text-sm font-semibold mb-2 mt-4 text-accent">Thresholds</h3>
                <div className="space-y-1 text-text-secondary">
                  <p>Awareness: floor 0.60, cap 1.0 (monotonic)</p>
                  <p>Cohesion: 0-10, +1 recovery/turn</p>
                  <p>Exposure decay: -0.1/turn</p>
                  <p>Scandal threshold: exposure &gt; 1.8</p>
                  <p>Concentration penalty: 1/(1+0.15*N)</p>
                  <p>Fatigue: -20% per consecutive use</p>
                  <p>EMA alpha: 0.65 (same-key effect overwrites)</p>
                </div>
              </div>

              {/* Issue Dimensions */}
              <div className="col-span-2">
                <h3 className="text-sm font-semibold mb-2 text-accent">28 Issue Dimensions</h3>
                <div className="grid grid-cols-4 gap-1">
                  {[
                    '0: sharia_jurisdiction', '1: fiscal_autonomy', '2: chinese_relations', '3: bic_reform',
                    '4: ethnic_quotas', '5: fertility_policy', '6: constitutional_structure', '7: resource_revenue',
                    '8: housing', '9: education', '10: labor_automation', '11: military_role',
                    '12: immigration', '13: language_policy', '14: womens_rights', '15: traditional_authority',
                    '16: infrastructure', '17: land_tenure', '18: taxation', '19: agricultural_policy',
                    '20: biological_enhancement', '21: trade_policy', '22: environmental_regulation', '23: media_freedom',
                    '24: healthcare', '25: pada_status', '26: energy_policy', '27: az_restructuring',
                  ].map(dim => (
                    <span key={dim} className="text-text-secondary font-mono">{dim}</span>
                  ))}
                </div>
              </div>

              {/* Admin Zones */}
              <div>
                <h3 className="text-sm font-semibold mb-2 text-accent">Admin Zones</h3>
                <div className="space-y-0.5 text-text-secondary">
                  <p>1: Lagos (Southwest urban)</p>
                  <p>2: Niger (Southwest rural)</p>
                  <p>3: Confluence (South-Central)</p>
                  <p>4: Littoral (South-South)</p>
                  <p>5: Eastern (Southeast)</p>
                  <p>6: Central (North-Central)</p>
                  <p>7: Chad (Northeast)</p>
                  <p>8: Savanna (Northwest)</p>
                </div>
              </div>

              {/* Campaign Phases */}
              <div>
                <h3 className="text-sm font-semibold mb-2 text-accent">Campaign Phases</h3>
                <div className="space-y-0.5 text-text-secondary">
                  <p>Turns 1-3: Foundation</p>
                  <p>Turns 4-6: Expansion</p>
                  <p>Turns 7-9: Intensification</p>
                  <p>Turns 10-12: Final Push</p>
                </div>

                <h3 className="text-sm font-semibold mb-2 mt-4 text-accent">Presidential Spread</h3>
                <div className="text-text-secondary">
                  <p>Need 25%+ in 24+ of 38 states</p>
                  <p>Plus national plurality</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
