import { useState, useEffect } from 'react';
import type { Party, ActionInput, ActionType } from '../types';
import { fetchParties } from '../api/parties';
import { fetchActionTypes, fetchIssueNames } from '../api/config';
import { newCampaign, advanceTurn } from '../api/campaign';
import type { CampaignStateResponse, TurnResult, PartyStatus } from '../api/campaign';
import ActionBuilder from '../components/ActionBuilder';

export default function Campaign() {
  const [parties, setParties] = useState<Party[]>([]);
  const [actionTypes, setActionTypes] = useState<ActionType[]>([]);
  const [issueNames, setIssueNames] = useState<string[]>([]);
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
    const cost = actionTypes.find(at => at.name === a.action_type)?.base_cost ?? 0;
    acc[a.party] = (acc[a.party] ?? 0) + cost;
    return acc;
  }, {});

  if (!campaignState) {
    return (
      <div className="p-8">
        <h2 className="text-2xl font-bold mb-4">Campaign Mode</h2>
        <p className="text-text-secondary mb-4">{parties.length} parties loaded. Start a new 12-turn campaign simulation.</p>
        {error && <div className="mb-4 p-3 bg-danger/20 text-danger rounded text-sm">{error}</div>}
        <button onClick={handleNewCampaign} disabled={loading}
          className="px-6 py-2 bg-accent rounded hover:bg-accent-hover text-white disabled:opacity-50">
          {loading ? 'Initializing...' : 'Start New Campaign'}
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      {/* Turn Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            Turn {campaignState.turn} of {campaignState.n_turns}
          </h2>
          <span className="text-sm text-text-secondary">{campaignState.phase}</span>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowBuilder(!showBuilder)}
            className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
            {showBuilder ? 'Hide' : 'Add Actions'}
          </button>
          <button onClick={handleAdvance} disabled={loading}
            className="px-4 py-1.5 text-sm bg-accent rounded hover:bg-accent-hover text-white disabled:opacity-50">
            {loading ? 'Processing...' : `Submit Turn ${campaignState.turn}`}
          </button>
        </div>
      </div>

      {error && <div className="p-3 bg-danger/20 text-danger rounded text-sm">{error}</div>}

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
          onAdd={(a) => setActions(prev => [...prev, a])}
          onClose={() => setShowBuilder(false)}
        />
      )}

      {/* Action Queue */}
      {actions.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <h3 className="text-sm font-semibold mb-2">Queued Actions ({actions.length})</h3>
          <div className="space-y-1">
            {actions.map((a, i) => (
              <div key={i} className="flex items-center gap-3 text-xs py-1 border-b border-bg-tertiary/30">
                <span className="font-mono w-12" style={{ color: parties.find(p => p.name === a.party)?.color }}>{a.party}</span>
                <span className="flex-1">{a.action_type}</span>
                <span className="text-text-secondary">
                  {actionTypes.find(at => at.name === a.action_type)?.base_cost ?? '?'} PC
                </span>
                <button onClick={() => removeAction(i)} className="text-danger/60 hover:text-danger px-1">x</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Turn History */}
      {history.length > 0 && (
        <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary">
          <h3 className="text-sm font-semibold mb-2">Turn History</h3>
          <div className="space-y-2">
            {history.map((h, i) => {
              const sorted = Object.entries(h.national_vote_shares).sort((a, b) => b[1] - a[1]);
              return (
                <div key={i} className="border-b border-bg-tertiary/30 pb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono w-16">Turn {h.turn}</span>
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
