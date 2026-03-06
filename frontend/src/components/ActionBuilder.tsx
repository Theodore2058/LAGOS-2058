import { useState } from 'react';
import type { ActionInput, ActionType, Party } from '../types';
import { ADMIN_ZONES } from '../types';

interface Props {
  parties: Party[];
  actionTypes: ActionType[];
  issueNames: string[];
  onAdd: (action: ActionInput) => void;
  onClose: () => void;
}

const AZ_IDS = [1, 2, 3, 4, 5, 6, 7, 8];

export default function ActionBuilder({ parties, actionTypes, issueNames, onAdd, onClose }: Props) {
  const [party, setParty] = useState(parties[0]?.name ?? '');
  const [actionType, setActionType] = useState('');
  const [targetAzs, setTargetAzs] = useState<number[]>([]);
  const [targetParty, setTargetParty] = useState('');
  const [language, setLanguage] = useState('english');
  const [params, setParams] = useState<Record<string, unknown>>({});

  const selectedAction = actionTypes.find(a => a.name === actionType);
  const cost = selectedAction?.base_cost ?? 0;

  const toggleAz = (az: number) => {
    setTargetAzs(prev => prev.includes(az) ? prev.filter(a => a !== az) : [...prev, az]);
  };

  const handleSubmit = () => {
    if (!party || !actionType) return;
    onAdd({
      party,
      action_type: actionType,
      target_lgas: null,
      target_azs: targetAzs.length > 0 ? targetAzs : null,
      target_party: targetParty || null,
      parameters: {
        ...params,
        ...((['rally', 'advertising', 'ground_game'].includes(actionType)) ? { language } : {}),
      },
    });
    // Reset for next action
    setActionType('');
    setTargetAzs([]);
    setTargetParty('');
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
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            {parties.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Action Type</label>
          <select value={actionType} onChange={e => { setActionType(e.target.value); setParams({}); }}
            className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            <option value="">-- Select --</option>
            {actionTypes.map(a => (
              <option key={a.name} value={a.name}>{a.name} ({a.base_cost} PC)</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">Cost</label>
          <div className="text-lg font-bold text-accent">{cost} PC</div>
        </div>
      </div>

      {selectedAction && (
        <p className="text-xs text-text-secondary">{selectedAction.description}</p>
      )}

      {/* Target AZs */}
      {actionType && !['manifesto', 'fundraising', 'opposition_research'].includes(actionType) && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Target Zones (empty = national)</label>
          <div className="flex flex-wrap gap-2">
            {AZ_IDS.map(az => (
              <button key={az} onClick={() => toggleAz(az)}
                className={`px-2 py-1 text-xs rounded transition-colors duration-150 ${targetAzs.includes(az) ? 'bg-accent text-bg-primary' : 'bg-bg-tertiary hover:bg-bg-tertiary/70'}`}>
                {ADMIN_ZONES[az]?.split(' ')[0] ?? `AZ ${az}`}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Language selector */}
      {['rally', 'advertising', 'ground_game'].includes(actionType) && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Language</label>
          <select value={language} onChange={e => setLanguage(e.target.value)}
            className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            {['english', 'hausa', 'yoruba', 'igbo', 'arabic', 'pidgin', 'mandarin'].map(l => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
      )}

      {/* Action-specific params */}
      {actionType === 'advertising' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Medium</label>
          <select value={(params.medium as string) ?? 'radio'} onChange={e => setParams({ ...params, medium: e.target.value })}
            className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            <option value="radio">Radio</option>
            <option value="tv">TV</option>
            <option value="internet">Internet</option>
          </select>
          <label className="text-xs text-text-secondary block mb-1 mt-2">Budget ({((params.budget as number) ?? 1.0).toFixed(1)})</label>
          <input type="range" min={0.5} max={3} step={0.1} value={(params.budget as number) ?? 1.0}
            onChange={e => setParams({ ...params, budget: parseFloat(e.target.value) })}
            className="w-full accent-accent" />
        </div>
      )}

      {actionType === 'ground_game' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Intensity ({((params.intensity as number) ?? 1.0).toFixed(1)})</label>
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
          <p className="text-xs text-danger mt-1">Warning: Patronage increases exposure risk</p>
        </div>
      )}

      {actionType === 'opposition_research' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Target Party</label>
          <select value={targetParty} onChange={e => setTargetParty(e.target.value)}
            className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            <option value="">-- Select --</option>
            {parties.filter(p => p.name !== party).map(p => (
              <option key={p.name} value={p.name}>{p.name}</option>
            ))}
          </select>
        </div>
      )}

      {actionType === 'ethnic_mobilization' && (
        <div>
          <p className="text-xs text-danger">Warning: Ethnic mobilization increases exposure risk</p>
        </div>
      )}

      {actionType === 'poll' && (
        <div>
          <label className="text-xs text-text-secondary block mb-1">Poll Tier (cost = tier PC)</label>
          <select value={(params.poll_tier as number) ?? 1}
            onChange={e => setParams({ ...params, poll_tier: parseInt(e.target.value) })}
            className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
            {[1, 2, 3, 4, 5].map(t => (
              <option key={t} value={t}>Tier {t} ({t} PC)</option>
            ))}
          </select>
        </div>
      )}

      {actionType === 'eto_engagement' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Category</label>
            <select value={(params.category as string) ?? 'Mobilization'}
              onChange={e => setParams({ ...params, category: e.target.value })}
              className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              {['Mobilization', 'Elite', 'Economic', 'Legitimacy'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Score Change</label>
            <input type="number" min={1} max={5} value={(params.score_change as number) ?? 2}
              onChange={e => setParams({ ...params, score_change: parseInt(e.target.value) })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
          </div>
        </div>
      )}

      {actionType === 'pledge' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Issue Dimension</label>
            <select value={(params.dimension as number) ?? 0}
              onChange={e => setParams({ ...params, dimension: parseInt(e.target.value) })}
              className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              {issueNames.map((name, i) => <option key={i} value={i}>{name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Description</label>
            <input type="text" value={(params.description as string) ?? ''}
              onChange={e => setParams({ ...params, description: e.target.value })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
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
              className="bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors">
              {['positive', 'negative', 'contrast'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Narrative</label>
            <input type="text" value={(params.narrative as string) ?? ''}
              onChange={e => setParams({ ...params, narrative: e.target.value })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
              placeholder="Media narrative" />
          </div>
        </div>
      )}

      {actionType === 'endorsement' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-text-secondary block mb-1">Endorser Type</label>
            <input type="text" value={(params.endorser_type as string) ?? ''}
              onChange={e => setParams({ ...params, endorser_type: e.target.value })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
              placeholder="e.g. Traditional ruler, Celebrity" />
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Endorser Name</label>
            <input type="text" value={(params.endorser_name as string) ?? ''}
              onChange={e => setParams({ ...params, endorser_name: e.target.value })}
              className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-1.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
              placeholder="Name of endorser" />
          </div>
        </div>
      )}

      <button onClick={handleSubmit} disabled={!party || !actionType}
        className="w-full px-4 py-2 bg-accent rounded hover:bg-accent-hover text-bg-primary text-sm font-medium disabled:opacity-50 btn-accent">
        Add Action
      </button>
    </div>
  );
}
