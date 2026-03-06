import { useState, useEffect } from 'react';
import type { Party, ActionInput, ActionType } from '../types';
import { fetchParties } from '../api/parties';
import { fetchActionTypes, fetchIssueNames, fetchLGAs } from '../api/config';
import type { LGAInfo } from '../api/config';
import { newCampaign, advanceTurn } from '../api/campaign';
import type { CampaignStateResponse, TurnResult, PartyStatus } from '../api/campaign';
import ActionBuilder from '../components/ActionBuilder';

function computeQueuedActionCost(a: ActionInput, actionTypes: ActionType[]): number {
  const at = actionTypes.find(t => t.name === a.action_type);
  if (!at) return 0;
  let cost = at.base_cost;
  const scope = at.scope;
  const nLGAs = a.target_lgas?.length ?? 0;
  const nAZs = a.target_azs?.length ?? 0;

  // Area surcharge
  if (scope === 'lga') {
    if (nLGAs === 0) cost += 3;
    else if (nLGAs > 10) cost += Math.min(5, Math.ceil((nLGAs - 10) / 20));
  } else if (scope === 'regional') {
    if (nAZs === 0) cost += 3;
    else if (nAZs > 1) cost += nAZs - 1;
  }

  // Param surcharges
  const p = a.parameters;
  if (a.action_type === 'advertising') {
    const budget = (p.budget as number) ?? 1.0;
    if (budget > 2.0) cost += 2;
    else if (budget > 1.5) cost += 1;
    if ((p.medium as string) === 'tv') cost += 1;
  } else if (a.action_type === 'ground_game') {
    const intensity = (p.intensity as number) ?? 1.0;
    if (intensity > 1.5) cost += 2;
    else if (intensity > 1.0) cost += 1;
  } else if (a.action_type === 'patronage') {
    const scale = (p.scale as number) ?? 1.0;
    if (scale > 2.0) cost += 2;
    else if (scale > 1.5) cost += 1;
  } else if (a.action_type === 'eto_engagement') {
    if (((p.score_change as number) ?? 1.0) > 3.0) cost += 1;
  } else if (a.action_type === 'poll') {
    cost = Math.max(1, Math.min(5, (p.poll_tier as number) ?? 1));
  }
  return cost;
}

export default function Campaign() {
  const [parties, setParties] = useState<Party[]>([]);
  const [actionTypes, setActionTypes] = useState<ActionType[]>([]);
  const [issueNames, setIssueNames] = useState<string[]>([]);
  const [lgas, setLgas] = useState<LGAInfo[]>([]);
  const [campaignState, setCampaignState] = useState<CampaignStateResponse | null>(null);
  const [history, setHistory] = useState<TurnResult[]>([]);
  const [actions, setActions] = useState<ActionInput[]>([]);
  const [showBuilder, setShowBuilder] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
    fetchActionTypes().then(setActionTypes).catch(e => console.error('Failed to fetch action types:', e));
    fetchIssueNames().then(setIssueNames).catch(e => console.error('Failed to fetch issue names:', e));
    fetchLGAs().then(setLgas).catch(e => console.error('Failed to fetch LGAs:', e));
  }, []);

  const handleNewCampaign = async () => {
    if (parties.length < 2) {
      setError('Need at least 2 parties');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const state = await newCampaign(parties, {
        q: 0.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, scale: 1.5,
        tau_0: 3.0, tau_1: 0.3, tau_2: 0.5, beta_econ: 0.3,
        kappa: 200, sigma_national: 0.10, sigma_regional: 0.15,
        sigma_turnout: 0.0, sigma_turnout_regional: 0.0,
      }, 5, null, 12);
      setCampaignState(state);
      setHistory([]);
      setActions([]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed');
    }
    setLoading(false);
  };

  const handleAdvance = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await advanceTurn(actions, []);
      setCampaignState(result.state);
      setHistory(prev => [...prev, result]);
      setActions([]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Turn failed');
    }
    setLoading(false);
  };

  const removeAction = (idx: number) => {
    setActions(prev => prev.filter((_, i) => i !== idx));
  };

  const totalPCByParty = actions.reduce<Record<string, number>>((acc, a) => {
    acc[a.party] = (acc[a.party] ?? 0) + computeQueuedActionCost(a, actionTypes);
    return acc;
  }, {});

  if (!campaignState) {
    return (
      <div className="p-8 max-w-2xl">
        <h2 className="text-2xl font-bold mb-2">Campaign Mode</h2>
        <p className="text-text-secondary mb-6">{parties.length} parties loaded. Start a new 12-turn campaign simulation.</p>
        {error && <div className="mb-4 p-3 bg-danger/20 text-danger rounded-md text-sm border border-danger/30">{error}</div>}
        <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/50">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}><path d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold">12-Turn Campaign Simulation</h3>
              <p className="text-xs text-text-secondary">Actions, crises, PC economy, synergies, and scandals</p>
            </div>
          </div>
          <button onClick={handleNewCampaign} disabled={loading}
            className="w-full px-6 py-2.5 bg-accent rounded-md hover:bg-accent-hover text-bg-primary font-medium disabled:opacity-50 btn-accent">
            {loading ? 'Initializing...' : 'Start New Campaign'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      {/* Turn Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
            Turn {campaignState.turn} <span className="text-text-secondary font-normal">of {campaignState.n_turns}</span>
          </h2>
          <span className="text-xs text-accent uppercase tracking-[0.1em] font-medium">{campaignState.phase}</span>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowBuilder(!showBuilder)}
            className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
            {showBuilder ? 'Hide' : 'Add Actions'}
          </button>
          <button onClick={handleAdvance} disabled={loading}
            className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium disabled:opacity-50 btn-accent">
            {loading ? 'Processing...' : `Submit Turn ${campaignState.turn}`}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-danger/20 text-danger rounded text-sm flex items-center justify-between border border-danger/30">
          {error}
          <button onClick={() => setError(null)} className="text-danger/60 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors shrink-0 ml-2" aria-label="Dismiss error">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
          </button>
        </div>
      )}

      {/* Party Status Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {campaignState.party_statuses.map(ps => (
          <PartyCard key={ps.name} status={ps} color={parties.find(p => p.name === ps.name)?.color ?? '#888'}
            pcUsed={totalPCByParty[ps.name] ?? 0} />
        ))}
      </div>

      {/* Action Builder */}
      {showBuilder && (
        <ActionBuilder
          parties={parties}
          actionTypes={actionTypes}
          issueNames={issueNames}
          lgas={lgas}
          onAdd={(a) => setActions(prev => [...prev, a])}
          onClose={() => setShowBuilder(false)}
        />
      )}

      {/* Action Queue */}
      {actions.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold">Queued Actions ({actions.length})</h3>
            <button onClick={() => setActions([])} className="text-xs text-danger/60 hover:text-danger transition-colors">Clear All</button>
          </div>
          {/* Group by party */}
          {Object.entries(
            actions.reduce<Record<string, { actions: { action: ActionInput; idx: number }[]; totalCost: number }>>((acc, a, i) => {
              const actionCost = computeQueuedActionCost(a, actionTypes);
              if (!acc[a.party]) acc[a.party] = { actions: [], totalCost: 0 };
              acc[a.party].actions.push({ action: a, idx: i });
              acc[a.party].totalCost += actionCost;
              return acc;
            }, {})
          ).map(([partyName, group]) => {
            const partyColor = parties.find(p => p.name === partyName)?.color ?? '#888';
            const partyStatus = campaignState.party_statuses.find(ps => ps.name === partyName);
            const overBudget = partyStatus && group.totalCost > partyStatus.pc;
            return (
              <div key={partyName} className="mb-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: partyColor }} />
                  <span className="text-xs font-semibold" style={{ color: partyColor }}>{partyName}</span>
                  <span className={`text-xs font-mono ml-auto ${overBudget ? 'text-danger font-bold' : 'text-text-secondary'}`}>
                    {group.totalCost} PC{overBudget ? ` (exceeds ${partyStatus!.pc.toFixed(0)} available!)` : ''}
                  </span>
                </div>
                {group.actions.map(({ action: a, idx }) => (
                  <div key={idx} className="flex items-center gap-3 text-xs py-1 pl-4 border-b border-bg-tertiary/20 hover:bg-bg-tertiary/20 transition-colors rounded">
                    <span className="flex-1">{a.action_type}</span>
                    {a.target_lgas && a.target_lgas.length > 0 && (
                      <span className="text-text-secondary text-[10px]">{a.target_lgas.length} LGA{a.target_lgas.length > 1 ? 's' : ''}</span>
                    )}
                    {a.target_azs && a.target_azs.length > 0 && (
                      <span className="text-text-secondary text-[10px]">AZ: {a.target_azs.join(',')}</span>
                    )}
                    <span className="text-text-secondary font-mono w-10 text-right">
                      {computeQueuedActionCost(a, actionTypes)} PC
                    </span>
                    <button onClick={() => removeAction(idx)} className="text-danger/60 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors" aria-label={`Remove ${a.action_type} action`}>
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                    </button>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}

      {/* Turn History */}
      {history.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-2">Turn History</h3>
          <div className="space-y-0">
            {history.map((h, i) => {
              const sorted = Object.entries(h.national_vote_shares).sort((a, b) => b[1] - a[1]);
              return (
                <div key={i} className={`border-b border-bg-tertiary/30 py-2 px-2 -mx-2 rounded hover:bg-bg-tertiary/20 transition-colors ${i % 2 === 1 ? 'bg-bg-tertiary/10' : ''}`}>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono w-16 text-accent font-semibold">Turn {h.turn}</span>
                    <span className="text-xs text-text-secondary">Turnout: {(h.national_turnout * 100).toFixed(1)}%</span>
                    <span className="text-xs flex-1">
                      {sorted.slice(0, 3).map(([name, share]) => (
                        <span key={name} className="mr-3" style={{ color: parties.find(p => p.name === name)?.color }}>
                          {name}: {(share * 100).toFixed(1)}%
                        </span>
                      ))}
                    </span>
                  </div>
                  {h.scandals.length > 0 && (
                    <div className="text-xs text-danger mt-1">
                      {h.scandals.map((s, j) => (
                        <span key={j}>SCANDAL: {String((s as Record<string, unknown>).party)} (valence -{String((s as Record<string, unknown>).valence_penalty)}) </span>
                      ))}
                    </div>
                  )}
                  {h.synergies.length > 0 && (
                    <div className="text-xs text-success mt-1">
                      {h.synergies.map((s, j) => (
                        <span key={j}>SYNERGY: {String((s as Record<string, unknown>).party)} {String((s as Record<string, unknown>).channel)} +{Number((s as Record<string, unknown>).magnitude).toFixed(2)} </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="animate-spin w-6 h-6 border-2 border-accent border-t-transparent rounded-full mx-auto mb-2" />
            <p className="text-sm text-text-secondary">Processing turn...</p>
          </div>
        </div>
      )}
    </div>
  );
}

function PartyCard({ status, color, pcUsed }: { status: PartyStatus; color: string; pcUsed: number }) {
  const pcColor = status.pc >= 10 ? '#22c55e' : status.pc >= 5 ? '#f59e0b' : '#ef4444';
  const exposureDanger = status.exposure > 1.5;
  const momentumArrow = status.momentum_direction === 'up' ? '\u2191' : status.momentum_direction === 'down' ? '\u2193' : '\u2194';
  const cohesionPct = (status.cohesion / 10) * 100;

  return (
    <div className="bg-bg-secondary rounded-lg p-3.5 border border-bg-tertiary/50 hover:border-bg-quaternary/50 transition-colors"
      style={{ borderTopColor: color, borderTopWidth: 2 }}>
      <div className="flex items-center gap-2 mb-3">
        <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
        <span className="font-semibold text-sm">{status.name}</span>
        <span className="ml-auto text-xs font-mono" title="Momentum">
          {momentumArrow} {status.momentum > 0 ? `+${status.momentum}` : status.momentum}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
        <div>
          <span className="text-text-secondary block mb-0.5">PC</span>
          <span className="font-semibold" style={{ color: pcColor }}>{status.pc.toFixed(0)}</span>
          {pcUsed > 0 && <span className="text-warning"> (-{pcUsed})</span>}
        </div>
        <div>
          <span className="text-text-secondary block mb-0.5">Vote</span>
          <span className="font-semibold">{(status.vote_share * 100).toFixed(1)}%</span>
        </div>
        <div>
          <span className="text-text-secondary block mb-0.5">Cohesion</span>
          <div className="flex items-center gap-1.5">
            <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
              <div className="h-1.5 rounded-full transition-all"
                style={{ width: `${cohesionPct}%`, backgroundColor: status.cohesion >= 7 ? '#22c55e' : status.cohesion >= 4 ? '#f59e0b' : '#ef4444' }} />
            </div>
            <span className="text-[10px] font-mono w-6 text-right">{status.cohesion.toFixed(0)}</span>
          </div>
        </div>
        <div>
          <span className="text-text-secondary block mb-0.5">Seats</span>
          <span className="font-semibold">{status.seats.toFixed(0)}</span>
        </div>
        <div className="col-span-2">
          <span className="text-text-secondary block mb-0.5">Exposure</span>
          <div className="flex items-center gap-1.5">
            <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
              <div className="h-1.5 rounded-full transition-all"
                style={{ width: `${Math.min(status.exposure / 2.5 * 100, 100)}%`, backgroundColor: exposureDanger ? '#ef4444' : '#94a3b8' }} />
            </div>
            <span className={`text-[10px] font-mono w-8 text-right ${exposureDanger ? 'text-danger font-bold' : ''}`}>
              {status.exposure.toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
