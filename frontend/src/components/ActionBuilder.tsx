import { useState, useMemo } from 'react';
import type { ActionInput, ActionType, Party } from '../types';
import type { LGAInfo } from '../api/config';
import TargetSelector from './TargetSelector';

interface Props {
  parties: Party[];
  actionTypes: ActionType[];
  issueNames: string[];
  lgas: LGAInfo[];
  onAdd: (action: ActionInput) => void;
  onClose: () => void;
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

  // Area-based surcharge
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
    const budget = (params.budget as number) ?? 1.0;
    const medium = (params.medium as string) ?? 'radio';
    if (budget > 2.0) cost += 2;
    else if (budget > 1.5) cost += 1;
    if (medium === 'tv') cost += 1;
  } else if (actionType === 'ground_game') {
    const intensity = (params.intensity as number) ?? 1.0;
    if (intensity > 1.5) cost += 2;
    else if (intensity > 1.0) cost += 1;
  } else if (actionType === 'patronage') {
    const scale = (params.scale as number) ?? 1.0;
    if (scale > 2.0) cost += 2;
    else if (scale > 1.5) cost += 1;
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
  { value: 'traditional_ruler', label: 'Traditional Ruler', desc: 'Strong regional influence (+0.12 valence)' },
  { value: 'religious_leader', label: 'Religious Leader', desc: 'Faith community networks (+0.10 valence)' },
  { value: 'eto_leader', label: 'ETO Leader', desc: 'Institutional authority (+0.10 valence)' },
  { value: 'celebrity', label: 'Celebrity', desc: 'Media attention, moderate impact (+0.08 valence)' },
  { value: 'notable', label: 'Notable Figure', desc: 'General credibility (+0.06 valence)' },
];

const FUNDRAISING_SOURCES = [
  { value: 'diaspora', label: 'Diaspora', desc: '3 PC yield, no side effects' },
  { value: 'business_elite', label: 'Business Elite', desc: '4 PC yield, +1.0 exposure risk' },
  { value: 'grassroots', label: 'Grassroots', desc: '2 PC yield, small turnout boost' },
  { value: 'membership', label: 'Membership', desc: '1-3 PC yield (scales with cohesion)' },
];

const selectClass = 'bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors';
const inputClass = 'w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors';

export default function ActionBuilder({ parties, actionTypes, issueNames, lgas, onAdd, onClose }: Props) {
  const [party, setParty] = useState(parties[0]?.name ?? '');
  const [actionType, setActionType] = useState('');
  const [targetLGAs, setTargetLGAs] = useState<number[]>([]);
  const [targetAzs, setTargetAzs] = useState<number[]>([]);
  const [targetParty, setTargetParty] = useState('');
  const [language, setLanguage] = useState('english');
  const [params, setParams] = useState<Record<string, unknown>>({});

  const selectedAction = actionTypes.find(a => a.name === actionType);
  const scope = selectedAction?.scope ?? 'none';

  // Dynamic cost computation
  const cost = useMemo(() => {
    if (!selectedAction) return 0;
    return computeActionCost(
      actionType, scope, selectedAction.base_cost, params,
      targetLGAs.length, targetAzs.length,
    );
  }, [actionType, scope, selectedAction, params, targetLGAs.length, targetAzs.length]);

  const areaSurcharge = useMemo(() => {
    if (!selectedAction) return 0;
    return cost - computeActionCost(actionType, scope, selectedAction.base_cost, params, scope === 'lga' ? 1 : 1, scope === 'regional' ? 1 : 0);
  }, [actionType, scope, selectedAction, params, cost]);

  const handleTargetChange = (lgaIds: number[], azIds: number[]) => {
    setTargetLGAs(lgaIds);
    setTargetAzs(azIds);
  };

  const handleSubmit = () => {
    if (!party || !actionType) return;
    onAdd({
      party,
      action_type: actionType,
      target_lgas: targetLGAs.length > 0 ? targetLGAs : null,
      target_azs: targetAzs.length > 0 ? targetAzs : null,
      target_party: targetParty || null,
      parameters: {
        ...params,
        ...((['rally', 'advertising', 'ground_game'].includes(actionType)) ? { language } : {}),
      },
    });
    setActionType('');
    setTargetLGAs([]);
    setTargetAzs([]);
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
          <select value={party} onChange={e => setParty(e.target.value)}
            className={`w-full ${selectClass}`}>
            {parties.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Action Type</label>
          <select value={actionType} onChange={e => { setActionType(e.target.value); setParams({}); setTargetLGAs([]); setTargetAzs([]); }}
            className={`w-full ${selectClass}`}>
            <option value="">-- Select --</option>
            {actionTypes.map(a => (
              <option key={a.name} value={a.name}>{a.name} ({a.base_cost}+ PC)</option>
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
        <p className="text-xs text-text-secondary">{selectedAction.description}</p>
      )}

      {/* Target selector */}
      {actionType && (
        <TargetSelector
          lgas={lgas}
          selectedLGAs={targetLGAs}
          selectedAZs={targetAzs}
          scope={scope}
          onChange={handleTargetChange}
        />
      )}

      {/* Language selector */}
      {['rally', 'advertising', 'ground_game'].includes(actionType) && (
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
          <label className="text-xs text-text-secondary block mb-1 mt-2">Budget ({((params.budget as number) ?? 1.0).toFixed(1)}) {((params.budget as number) ?? 1.0) > 1.5 ? '— +1 PC' : ''}{((params.budget as number) ?? 1.0) > 2.0 ? ' (+2 total)' : ''}</label>
          <input type="range" min={0.5} max={3} step={0.1} value={(params.budget as number) ?? 1.0}
            onChange={e => setParams({ ...params, budget: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
        </div>
      )}

      {actionType === 'ground_game' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Intensity ({((params.intensity as number) ?? 1.0).toFixed(1)}) {((params.intensity as number) ?? 1.0) > 1.0 ? '— stronger GOTV + awareness' : ''}</label>
          <input type="range" min={0.5} max={2} step={0.1} value={(params.intensity as number) ?? 1.0}
            onChange={e => setParams({ ...params, intensity: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
        </div>
      )}

      {actionType === 'patronage' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Scale ({((params.scale as number) ?? 1.0).toFixed(1)})</label>
          <input type="range" min={0.5} max={3} step={0.1} value={(params.scale as number) ?? 1.0}
            onChange={e => setParams({ ...params, scale: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
          <p className="text-xs text-danger mt-1">+{(0.3 * ((params.scale as number) ?? 1.0)).toFixed(1)} exposure risk</p>
        </div>
      )}

      {actionType === 'opposition_research' && (
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

      {actionType === 'pledge' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Issue Dimension</label>
            <select value={(params.dimension as number) ?? 0}
              onChange={e => setParams({ ...params, dimension: parseInt(e.target.value) })}
              className={selectClass}>
              {issueNames.map((name, i) => <option key={i} value={i}>{name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Description</label>
            <input type="text" value={(params.description as string) ?? ''}
              onChange={e => setParams({ ...params, description: e.target.value })}
              className={inputClass}
              placeholder="Pledge description" />
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
          <div>
            <label className="text-xs text-text-secondary block mb-1">Narrative</label>
            <input type="text" value={(params.narrative as string) ?? ''}
              onChange={e => setParams({ ...params, narrative: e.target.value })}
              className={inputClass}
              placeholder="Media narrative" />
          </div>
        </div>
      )}

      {actionType === 'endorsement' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Endorser Type</label>
            <select value={(params.endorser_type as string) ?? 'notable'}
              onChange={e => setParams({ ...params, endorser_type: e.target.value })}
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

      {actionType === 'fundraising' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Source</label>
          <select value={(params.source as string) ?? 'diaspora'}
            onChange={e => setParams({ ...params, source: e.target.value })}
            className={selectClass}>
            {FUNDRAISING_SOURCES.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          <p className="text-[10px] text-text-secondary mt-0.5">
            {FUNDRAISING_SOURCES.find(s => s.value === ((params.source as string) ?? 'diaspora'))?.desc}
          </p>
        </div>
      )}

      {actionType === 'crisis_response' && (
        <p className="text-[10px] text-text-secondary">Responds to active crises. Boosts valence and cohesion in affected areas.</p>
      )}

      <button onClick={handleSubmit} disabled={!party || !actionType}
        className="w-full px-4 py-2 bg-accent rounded hover:bg-accent-hover text-bg-primary text-sm font-medium disabled:opacity-50 btn-accent">
        Add Action ({cost} PC)
      </button>
    </div>
  );
}
