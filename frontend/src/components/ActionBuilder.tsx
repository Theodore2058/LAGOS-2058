import { useState, useMemo } from 'react';
import type { ActionInput, ActionType, Party } from '../types';
import type { LGAInfo, VotingDistrict } from '../api/config';
import TargetSelector from './TargetSelector';

interface Props {
  parties: Party[];
  actionTypes: ActionType[];
  issueNames: string[];
  lgas: LGAInfo[];
  districts: VotingDistrict[];
  partyPC?: Record<string, number>;
  pcUsedByParty?: Record<string, number>;
  onAdd: (action: ActionInput) => void;
  onClose: () => void;
}

// Categorize actions for grouped display
const ACTION_CATEGORIES: { label: string; actions: string[] }[] = [
  { label: 'Outreach', actions: ['rally', 'advertising', 'ground_game', 'media'] },
  { label: 'Political', actions: ['endorsement', 'patronage', 'ethnic_mobilization', 'eto_engagement'] },
  { label: 'Strategic', actions: ['opposition_research', 'crisis_response', 'manifesto'] },
  { label: 'Resources', actions: ['fundraising', 'poll', 'eto_intelligence'] },
];

// Which effect channels each action primarily affects
const ACTION_CHANNELS: Record<string, { ch: string; color: string }[]> = {
  rally:                [{ ch: 'salience', color: 'bg-purple-400' }, { ch: 'awareness', color: 'bg-blue-400' }, { ch: 'tau', color: 'bg-emerald-400' }, { ch: 'cohesion', color: 'bg-cyan-400' }],
  advertising:          [{ ch: 'salience', color: 'bg-purple-400' }, { ch: 'awareness', color: 'bg-blue-400' }],
  ground_game:          [{ ch: 'ceiling', color: 'bg-rose-400' }, { ch: 'tau', color: 'bg-emerald-400' }, { ch: 'valence', color: 'bg-amber-400' }],
  media:                [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'salience', color: 'bg-purple-400' }, { ch: 'exposure', color: 'bg-red-400' }],
  endorsement:          [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'salience', color: 'bg-purple-400' }],
  patronage:            [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'tau', color: 'bg-emerald-400' }, { ch: 'exposure', color: 'bg-red-400' }],
  ethnic_mobilization:  [{ ch: 'salience', color: 'bg-purple-400' }, { ch: 'tau', color: 'bg-emerald-400' }, { ch: 'exposure', color: 'bg-red-400' }],
  eto_engagement:       [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'salience', color: 'bg-purple-400' }, { ch: 'awareness', color: 'bg-blue-400' }],
  opposition_research:  [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'salience', color: 'bg-purple-400' }],
  crisis_response:      [{ ch: 'valence', color: 'bg-amber-400' }, { ch: 'awareness', color: 'bg-blue-400' }, { ch: 'cohesion', color: 'bg-cyan-400' }],
  fundraising:          [],
  poll:                 [],
  manifesto:            [{ ch: 'salience', color: 'bg-purple-400' }, { ch: 'valence', color: 'bg-amber-400' }],
  eto_intelligence:     [],
};

function formatActionName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// Client-side cost computation mirroring backend logic
function computeActionCost(
  actionType: string,
  scope: string,
  baseCost: number,
  params: Record<string, unknown>,
  nTargetLGAs: number,
  nTargetAZs: number,
): number {
  let cost = baseCost;

  // Area-based surcharge (district scope has no surcharge — rally, ground_game)
  if (scope === 'lga') {
    if (nTargetLGAs === 0) {
      cost += 3; // national blanket
    } else if (nTargetLGAs > 10) {
      cost += Math.min(5, Math.ceil((nTargetLGAs - 10) / 20));
    }
  } else if (scope === 'regional') {
    if (nTargetAZs === 0) {
      cost += 3; // national blanket
    } else if (nTargetAZs > 1) {
      cost += nTargetAZs - 1;
    }
  }

  // Parameter-based surcharges
  if (actionType === 'advertising') {
    const budget = (params.budget as number) ?? 0;
    const medium = (params.medium as string) ?? 'radio';
    cost += budget;
    if (medium === 'tv') cost += 1;
  } else if (actionType === 'ground_game') {
    const intensity = (params.intensity as number) ?? 0;
    cost += intensity;
  } else if (actionType === 'patronage') {
    const tier = (params.tier as number) ?? 0;
    cost += tier;
  } else if (actionType === 'eto_engagement') {
    const scoreChange = (params.score_change as number) ?? 1.0;
    if (scoreChange > 3.0) cost += 1;
  } else if (actionType === 'poll') {
    cost = Math.max(1, Math.min(5, (params.poll_tier as number) ?? 1));
  }
  return cost;
}

const LANGUAGE_DESCRIPTIONS: Record<string, string> = {
  english: 'Broad: tech, trade, constitutional reform',
  hausa: 'Sharia, education, traditional authority, immigration',
  yoruba: 'Fiscal autonomy, resource revenue, AZ restructuring',
  igbo: 'Autonomy, restructuring, trade, taxation',
  arabic: 'Sharia jurisdiction, education, traditional authority',
  pidgin: 'Housing, taxation, labor, healthcare, infrastructure',
  mandarin: 'Chinese relations, trade, automation, biotech',
};

const MEDIUM_DESCRIPTIONS: Record<string, string> = {
  radio: 'Best reach in rural/low-media areas',
  tv: 'Strong in urban/media-heavy areas (+1 PC)',
  internet: 'Scales with internet access, good for youth',
};

const ENDORSER_TYPES = [
  { value: 'traditional_ruler', label: 'Traditional Ruler', desc: 'Local chief/emir — LGA scope (+0.12 valence)' },
  { value: 'religious_leader', label: 'Religious Leader', desc: 'Faith community — regional scope (+0.10 valence)' },
  { value: 'eto_leader', label: 'ETO Leader', desc: 'Zone authority — regional scope (+0.10 valence)' },
  { value: 'celebrity', label: 'Celebrity', desc: 'National figure — no targeting (+0.08 valence)' },
  { value: 'notable', label: 'Notable Figure', desc: 'Local figure — district scope (+0.06 valence)' },
];

const ENDORSER_SCOPE: Record<string, string> = {
  traditional_ruler: 'lga',
  religious_leader: 'regional',
  eto_leader: 'regional',
  celebrity: 'none',
  notable: 'district',
};

const FUNDRAISING_SOURCES = [
  { value: 'diaspora', label: 'Diaspora', desc: 'Base yield 4 PC, no side effects' },
  { value: 'business_elite', label: 'Business Elite', desc: 'Base yield 5 PC, +1.5 exposure risk' },
  { value: 'grassroots', label: 'Grassroots', desc: 'Base yield 4 PC, turnout + awareness boost' },
  { value: 'membership', label: 'Membership', desc: 'Base yield 2-5 PC (cohesion), +cohesion recovery' },
];

// Actions exempt from GM scoring
const GM_SCORING_EXEMPT = ['poll', 'eto_intelligence'];

function computeGMScore(params: Record<string, unknown>): number {
  const sf = Math.max(1, Math.min(5, (params.strategic_fit as number) ?? 3));
  let q = Math.max(1, Math.min(5, (params.quality as number) ?? 3));
  const creativity = (params.has_content ? 1 : 0) + (params.has_visual_audio ? 1 : 0) + (params.has_strategic_docs ? 1 : 0);
  q = Math.min(5, q + creativity);
  return sf + q;
}

const SCORE_LABELS: Record<number, { label: string; color: string }> = {
  2: { label: 'Catastrophic', color: 'text-red-400' },
  3: { label: 'Poor', color: 'text-red-400' },
  4: { label: 'Below Avg', color: 'text-orange-400' },
  5: { label: 'Mediocre', color: 'text-orange-400' },
  6: { label: 'Average', color: 'text-text-secondary' },
  7: { label: 'Good', color: 'text-blue-400' },
  8: { label: 'Strong', color: 'text-blue-400' },
  9: { label: 'Excellent', color: 'text-emerald-400' },
  10: { label: 'Masterful', color: 'text-emerald-400' },
};

const selectClass = 'bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors';
const inputClass = 'w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors';

export default function ActionBuilder({ parties, actionTypes, issueNames, lgas, districts, partyPC, pcUsedByParty, onAdd, onClose }: Props) {
  const [party, setParty] = useState(parties[0]?.name ?? '');
  const [actionType, setActionType] = useState('');
  const [targetLGAs, setTargetLGAs] = useState<number[]>([]);
  const [targetAzs, setTargetAzs] = useState<number[]>([]);
  const [targetDistricts, setTargetDistricts] = useState<string[]>([]);
  const [targetParty, setTargetParty] = useState('');
  const [language, setLanguage] = useState('english');
  const [params, setParams] = useState<Record<string, unknown>>({});

  const selectedAction = actionTypes.find(a => a.name === actionType);
  const baseScope = selectedAction?.scope ?? 'none';
  // Endorsement scope varies by endorser type
  const scope = actionType === 'endorsement'
    ? (ENDORSER_SCOPE[(params.endorser_type as string) ?? 'notable'] ?? 'district')
    : baseScope;

  // For district scope, count total LGAs across selected districts
  const districtLGACount = useMemo(() => {
    if (scope !== 'district') return 0;
    return targetDistricts.reduce((sum, id) => {
      const d = districts.find(d => d.district_id === id);
      return sum + (d?.n_lgas ?? 0);
    }, 0);
  }, [scope, targetDistricts, districts]);

  // Dynamic cost computation
  const effectiveLGACount = scope === 'district' ? districtLGACount : targetLGAs.length;
  const cost = useMemo(() => {
    if (!selectedAction) return 0;
    return computeActionCost(
      actionType, scope, selectedAction.base_cost, params,
      effectiveLGACount, targetAzs.length,
    );
  }, [actionType, scope, selectedAction, params, effectiveLGACount, targetAzs.length]);

  const areaSurcharge = useMemo(() => {
    if (!selectedAction) return 0;
    return cost - computeActionCost(actionType, scope, selectedAction.base_cost, params, scope === 'lga' || scope === 'district' ? 1 : 1, scope === 'regional' ? 1 : 0);
  }, [actionType, scope, selectedAction, params, cost]);

  const handleTargetChange = (lgaIds: number[], azIds: number[]) => {
    setTargetLGAs(lgaIds);
    setTargetAzs(azIds);
  };

  const handleSubmit = () => {
    if (!party || !actionType) return;
    // Build parameters, including GM scoring fields for scored actions
    const finalParams = { ...params };
    if (['rally', 'advertising', 'ground_game', 'media'].includes(actionType)) {
      finalParams.language = language;
    }
    // Include GM scoring params for all scored actions
    if (!GM_SCORING_EXEMPT.includes(actionType)) {
      finalParams.strategic_fit = (params.strategic_fit as number) ?? 3;
      finalParams.quality = (params.quality as number) ?? 3;
      if (params.has_content) finalParams.has_content = true;
      if (params.has_visual_audio) finalParams.has_visual_audio = true;
      if (params.has_strategic_docs) finalParams.has_strategic_docs = true;
    }
    onAdd({
      party,
      action_type: actionType,
      target_lgas: targetLGAs.length > 0 ? targetLGAs : null,
      target_azs: targetAzs.length > 0 ? targetAzs : null,
      target_districts: targetDistricts.length > 0 ? targetDistricts : null,
      target_party: targetParty || null,
      parameters: finalParams,
    });
    setActionType('');
    setTargetLGAs([]);
    setTargetAzs([]);
    setTargetDistricts([]);
    setTargetParty('');
    setLanguage('english');
    setParams({});
  };

  return (
    <div className="bg-bg-secondary rounded-lg p-4 border border-bg-tertiary/50 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Add Action</h3>
        <button onClick={onClose} className="text-text-secondary hover:text-text-primary text-sm px-2 py-1 rounded hover:bg-bg-tertiary/50 transition-colors">Close</button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="text-xs text-text-secondary block mb-1">Party</label>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: parties.find(p => p.name === party)?.color ?? '#888' }} />
            <select value={party} onChange={e => setParty(e.target.value)}
              className={`w-full ${selectClass}`}>
              {parties.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
            </select>
          </div>
          {partyPC && party && (() => {
            const total = partyPC[party] ?? 0;
            const queued = pcUsedByParty?.[party] ?? 0;
            const remaining = total - queued - cost;
            const maxPC = 18;
            return (
              <div className="mt-1">
                <div className="flex items-center gap-1 h-2.5 bg-bg-tertiary rounded-full overflow-hidden">
                  {queued > 0 && <div className="h-full bg-warning/60 rounded-l-full" style={{ width: `${(queued / maxPC) * 100}%` }} title={`${queued} PC queued`} />}
                  {cost > 0 && <div className={`h-full ${remaining < 0 ? 'bg-danger/60' : 'bg-accent/60'}`} style={{ width: `${(Math.min(cost, total - queued) / maxPC) * 100}%` }} title={`${cost} PC this action`} />}
                  <div className="flex-1" />
                </div>
                <div className="flex justify-between text-[10px] mt-0.5">
                  <span className="text-text-secondary">{total} PC total</span>
                  <span className={`font-mono font-medium ${remaining < 0 ? 'text-danger' : 'text-text-secondary'}`}>
                    {remaining >= 0 ? `${remaining} left` : `${Math.abs(remaining)} over`}
                  </span>
                </div>
              </div>
            );
          })()}
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Action Type</label>
          <select value={actionType} onChange={e => { setActionType(e.target.value); setParams({}); setTargetLGAs([]); setTargetAzs([]); setTargetDistricts([]); }}
            className={`w-full ${selectClass}`}>
            <option value="">-- Select action --</option>
            {ACTION_CATEGORIES.map(cat => {
              const available = cat.actions.filter(a => actionTypes.some(at => at.name === a));
              if (available.length === 0) return null;
              return (
                <optgroup key={cat.label} label={cat.label}>
                  {available.map(a => {
                    const at = actionTypes.find(at => at.name === a)!;
                    return <option key={a} value={a}>{formatActionName(a)} ({at.base_cost}+ PC)</option>;
                  })}
                </optgroup>
              );
            })}
            {/* Any uncategorized actions */}
            {actionTypes.filter(a => !ACTION_CATEGORIES.some(c => c.actions.includes(a.name))).map(a => (
              <option key={a.name} value={a.name}>{formatActionName(a.name)} ({a.base_cost}+ PC)</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Total Cost</label>
          <div className="text-lg font-bold text-accent">
            {cost} PC
            {areaSurcharge > 0 && (
              <span className="text-xs font-normal text-text-secondary ml-1">(+{areaSurcharge} area)</span>
            )}
          </div>
        </div>
      </div>

      {selectedAction && (
        <div className="space-y-1">
          <p className="text-xs text-text-secondary">{selectedAction.description}</p>
          {ACTION_CHANNELS[actionType]?.length > 0 && (
            <div className="flex items-center gap-1">
              <span className="text-[10px] text-text-secondary/50">Channels:</span>
              {ACTION_CHANNELS[actionType].map(({ ch, color }) => (
                <span key={ch} className={`text-[10px] px-1.5 py-0.5 rounded-full ${color}/20 text-text-secondary`}>
                  {ch}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* GM Score */}
      {actionType && !GM_SCORING_EXEMPT.includes(actionType) && (() => {
        const gmScore = computeGMScore(params);
        const scoreInfo = SCORE_LABELS[gmScore] ?? { label: '', color: 'text-text-secondary' };
        return (
          <div className="bg-bg-tertiary/50 rounded-lg p-3 border border-bg-quaternary/30 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-text-secondary">GM Score</span>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-bold ${scoreInfo.color}`}>{gmScore}</span>
                <span className={`text-xs ${scoreInfo.color}`}>{scoreInfo.label}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] text-text-secondary block mb-1">Strategic Fit</label>
                <div className="flex gap-1">
                  {[1,2,3,4,5].map(n => (
                    <button key={n} onClick={() => setParams({ ...params, strategic_fit: n })}
                      className={`flex-1 text-xs py-1 rounded transition-colors ${
                        ((params.strategic_fit as number) ?? 3) === n
                          ? 'bg-accent text-bg-primary font-bold'
                          : 'bg-bg-tertiary hover:bg-bg-quaternary/50 text-text-secondary'
                      }`}>{n}</button>
                  ))}
                </div>
                <p className="text-[9px] text-text-secondary/60 mt-0.5">Region, demographic, issue, language</p>
              </div>
              <div>
                <label className="text-[10px] text-text-secondary block mb-1">Quality of Execution</label>
                <div className="flex gap-1">
                  {[1,2,3,4,5].map(n => (
                    <button key={n} onClick={() => setParams({ ...params, quality: n })}
                      className={`flex-1 text-xs py-1 rounded transition-colors ${
                        ((params.quality as number) ?? 3) === n
                          ? 'bg-accent text-bg-primary font-bold'
                          : 'bg-bg-tertiary hover:bg-bg-quaternary/50 text-text-secondary'
                      }`}>{n}</button>
                  ))}
                </div>
                <p className="text-[9px] text-text-secondary/60 mt-0.5">Detail, realism, creativity, understanding</p>
              </div>
            </div>
            <div className="flex items-center gap-4 pt-1">
              <span className="text-[10px] text-text-secondary/60">Bonuses:</span>
              {[
                { key: 'has_content', label: 'Content' },
                { key: 'has_visual_audio', label: 'Visual/Audio' },
                { key: 'has_strategic_docs', label: 'Strategy Doc' },
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-1 cursor-pointer">
                  <input type="checkbox" checked={!!params[key]}
                    onChange={e => setParams({ ...params, [key]: e.target.checked })}
                    className="rounded border-bg-quaternary/50 bg-bg-tertiary text-accent focus:ring-accent/30 w-3 h-3" />
                  <span className="text-[10px] text-text-secondary">{label}</span>
                  <span className="text-[9px] text-emerald-400/60">+1Q</span>
                </label>
              ))}
            </div>
          </div>
        );
      })()}

      {/* Target selector */}
      {actionType && (
        <TargetSelector
          lgas={lgas}
          districts={districts}
          selectedLGAs={targetLGAs}
          selectedAZs={targetAzs}
          selectedDistricts={targetDistricts}
          scope={scope}
          singleDistrict={actionType === 'rally'}
          onChange={handleTargetChange}
          onDistrictChange={setTargetDistricts}
        />
      )}

      {/* Language selector */}
      {['rally', 'advertising', 'ground_game', 'media'].includes(actionType) && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Language</label>
          <select value={language} onChange={e => setLanguage(e.target.value)}
            className={selectClass}>
            {Object.entries(LANGUAGE_DESCRIPTIONS).map(([l]) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
          <p className="text-[10px] text-text-secondary mt-0.5">{LANGUAGE_DESCRIPTIONS[language]}</p>
        </div>
      )}

      {/* Action-specific params */}
      {actionType === 'advertising' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Medium</label>
          <select value={(params.medium as string) ?? 'radio'} onChange={e => setParams({ ...params, medium: e.target.value })}
            className={selectClass}>
            {Object.entries(MEDIUM_DESCRIPTIONS).map(([m]) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <p className="text-[10px] text-text-secondary mt-0.5">{MEDIUM_DESCRIPTIONS[(params.medium as string) ?? 'radio']}</p>
          <label className="text-xs text-text-secondary block mb-1 mt-2">Ad Spend</label>
          <div className="flex gap-1.5">
            {([
              { value: 0, label: 'Standard', desc: '+0 PC' },
              { value: 1, label: 'Heavy', desc: '+1 PC' },
              { value: 2, label: 'Blitz', desc: '+2 PC' },
            ] as const).map(opt => (
              <button key={opt.value} type="button"
                className={`flex-1 px-2 py-1 rounded text-xs border transition-colors ${
                  ((params.budget as number) ?? 0) === opt.value
                    ? 'bg-accent/20 border-accent text-accent'
                    : 'border-bg-tertiary text-text-secondary hover:border-text-secondary'
                }`}
                onClick={() => setParams({ ...params, budget: opt.value })}
              >
                <div className="font-medium">{opt.label}</div>
                <div className="text-[10px] opacity-60">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {actionType === 'ground_game' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Intensity</label>
          <div className="flex gap-1.5">
            {([
              { value: 0, label: 'Standard', desc: '+0 PC' },
              { value: 1, label: 'Reinforced', desc: '+1 PC' },
              { value: 2, label: 'Surge', desc: '+2 PC' },
            ] as const).map(opt => (
              <button key={opt.value} type="button"
                className={`flex-1 px-2 py-1 rounded text-xs border transition-colors ${
                  ((params.intensity as number) ?? 0) === opt.value
                    ? 'bg-accent/20 border-accent text-accent'
                    : 'border-bg-tertiary text-text-secondary hover:border-text-secondary'
                }`}
                onClick={() => setParams({ ...params, intensity: opt.value })}
              >
                <div className="font-medium">{opt.label}</div>
                <div className="text-[10px] opacity-60">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {actionType === 'patronage' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Scale</label>
          <div className="flex gap-1">
            {[
              { value: 0, label: 'Standard', desc: '+0.3 exposure' },
              { value: 1, label: 'Heavy', desc: '+0.6 exposure' },
              { value: 2, label: 'Massive', desc: '+0.9 exposure' },
            ].map(opt => (
              <button key={opt.value} type="button"
                onClick={() => setParams({ ...params, tier: opt.value })}
                className={`flex-1 px-2 py-1.5 rounded text-xs border transition-colors ${
                  (params.tier ?? 0) === opt.value
                    ? 'bg-accent text-white border-accent'
                    : 'bg-surface border-border hover:border-accent'
                }`}>
                <div className="font-medium">{opt.label}</div>
                <div className="text-[10px] opacity-60">{opt.desc}</div>
              </button>
            ))}
          </div>
          <p className="text-xs text-danger mt-1">+{(0.3 * (1 + ((params.tier as number) ?? 0))).toFixed(1)} exposure risk</p>
        </div>
      )}

      {actionType === 'opposition_research' && (
        <div className="space-y-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Target Party</label>
            <select value={targetParty} onChange={e => setTargetParty(e.target.value)}
              className={selectClass}>
              <option value="">-- Select --</option>
              {parties.filter(p => p.name !== party).map(p => (
                <option key={p.name} value={p.name}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Target Dimensions <span className="opacity-50">(max 4; empty = auto-detect weakest)</span>
            </label>
            <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
              {issueNames.map((name, i) => {
                const current = (params.target_dimensions as number[]) ?? [];
                const selected = current.includes(i);
                const atLimit = current.length >= 4 && !selected;
                return (
                  <button key={i} type="button"
                    disabled={atLimit}
                    onClick={() => {
                      const next = selected ? current.filter(d => d !== i) : [...current, i];
                      setParams({ ...params, target_dimensions: next.length ? next : undefined });
                    }}
                    className={`px-2 py-0.5 rounded text-[10px] border transition-colors ${
                      selected
                        ? 'bg-accent text-white border-accent'
                        : atLimit
                          ? 'bg-surface border-border opacity-30 cursor-not-allowed'
                          : 'bg-surface border-border hover:border-accent'
                    }`}>
                    {name}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {actionType === 'ethnic_mobilization' && (
        <p className="text-xs text-danger">+0.5 exposure risk per use</p>
      )}

      {actionType === 'poll' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Poll Tier</label>
          <select value={(params.poll_tier as number) ?? 1}
            onChange={e => setParams({ ...params, poll_tier: parseInt(e.target.value) })}
            className={selectClass}>
            <option value={1}>Tier 1 — National aggregate (1 PC, +/-1.5)</option>
            <option value={2}>Tier 2 — Zonal breakdown (2 PC, +/-1.0)</option>
            <option value={3}>Tier 3 — State breakdown (3 PC, +/-0.7)</option>
            <option value={4}>Tier 4 — State detail (4 PC, +/-0.4)</option>
            <option value={5}>Tier 5 — LGA-level (5 PC, +/-0.25)</option>
          </select>
          <p className="text-[10px] text-text-secondary mt-0.5">Results delivered next turn</p>
        </div>
      )}

      {actionType === 'eto_engagement' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Category</label>
            <select value={(params.category as string) ?? 'economic'}
              onChange={e => setParams({ ...params, category: e.target.value })}
              className={selectClass}>
              <option value="economic">Economic (resource/land/tax)</option>
              <option value="labor">Labor (automation/education)</option>
              <option value="elite">Elite (relations/constitution)</option>
              <option value="youth">Youth (biotech/media/environment)</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Score Change (+{(params.score_change as number) ?? 2})</label>
            <input type="number" min={1} max={5} value={(params.score_change as number) ?? 2}
              onChange={e => setParams({ ...params, score_change: parseInt(e.target.value) })}
              className={inputClass} />
          </div>
        </div>
      )}

      {actionType === 'media' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Tone</label>
            <select value={(params.tone as string) ?? 'positive'}
              onChange={e => setParams({ ...params, tone: e.target.value })}
              className={selectClass}>
              <option value="positive">Positive (highlight own strengths)</option>
              <option value="negative">Negative (attack opponents)</option>
              <option value="contrast">Contrast (compare positions)</option>
            </select>
          </div>
          {((params.tone as string) === 'negative' || (params.tone as string) === 'contrast') ? (
            <div>
              <label className="text-xs text-text-secondary block mb-1">Target Party</label>
              <select value={targetParty} onChange={e => setTargetParty(e.target.value)}
                className={selectClass}>
                <option value="">-- Select --</option>
                {parties.filter(p => p.name !== party).map(p => (
                  <option key={p.name} value={p.name}>{p.name}</option>
                ))}
              </select>
            </div>
          ) : (
            <div>
              <label className="text-xs text-text-secondary block mb-1">Narrative</label>
              <input type="text" value={(params.narrative as string) ?? ''}
                onChange={e => setParams({ ...params, narrative: e.target.value })}
                className={inputClass}
                placeholder="Media narrative" />
            </div>
          )}
        </div>
      )}

      {actionType === 'endorsement' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Endorser Type</label>
            <select value={(params.endorser_type as string) ?? 'notable'}
              onChange={e => { setParams({ ...params, endorser_type: e.target.value }); setTargetLGAs([]); setTargetAzs([]); setTargetDistricts([]); }}
              className={selectClass}>
              {ENDORSER_TYPES.map(et => (
                <option key={et.value} value={et.value}>{et.label}</option>
              ))}
            </select>
            <p className="text-[10px] text-text-secondary mt-0.5">
              {ENDORSER_TYPES.find(et => et.value === ((params.endorser_type as string) ?? 'notable'))?.desc}
            </p>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Endorser Name</label>
            <input type="text" value={(params.endorser_name as string) ?? ''}
              onChange={e => setParams({ ...params, endorser_name: e.target.value })}
              className={inputClass}
              placeholder="Name of endorser" />
          </div>
        </div>
      )}

      {actionType === 'fundraising' && (() => {
        const source = (params.source as string) ?? 'diaspora';
        const baseYield = source === 'business_elite' ? 5 : source === 'grassroots' ? 4 : source === 'membership' ? 3 : 4;
        const gmScore = computeGMScore(params);
        const sm = gmScore / 6.0;
        const yieldPC = Math.max(0, Math.floor(baseYield * sm));
        const net = yieldPC - 2;
        const netColor = net > 0 ? 'text-emerald-400' : net === 0 ? 'text-amber-400' : 'text-red-400';
        return (
          <div className="space-y-2">
            <div>
              <label className="text-xs text-text-secondary block mb-1">Source</label>
              <select value={source}
                onChange={e => setParams({ ...params, source: e.target.value })}
                className={selectClass}>
                {FUNDRAISING_SOURCES.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              <p className="text-[10px] text-text-secondary mt-0.5">
                {FUNDRAISING_SOURCES.find(s => s.value === source)?.desc}
              </p>
            </div>
            <div className="bg-bg-tertiary rounded-md px-3 py-2 border border-bg-quaternary/30">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">Yield Preview</span>
                <span className="text-text-secondary">base {baseYield} × {sm.toFixed(2)} = <span className="text-text-primary font-medium">{yieldPC} PC</span></span>
              </div>
              <div className="flex items-center justify-between text-xs mt-1">
                <span className="text-text-secondary">Net (yield − 2 cost)</span>
                <span className={`font-bold ${netColor}`}>{net > 0 ? '+' : ''}{net} PC</span>
              </div>
            </div>
          </div>
        );
      })()}

      {actionType === 'crisis_response' && (
        <p className="text-[10px] text-text-secondary">Responds to active crises. Boosts valence and cohesion in affected areas.</p>
      )}

      {partyPC && party && actionType && ((partyPC[party] ?? 0) - (pcUsedByParty?.[party] ?? 0) - cost) < 0 && (
        <div className="text-xs text-danger bg-danger/10 rounded px-2 py-1.5 border border-danger/20">
          Exceeds {party}'s budget by {Math.abs((partyPC[party] ?? 0) - (pcUsedByParty?.[party] ?? 0) - cost).toFixed(0)} PC — action will be rejected by the engine
        </div>
      )}

      <button onClick={handleSubmit} disabled={!party || !actionType}
        className="w-full px-4 py-2 bg-accent rounded hover:bg-accent-hover text-bg-primary text-sm font-medium disabled:opacity-50 btn-accent">
        Add Action ({cost} PC)
      </button>
    </div>
  );
}
