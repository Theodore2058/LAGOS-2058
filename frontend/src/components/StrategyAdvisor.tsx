import { useState, useMemo } from 'react';
import type { Party, ActionInput, ActionType } from '../types';
import type { PartyStatus } from '../api/campaign';

interface Props {
  phase: string;
  turn: number;
  nTurns: number;
  partyStatuses: PartyStatus[];
  queuedActions: ActionInput[];
  actionTypes: ActionType[];
  parties: Party[];
}

const PHASE_RECS: Record<string, { actions: string[]; tip: string }> = {
  foundation: {
    actions: ['rally', 'ground_game', 'fundraising', 'endorsement'],
    tip: 'Build awareness early. Fundraise to stockpile PC. Rally in strongholds for cheap awareness boosts.',
  },
  expansion: {
    actions: ['advertising', 'endorsement', 'ethnic_mobilization', 'eto_engagement'],
    tip: 'Broaden reach with advertising + media combos. Secure key endorsements. Start ETO engagement.',
  },
  intensification: {
    actions: ['opposition_research', 'advertising', 'ground_game', 'manifesto'],
    tip: 'Attack weak opponents. Push salience on favorable issues. Pair rally + ground_game for synergy.',
  },
  'final push': {
    actions: ['rally', 'ground_game', 'advertising', 'crisis_response'],
    tip: 'Maximize turnout with rally + ground_game. Every PC counts. Watch exposure thresholds.',
  },
};

const SYNERGY_PAIRS: [string, string, string, string][] = [
  ['rally', 'ground_game', 'awareness', '+1.5x'],
  ['advertising', 'media', 'salience', '+1.3x'],
  ['endorsement', 'ethnic_mobilization', 'valence', '+1.2x'],
  ['eto_engagement', 'ground_game', 'ceiling', '+1.4x'],
];

export default function StrategyAdvisor({ phase, turn, nTurns, partyStatuses, queuedActions, parties }: Props) {
  const [expanded, setExpanded] = useState(true);

  const phaseKey = phase.toLowerCase();
  const recs = PHASE_RECS[phaseKey];

  // Risk alerts
  const alerts = useMemo(() => {
    const items: { party: string; color: string; type: 'danger' | 'warning'; msg: string }[] = [];
    for (const ps of partyStatuses) {
      const color = parties.find(p => p.name === ps.name)?.color ?? '#888';
      if (ps.exposure > 1.5) {
        items.push({ party: ps.name, color, type: 'danger', msg: `Exposure ${ps.exposure.toFixed(2)} — scandal imminent (>1.8 triggers)` });
      } else if (ps.exposure > 1.2) {
        items.push({ party: ps.name, color, type: 'warning', msg: `Exposure ${ps.exposure.toFixed(2)} — approaching danger zone` });
      }
      if (ps.cohesion < 3) {
        items.push({ party: ps.name, color, type: 'danger', msg: `Cohesion ${ps.cohesion.toFixed(0)}/10 — severely reduced effect magnitudes` });
      } else if (ps.cohesion < 5) {
        items.push({ party: ps.name, color, type: 'warning', msg: `Cohesion ${ps.cohesion.toFixed(0)}/10 — diminished action effectiveness` });
      }
    }
    return items;
  }, [partyStatuses, parties]);

  // Synergy opportunities based on queued actions
  const synergyHints = useMemo(() => {
    const hints: { pair: string; channel: string; mult: string; party: string; color: string }[] = [];
    const actionsByParty: Record<string, Set<string>> = {};
    for (const a of queuedActions) {
      if (!actionsByParty[a.party]) actionsByParty[a.party] = new Set();
      actionsByParty[a.party].add(a.action_type);
    }

    for (const [partyName, types] of Object.entries(actionsByParty)) {
      const color = parties.find(p => p.name === partyName)?.color ?? '#888';
      for (const [a, b, channel, mult] of SYNERGY_PAIRS) {
        if (types.has(a) && types.has(b)) {
          hints.push({ pair: `${a} + ${b}`, channel, mult, party: partyName, color });
        }
      }
    }
    return hints;
  }, [queuedActions, parties]);

  // Awareness warnings
  const awarenessAlerts = useMemo(() => {
    const items: { party: string; color: string; awareness: number; msg: string }[] = [];
    for (const ps of partyStatuses) {
      const color = parties.find(p => p.name === ps.name)?.color ?? '#888';
      if (ps.awareness < 0.65) {
        items.push({ party: ps.name, color, awareness: ps.awareness, msg: `Awareness ${(ps.awareness * 100).toFixed(0)}% — below floor, prioritize rally/advertising` });
      } else if (ps.awareness < 0.75 && turn >= 4) {
        items.push({ party: ps.name, color, awareness: ps.awareness, msg: `Awareness ${(ps.awareness * 100).toFixed(0)}% — still low for ${phaseKey} phase` });
      }
    }
    return items.sort((a, b) => a.awareness - b.awareness).slice(0, 4);
  }, [partyStatuses, parties, turn, phaseKey]);

  // Turn urgency
  const urgencyMsg = useMemo(() => {
    const turnsLeft = nTurns - turn + 1;
    if (turnsLeft <= 1) return 'FINAL TURN — all remaining PC should be spent. Maximum turnout actions.';
    if (turnsLeft <= 2) return `${turnsLeft} turns left — deploy all resources. Rally + ground_game for turnout.`;
    if (turnsLeft <= 3) return `${turnsLeft} turns left — entering final push. Prioritize high-impact actions.`;
    return null;
  }, [turn, nTurns]);

  // PC efficiency: only warn about specific cases, not every party
  const pcTips = useMemo(() => {
    const tips: { party: string; color: string; msg: string }[] = [];
    const turnsLeft = nTurns - turn + 1;
    // Sort by PC descending, only warn about top parties
    const sorted = [...partyStatuses].sort((a, b) => b.pc - a.pc);
    const highPCCount = sorted.filter(ps => ps.pc >= 16).length;

    for (const ps of sorted) {
      const color = parties.find(p => p.name === ps.name)?.color ?? '#888';
      if (turnsLeft <= 3 && ps.pc >= 10) {
        tips.push({ party: ps.name, color, msg: `${ps.pc.toFixed(0)} PC unspent with ${turnsLeft} turn${turnsLeft > 1 ? 's' : ''} left` });
        if (tips.length >= 3) break; // Limit to top 3
      } else if (ps.pc >= 16 && highPCCount <= 4) {
        // Only show individual warnings when a few parties are at risk, not all
        tips.push({ party: ps.name, color, msg: `${ps.pc.toFixed(0)} PC — near hoarding cap (18)` });
      }
    }
    // If many parties are near cap, show a summary instead
    if (highPCCount > 4 && turnsLeft > 3) {
      tips.length = 0; // clear individual tips
      tips.push({ party: '', color: '#f59e0b', msg: `${highPCCount} parties at ${'\u2265'}16 PC — widespread hoarding near cap (18)` });
    }
    return tips;
  }, [partyStatuses, parties, turn, nTurns]);

  const totalAlerts = alerts.length + awarenessAlerts.length + synergyHints.length + pcTips.length;

  return (
    <div className="bg-bg-secondary rounded-lg border border-accent/20 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-bg-tertiary/20 transition-colors text-left"
      >
        <svg className={`w-3 h-3 text-text-secondary shrink-0 transition-transform ${expanded ? 'rotate-90' : ''}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M9 18l6-6-6-6" /></svg>
        <svg className="w-4 h-4 text-accent shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <span className="text-sm font-semibold tracking-wide flex-1">Strategy Advisor</span>
        {!expanded && totalAlerts > 0 && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-accent/15 text-accent font-mono">{totalAlerts}</span>
        )}
        {!expanded && alerts.some(a => a.type === 'danger') && (
          <span className="w-2 h-2 rounded-full bg-danger animate-pulse" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {/* Phase Guidance */}
          {recs && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Phase Guidance</div>
              <p className="text-xs text-text-secondary mb-2">{recs.tip}</p>
              <div className="flex flex-wrap gap-1.5">
                {recs.actions.map(a => (
                  <span key={a} className="text-[10px] px-2 py-0.5 rounded bg-accent/10 text-accent border border-accent/20 font-mono">
                    {a}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Urgency Banner */}
          {urgencyMsg && (
            <div className="text-xs py-2 px-3 rounded bg-danger/10 border border-danger/30 text-danger font-medium flex items-center gap-2">
              <svg className="w-3.5 h-3.5 shrink-0 animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              {urgencyMsg}
            </div>
          )}

          {/* Awareness Warnings */}
          {awarenessAlerts.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Awareness Gaps</div>
              <div className="space-y-1">
                {awarenessAlerts.map((a, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1 px-2 rounded bg-blue-500/10 border border-blue-500/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0" />
                    <span className="font-medium shrink-0" style={{ color: a.color }}>{a.party}</span>
                    <span className="text-blue-300/80">{a.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Alerts */}
          {alerts.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Risk Alerts</div>
              <div className="space-y-1">
                {alerts.map((a, i) => (
                  <div key={i} className={`flex items-center gap-2 text-xs py-1 px-2 rounded ${a.type === 'danger' ? 'bg-danger/10 border border-danger/20' : 'bg-warning/10 border border-warning/20'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${a.type === 'danger' ? 'bg-danger' : 'bg-warning'}`} />
                    <span className="font-medium shrink-0" style={{ color: a.color }}>{a.party}</span>
                    <span className={a.type === 'danger' ? 'text-danger/80' : 'text-warning/80'}>{a.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Synergy Opportunities */}
          {synergyHints.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">Active Synergies</div>
              <div className="space-y-1">
                {synergyHints.map((h, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1 px-2 rounded bg-success/10 border border-success/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-success shrink-0" />
                    <span className="font-medium shrink-0" style={{ color: h.color }}>{h.party}</span>
                    <span className="text-text-secondary">{h.pair}</span>
                    <span className="text-success font-mono ml-auto">{h.mult} {h.channel}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PC Tips */}
          {pcTips.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1.5 font-medium">PC Warnings</div>
              <div className="space-y-1">
                {pcTips.map((t, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1 px-2 rounded bg-warning/10 border border-warning/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-warning shrink-0" />
                    <span className="font-medium shrink-0" style={{ color: t.color }}>{t.party}</span>
                    <span className="text-warning/80">{t.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No issues */}
          {alerts.length === 0 && awarenessAlerts.length === 0 && synergyHints.length === 0 && pcTips.length === 0 && !urgencyMsg && (
            <div className="text-xs text-text-secondary/50 text-center py-1">No risk alerts or synergies detected</div>
          )}
        </div>
      )}
    </div>
  );
}
