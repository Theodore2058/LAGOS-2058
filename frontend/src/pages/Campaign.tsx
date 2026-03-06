import { useState, useEffect, useCallback } from 'react';
import type { Party, ActionInput, ActionType, CrisisInput } from '../types';
import { fetchParties } from '../api/parties';
import { fetchActionTypes, fetchIssueNames, fetchLGAs } from '../api/config';
import type { LGAInfo } from '../api/config';
import { newCampaign, advanceTurn, getCampaignState, getCampaignHistory } from '../api/campaign';
import type { CampaignStateResponse, TurnResult, PartyStatus } from '../api/campaign';
import { fetchTemplates } from '../api/crises';
import type { CrisisTemplate } from '../api/crises';
import { LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { saveScenario } from '../api/scenarios';
import ActionBuilder from '../components/ActionBuilder';
import { useToast } from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';
import { useKeyboard } from '../hooks/useKeyboard';

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

/** Build display tags for an action's key parameters */
function formatActionParams(a: ActionInput): string[] {
  const tags: string[] = [];
  const p = a.parameters;
  if (a.action_type === 'advertising') {
    if (p.medium) tags.push(String(p.medium));
    if (p.budget != null) tags.push(`budget ${Number(p.budget).toFixed(1)}`);
  } else if (a.action_type === 'ground_game') {
    if (p.intensity != null) tags.push(`intensity ${Number(p.intensity).toFixed(1)}`);
  } else if (a.action_type === 'patronage') {
    if (p.scale != null) tags.push(`scale ${Number(p.scale).toFixed(1)}`);
  } else if (a.action_type === 'poll') {
    if (p.poll_tier != null) tags.push(`tier ${p.poll_tier}`);
  } else if (a.action_type === 'endorsement') {
    if (p.endorser_type) tags.push(String(p.endorser_type).replace(/_/g, ' '));
    if (p.endorser_name) tags.push(String(p.endorser_name));
  } else if (a.action_type === 'eto_engagement') {
    if (p.category) tags.push(String(p.category));
    if (p.score_change != null) tags.push(`+${p.score_change}`);
  } else if (a.action_type === 'fundraising') {
    if (p.source) tags.push(String(p.source));
  } else if (a.action_type === 'opposition_research' && a.target_party) {
    tags.push(`vs ${a.target_party}`);
  } else if (a.action_type === 'pledge') {
    if (p.dimension != null) tags.push(`dim ${p.dimension}`);
  } else if (a.action_type === 'media') {
    if (p.tone) tags.push(String(p.tone));
  }
  if (['rally', 'advertising', 'ground_game'].includes(a.action_type) && p.language && p.language !== 'english') {
    tags.push(String(p.language));
  }
  return tags;
}

export default function Campaign() {
  const [parties, setParties] = useState<Party[]>([]);
  const [actionTypes, setActionTypes] = useState<ActionType[]>([]);
  const [issueNames, setIssueNames] = useState<string[]>([]);
  const [lgas, setLgas] = useState<LGAInfo[]>([]);
  const [campaignState, setCampaignState] = useState<CampaignStateResponse | null>(null);
  const [history, setHistory] = useState<TurnResult[]>([]);
  const [actions, setActions] = useState<ActionInput[]>([]);
  const [crises, setCrises] = useState<CrisisInput[]>([]);
  const [crisisTemplates, setCrisisTemplates] = useState<CrisisTemplate[]>([]);
  const [showBuilder, setShowBuilder] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmNewCampaign, setConfirmNewCampaign] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchParties().then(setParties).catch(e => console.error('Failed to fetch parties:', e));
    fetchActionTypes().then(setActionTypes).catch(e => console.error('Failed to fetch action types:', e));
    fetchIssueNames().then(setIssueNames).catch(e => console.error('Failed to fetch issue names:', e));
    fetchLGAs().then(setLgas).catch(e => console.error('Failed to fetch LGAs:', e));
    fetchTemplates().then(setCrisisTemplates).catch(e => console.error('Failed to fetch crisis templates:', e));
    // Try to resume an active campaign from the backend
    getCampaignState().then(state => {
      if (state && state.turn >= 1) {
        setCampaignState(state);
        getCampaignHistory().then(setHistory).catch(() => {});
      }
    }).catch(() => {}); // No active campaign — ignore
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
      const result = await advanceTurn(actions, crises);
      setCampaignState(result.state);
      setHistory(prev => [...prev, result]);
      setActions([]);
      setCrises([]);
      setShowBuilder(false);
      toast(`Turn ${result.turn} complete`, 'success');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Turn failed');
    }
    setLoading(false);
  };

  const handleSave = async () => {
    const name = `Campaign T${campaignState?.turn ?? 0} - ${new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`;
    try {
      await saveScenario(name);
      toast(`Saved as "${name}"`, 'success');
    } catch {
      toast('Failed to save campaign', 'error');
    }
  };

  const removeAction = (idx: number) => {
    setActions(prev => prev.filter((_, i) => i !== idx));
  };

  // Keyboard shortcuts: Ctrl+S save, Ctrl+Enter submit turn
  const handleSaveRef = useCallback(() => {
    if (campaignState && campaignState.turn <= campaignState.n_turns) handleSave();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignState]);
  const handleAdvanceRef = useCallback(() => {
    if (campaignState && !loading && campaignState.turn <= campaignState.n_turns) handleAdvance();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignState, loading, actions, crises]);
  useKeyboard({ 'ctrl+s': handleSaveRef, 'ctrl+enter': handleAdvanceRef }, [handleSaveRef, handleAdvanceRef]);

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

  const isComplete = campaignState.turn > campaignState.n_turns;
  const pollResults = campaignState.poll_results as { commissioned_by: string; poll_tier: number; scope: string; margin_of_error: number; turn_delivered: number; dimensions_polled?: string[] }[];

  const turnProgress = Math.min(((campaignState.turn - 1) / campaignState.n_turns) * 100, 100);
  const sortedStatuses = [...campaignState.party_statuses].sort((a, b) => b.seats - a.seats || b.vote_share - a.vote_share);

  // Build trend data for chart
  const trendData = history.map(h => {
    const row: Record<string, number | string> = { turn: `T${h.turn}` };
    for (const [name, share] of Object.entries(h.national_vote_shares)) {
      row[name] = Math.round(share * 1000) / 10; // percentage with 1 decimal
    }
    return row;
  });
  // Top 6 parties for charting (by latest vote share)
  const topParties = history.length > 0
    ? Object.entries(history[history.length - 1].national_vote_shares)
        .sort((a, b) => b[1] - a[1]).slice(0, 6).map(([name]) => name)
    : [];

  // Seat distribution data (all parties with seats > 0)
  const seatData = sortedStatuses
    .filter(ps => ps.seats > 0)
    .map(ps => ({ name: ps.name, seats: Math.round(ps.seats), color: parties.find(p => p.name === ps.name)?.color ?? '#888' }));

  return (
    <div className="p-6 space-y-4 relative">
      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-bg-primary/60 backdrop-blur-sm z-20 flex items-center justify-center rounded-lg">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
            <p className="text-sm text-text-secondary font-medium">Processing turn...</p>
          </div>
        </div>
      )}

      {/* Turn Progress Bar */}
      {!isComplete && (
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
            <div className="h-1.5 rounded-full bg-accent transition-all duration-500" style={{ width: `${turnProgress}%` }} />
          </div>
          <span className="text-[10px] text-text-secondary font-mono shrink-0">{campaignState.turn}/{campaignState.n_turns}</span>
        </div>
      )}

      {/* Campaign Complete Banner */}
      {isComplete && (
        <div className="bg-accent/10 border border-accent/30 rounded-lg p-4">
          <h2 className="text-xl font-bold text-accent mb-2">Campaign Complete</h2>
          <p className="text-sm text-text-secondary mb-3">All {campaignState.n_turns} turns have been played. Final results below.</p>
          <div className="flex flex-wrap gap-3">
            {[...campaignState.party_statuses].sort((a, b) => b.seats - a.seats).slice(0, 5).map((ps, i) => {
              const color = parties.find(p => p.name === ps.name)?.color ?? '#888';
              return (
                <div key={ps.name} className="flex items-center gap-2 text-sm">
                  <span className="font-mono text-text-secondary w-4">{i + 1}.</span>
                  <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
                  <span className="font-semibold" style={{ color }}>{ps.name}</span>
                  <span className="text-text-secondary">{ps.seats.toFixed(0)} seats ({(ps.vote_share * 100).toFixed(1)}%)</span>
                </div>
              );
            })}
          </div>
          <div className="flex gap-2 mt-3">
            <button onClick={handleSave}
              className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium btn-accent">
              Save to Scenarios
            </button>
            <button onClick={() => setConfirmNewCampaign(true)}
              className="px-4 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
              New Campaign
            </button>
          </div>
        </div>
      )}

      {/* Turn Header */}
      {!isComplete && (
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold tracking-wide" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
              Turn {campaignState.turn} <span className="text-text-secondary font-normal">of {campaignState.n_turns}</span>
            </h2>
            <div className="flex items-center gap-2">
              <span className="text-xs text-accent uppercase tracking-[0.1em] font-medium">{campaignState.phase}</span>
              {PHASE_DESCRIPTIONS[campaignState.phase.toLowerCase()] && (
                <span className="text-[10px] text-text-secondary">{PHASE_DESCRIPTIONS[campaignState.phase.toLowerCase()]}</span>
              )}
            </div>
          </div>
          <div className="flex gap-2 items-center">
            <button onClick={handleSave} title="Save campaign to scenarios (Ctrl+S)"
              className="px-2 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80" aria-label="Save campaign">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" /><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></svg>
            </button>
            <button onClick={() => {
                const next = !showBuilder;
                setShowBuilder(next);
                if (next) setTimeout(() => document.getElementById('action-builder')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
              }}
              className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
              {showBuilder ? 'Hide' : 'Add Actions'}
            </button>
            <button onClick={handleAdvance} disabled={loading} title="Submit turn (Ctrl+Enter)"
              className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium disabled:opacity-50 btn-accent">
              {loading ? 'Processing...' : `Submit Turn ${campaignState.turn}`}
            </button>
          </div>
        </div>
      )}

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
        {sortedStatuses.map(ps => (
          <PartyCard key={ps.name} status={ps} color={parties.find(p => p.name === ps.name)?.color ?? '#888'}
            pcUsed={totalPCByParty[ps.name] ?? 0} />
        ))}
      </div>

      {/* Action Builder */}
      {showBuilder && (
        <div id="action-builder">
        <ActionBuilder
          parties={parties}
          actionTypes={actionTypes}
          issueNames={issueNames}
          lgas={lgas}
          partyPC={Object.fromEntries(campaignState.party_statuses.map(ps => [ps.name, ps.pc]))}
          pcUsedByParty={totalPCByParty}
          onAdd={(a) => setActions(prev => [...prev, a])}
          onClose={() => setShowBuilder(false)}
        />
        </div>
      )}

      {/* Crisis Injector & Scandal History */}
      {!isComplete && (
        <div className="flex gap-3">
          {/* Crisis Templates */}
          <div className="flex-1 bg-bg-secondary rounded-lg p-3 border border-bg-tertiary/50">
            <h3 className="text-sm font-semibold mb-2">Trigger Crisis</h3>
            <div className="flex flex-wrap gap-1.5">
              {crisisTemplates.map(t => {
                const active = crises.some(c => c.name === t.name);
                return (
                  <button key={t.name} onClick={() => {
                      if (active) {
                        setCrises(prev => prev.filter(c => c.name !== t.name));
                      } else {
                        setCrises(prev => [...prev, {
                          name: t.name, turn: 0, affected_azs: t.affected_azs, affected_lgas: null,
                          salience_shifts: t.salience_shifts, valence_effects: t.valence_effects,
                          awareness_boost: t.awareness_boost, tau_modifier: t.tau_modifier, description: t.description,
                        }]);
                      }
                    }}
                    className={`text-[11px] px-2 py-1 rounded border transition-colors ${
                      active ? 'bg-danger/20 border-danger/50 text-danger' : 'border-bg-tertiary/50 text-text-secondary hover:text-text-primary hover:border-bg-quaternary/50'
                    }`}
                    title={t.description}
                  >
                    {t.name}{active ? ' \u2715' : ''}
                  </button>
                );
              })}
              {crisisTemplates.length === 0 && <span className="text-xs text-text-secondary">No templates loaded</span>}
            </div>
            {crises.length > 0 && (
              <div className="mt-2 text-xs text-danger">{crises.length} {crises.length > 1 ? 'crises' : 'crisis'} queued for this turn</div>
            )}
          </div>
          {/* Scandal History */}
          {campaignState.scandal_history.length > 0 && (
            <div className="w-64 bg-bg-secondary rounded-lg p-3 border border-danger/20 shrink-0">
              <h3 className="text-sm font-semibold mb-2 text-danger">Scandals</h3>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {campaignState.scandal_history.map((s, i) => {
                  const sc = s as Record<string, unknown>;
                  const color = parties.find(p => p.name === sc.party)?.color ?? '#888';
                  return (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <span className="font-mono text-text-secondary w-6">T{String(sc.turn)}</span>
                      <span className="font-medium" style={{ color }}>{String(sc.party)}</span>
                      <span className="text-danger">-{Number(sc.valence_penalty).toFixed(1)}v</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
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
            const remaining = (partyStatus?.pc ?? 0) - group.totalCost;
            return (
              <div key={partyName} className="mb-3 last:mb-0">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: partyColor }} />
                  <span className="text-xs font-semibold" style={{ color: partyColor }}>{partyName}</span>
                  <span className="text-[10px] text-text-secondary">{group.actions.length} action{group.actions.length > 1 ? 's' : ''}</span>
                  <span className={`text-xs font-mono ml-auto ${overBudget ? 'text-danger font-bold' : 'text-text-secondary'}`}>
                    {group.totalCost} PC{overBudget ? ` (exceeds ${partyStatus!.pc.toFixed(0)}!)` : ` / ${partyStatus?.pc.toFixed(0) ?? '?'} (${remaining.toFixed(0)} left)`}
                  </span>
                </div>
                {group.actions.map(({ action: a, idx }) => {
                  const paramTags = formatActionParams(a);
                  return (
                    <div key={idx} className="flex items-center gap-2 text-xs py-1.5 pl-4 border-b border-bg-tertiary/20 hover:bg-bg-tertiary/20 transition-colors rounded group/row">
                      <span className="font-medium shrink-0">{a.action_type.replace(/_/g, ' ')}</span>
                      <div className="flex-1 flex flex-wrap gap-1 min-w-0">
                        {a.target_lgas && a.target_lgas.length > 0 && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-bg-tertiary/60 text-text-secondary">{a.target_lgas.length} LGA{a.target_lgas.length > 1 ? 's' : ''}</span>
                        )}
                        {a.target_azs && a.target_azs.length > 0 && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-bg-tertiary/60 text-text-secondary">AZ {a.target_azs.join(', ')}</span>
                        )}
                        {!a.target_lgas?.length && !a.target_azs?.length && actionTypes.find(t => t.name === a.action_type)?.scope !== 'none' && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-warning/10 text-warning">national</span>
                        )}
                        {paramTags.map((tag, ti) => (
                          <span key={ti} className="text-[10px] px-1.5 py-0.5 rounded bg-bg-tertiary/40 text-text-secondary">{tag}</span>
                        ))}
                      </div>
                      <span className="text-text-secondary font-mono w-10 text-right shrink-0">
                        {computeQueuedActionCost(a, actionTypes)} PC
                      </span>
                      <button onClick={() => setActions(prev => [...prev, { ...a }])}
                        className="text-text-secondary/40 hover:text-accent p-0.5 rounded hover:bg-accent/10 transition-colors opacity-0 group-hover/row:opacity-100"
                        aria-label={`Duplicate ${a.action_type} action`} title="Duplicate">
                        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" /></svg>
                      </button>
                      <button onClick={() => removeAction(idx)}
                        className="text-danger/40 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors opacity-0 group-hover/row:opacity-100"
                        aria-label={`Remove ${a.action_type} action`} title="Remove">
                        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                      </button>
                    </div>
                  );
                })}
              </div>
            );
          })}
          {/* Total summary */}
          {actions.length > 1 && (
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-bg-tertiary/40">
              <span className="text-xs text-text-secondary">{Object.keys(totalPCByParty).length} parties, {actions.length} total actions</span>
              <span className="text-xs font-mono font-semibold text-accent">
                {Object.values(totalPCByParty).reduce((s, v) => s + v, 0)} PC total
              </span>
            </div>
          )}
        </div>
      )}

      {/* Poll Results */}
      {pollResults.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-accent/20">
          <h3 className="text-sm font-semibold mb-2 text-accent">Poll Results ({pollResults.length})</h3>
          <div className="space-y-2">
            {pollResults.map((poll, i) => {
              const color = parties.find(p => p.name === poll.commissioned_by)?.color ?? '#888';
              return (
                <div key={i} className="flex items-center gap-3 text-xs py-1.5 px-2 border border-bg-tertiary/30 rounded bg-bg-tertiary/10">
                  <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: color }} />
                  <span className="font-medium" style={{ color }}>{poll.commissioned_by}</span>
                  <span className="text-text-secondary">Tier {poll.poll_tier}</span>
                  <span className="text-text-secondary">{poll.scope}</span>
                  <span className="text-text-secondary">MOE: {'\u00B1'}{poll.margin_of_error.toFixed(1)}</span>
                  {poll.dimensions_polled && (
                    <span className="text-text-secondary truncate flex-1">{poll.dimensions_polled.length} dims</span>
                  )}
                  <span className="text-text-secondary font-mono">T{poll.turn_delivered}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Charts Row: Vote Share Trend + Seat Distribution */}
      {history.length >= 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Vote Share Trend */}
          {trendData.length >= 2 && (
            <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
              <h3 className="text-sm font-semibold mb-3">Vote Share Trend</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trendData} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
                  <XAxis dataKey="turn" tick={{ fill: '#64748b', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  {topParties.map(name => (
                    <Line key={name} type="monotone" dataKey={name} dot={false}
                      stroke={parties.find(p => p.name === name)?.color ?? '#888'}
                      strokeWidth={2} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          {/* Seat Distribution */}
          {seatData.length > 0 && (
            <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
              <h3 className="text-sm font-semibold mb-3">Seat Distribution <span className="text-text-secondary font-normal">({seatData.reduce((s, d) => s + d.seats, 0)} total)</span></h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={seatData} layout="vertical" margin={{ top: 0, right: 8, bottom: 0, left: 40 }}>
                  <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} width={36} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
                    labelStyle={{ color: '#94a3b8' }}
                    formatter={(value: number) => [`${value} seats`, '']}
                  />
                  <Bar dataKey="seats" radius={[0, 4, 4, 0]}>
                    {seatData.map((d, i) => <Cell key={i} fill={d.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Turn History */}
      {history.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50">
          <h3 className="text-sm font-semibold mb-2">Turn History</h3>
          <div className="space-y-0">
            {history.map((h, i) => (
              <TurnHistoryRow key={i} result={h} parties={parties} defaultExpanded={i === history.length - 1} />
            ))}
          </div>
        </div>
      )}

      <ConfirmModal
        open={confirmNewCampaign}
        title="Start New Campaign"
        message="This will discard the current campaign and all turn history. This cannot be undone."
        confirmLabel="Start New"
        confirmDanger
        onConfirm={() => {
          setConfirmNewCampaign(false);
          setCampaignState(null);
          setHistory([]);
          setActions([]);
        }}
        onCancel={() => setConfirmNewCampaign(false)}
      />
    </div>
  );
}

function TurnHistoryRow({ result: h, parties, defaultExpanded }: { result: TurnResult; parties: Party[]; defaultExpanded: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const sorted = Object.entries(h.national_vote_shares).sort((a, b) => b[1] - a[1]);
  const actionsByParty = (h.actions_resolved as { party: string; action_type: string; cost: number }[]).reduce<
    Record<string, { actions: string[]; totalCost: number }>
  >((acc, a) => {
    if (!acc[a.party]) acc[a.party] = { actions: [], totalCost: 0 };
    acc[a.party].actions.push(a.action_type);
    acc[a.party].totalCost += (a.cost ?? 0);
    return acc;
  }, {});
  const totalActions = h.actions_resolved.length;
  const hasEvents = h.scandals.length > 0 || h.synergies.length > 0;

  return (
    <div className="border-b border-bg-tertiary/30">
      <button onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 py-2 px-2 -mx-0 rounded hover:bg-bg-tertiary/20 transition-colors text-left">
        <svg className={`w-3 h-3 text-text-secondary shrink-0 transition-transform ${expanded ? 'rotate-90' : ''}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M9 18l6-6-6-6" /></svg>
        <span className="text-xs font-mono w-14 text-accent font-semibold shrink-0">Turn {h.turn}</span>
        <span className="text-xs text-text-secondary shrink-0">{(h.national_turnout * 100).toFixed(1)}%</span>
        <span className="text-xs flex-1 truncate">
          {sorted.slice(0, 4).map(([name, share]) => (
            <span key={name} className="mr-2" style={{ color: parties.find(p => p.name === name)?.color }}>
              {name} {(share * 100).toFixed(1)}%
            </span>
          ))}
        </span>
        {totalActions > 0 && (
          <span className="text-[10px] text-text-secondary shrink-0">{totalActions} action{totalActions > 1 ? 's' : ''}</span>
        )}
        {hasEvents && (
          <span className="text-[10px] shrink-0">
            {h.scandals.length > 0 && <span className="text-danger mr-1">{h.scandals.length} scandal{h.scandals.length > 1 ? 's' : ''}</span>}
            {h.synergies.length > 0 && <span className="text-success">{h.synergies.length} synergy</span>}
          </span>
        )}
      </button>
      {expanded && (
        <div className="pl-8 pr-2 pb-3 space-y-2">
          {/* Actions by party */}
          {Object.keys(actionsByParty).length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1">Actions</div>
              {Object.entries(actionsByParty).map(([partyName, { actions: acts, totalCost }]) => {
                const color = parties.find(p => p.name === partyName)?.color ?? '#888';
                const grouped = acts.reduce<Record<string, number>>((a, t) => { a[t] = (a[t] ?? 0) + 1; return a; }, {});
                return (
                  <div key={partyName} className="flex items-center gap-2 text-xs py-0.5">
                    <div className="w-2 h-2 rounded-sm shrink-0" style={{ backgroundColor: color }} />
                    <span className="font-medium w-12 shrink-0" style={{ color }}>{partyName}</span>
                    <span className="flex-1 text-text-secondary">
                      {Object.entries(grouped).map(([type, count]) => (
                        <span key={type} className="mr-2">{count > 1 ? `${count}x ` : ''}{type}</span>
                      ))}
                    </span>
                    <span className="text-text-secondary font-mono shrink-0">{totalCost} PC</span>
                  </div>
                );
              })}
            </div>
          )}
          {/* Scandals */}
          {h.scandals.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1">Scandals</div>
              {h.scandals.map((s, j) => {
                const sc = s as Record<string, unknown>;
                const color = parties.find(p => p.name === sc.party)?.color ?? '#888';
                return (
                  <div key={j} className="flex items-center gap-2 text-xs py-0.5">
                    <div className="w-2 h-2 rounded-sm shrink-0 bg-danger" />
                    <span className="font-medium" style={{ color }}>{String(sc.party)}</span>
                    <span className="text-danger">valence -{Number(sc.valence_penalty).toFixed(1)}</span>
                    {sc.reason && <span className="text-text-secondary">({String(sc.reason)})</span>}
                  </div>
                );
              })}
            </div>
          )}
          {/* Synergies */}
          {h.synergies.length > 0 && (
            <div>
              <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1">Synergies</div>
              {h.synergies.map((s, j) => {
                const sy = s as Record<string, unknown>;
                const color = parties.find(p => p.name === sy.party)?.color ?? '#888';
                return (
                  <div key={j} className="flex items-center gap-2 text-xs py-0.5">
                    <div className="w-2 h-2 rounded-sm shrink-0 bg-success" />
                    <span className="font-medium" style={{ color }}>{String(sy.party)}</span>
                    <span className="text-success">{String(sy.channel)} +{Number(sy.magnitude).toFixed(2)}</span>
                  </div>
                );
              })}
            </div>
          )}
          {/* Full vote shares */}
          <div>
            <div className="text-[10px] text-text-secondary uppercase tracking-wider mb-1">All Vote Shares</div>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5">
              {sorted.map(([name, share]) => (
                <span key={name} className="text-xs font-mono" style={{ color: parties.find(p => p.name === name)?.color ?? '#888' }}>
                  {name} {(share * 100).toFixed(1)}%
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const PHASE_DESCRIPTIONS: Record<string, string> = {
  foundation: 'Early groundwork. Build awareness and establish presence.',
  expansion: 'Mid-campaign. Expand reach, secure endorsements, run advertising.',
  intensification: 'Late-campaign. Lock in support, counter rivals, manage crises.',
  'final push': 'Final stretch. Maximum intensity. Every action counts.',
};

function PartyCard({ status, color, pcUsed }: { status: PartyStatus; color: string; pcUsed: number }) {
  const pcColor = status.pc >= 10 ? '#22c55e' : status.pc >= 5 ? '#f59e0b' : '#ef4444';
  const exposureDanger = status.exposure > 1.5;
  const momentumArrow = status.momentum_direction === 'up' ? '\u2191' : status.momentum_direction === 'down' ? '\u2193' : '\u2194';
  const cohesionPct = (status.cohesion / 10) * 100;
  const awarenessPct = Math.min(status.awareness * 100, 100);

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
        <div>
          <span className="text-text-secondary block mb-0.5">Awareness</span>
          <div className="flex items-center gap-1.5">
            <div className="flex-1 bg-bg-tertiary rounded-full h-1.5">
              <div className="h-1.5 rounded-full transition-all"
                style={{ width: `${awarenessPct}%`, backgroundColor: status.awareness >= 0.8 ? '#22c55e' : status.awareness >= 0.65 ? '#f59e0b' : '#94a3b8' }} />
            </div>
            <span className="text-[10px] font-mono w-8 text-right">{(status.awareness * 100).toFixed(0)}%</span>
          </div>
        </div>
        <div>
          <span className="text-text-secondary block mb-0.5">ETO</span>
          <span className="font-semibold font-mono">{status.eto_score.toFixed(1)}</span>
          <span className="text-text-secondary">/10</span>
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
