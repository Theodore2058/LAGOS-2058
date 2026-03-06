import { useState, useEffect, useMemo } from 'react';
import type { EngineParams } from '../types';
import { fetchEngineParamsDefaults } from '../api/config';

interface SliderParam {
  key: keyof EngineParams;
  label: string;
  min: number;
  max: number;
  step: number;
  tooltip: string;
}

interface ParamGroup {
  title: string;
  desc: string;
  params: SliderParam[];
}

const PARAM_GROUPS: ParamGroup[] = [
  {
    title: 'Spatial Model',
    desc: 'How voters evaluate parties on issues, ethnicity, religion, and economics',
    params: [
      { key: 'q', label: 'Proximity-Directional Mix', min: 0, max: 1, step: 0.05, tooltip: 'q=0 pure directional, q=1 pure proximity' },
      { key: 'beta_s', label: 'Spatial Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on spatial (issue) distance in utility' },
      { key: 'alpha_e', label: 'Ethnic Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on ethnic affinity between voter and party leader' },
      { key: 'alpha_r', label: 'Religious Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on religious affinity' },
      { key: 'beta_econ', label: 'Economic Voting', min: 0, max: 2, step: 0.05, tooltip: 'Weight on economic positioning match' },
      { key: 'scale', label: 'Voter Rationality', min: 0.1, max: 10, step: 0.1, tooltip: 'Softmax scale: higher = more deterministic voting' },
    ],
  },
  {
    title: 'Turnout Model',
    desc: 'What drives voter participation — abstention threshold, alienation, and indifference',
    params: [
      { key: 'tau_0', label: 'Baseline Abstention', min: 0, max: 5, step: 0.1, tooltip: 'Utility of abstaining. Higher = lower turnout' },
      { key: 'tau_1', label: 'Alienation Strength', min: 0, max: 2, step: 0.05, tooltip: 'How much low max-utility reduces turnout' },
      { key: 'tau_2', label: 'Indifference Strength', min: 0, max: 2, step: 0.05, tooltip: 'How much small utility gaps reduce turnout' },
    ],
  },
  {
    title: 'Noise & Uncertainty',
    desc: 'Monte Carlo variance, national/regional swings, and turnout fluctuations',
    params: [
      { key: 'kappa', label: 'Noise Concentration', min: 50, max: 1000, step: 10, tooltip: 'Dirichlet concentration. Higher = less MC noise' },
      { key: 'sigma_national', label: 'National Swing', min: 0, max: 0.5, step: 0.01, tooltip: 'SD of national-level random shock to vote shares' },
      { key: 'sigma_regional', label: 'Regional Swing', min: 0, max: 0.5, step: 0.01, tooltip: 'SD of regional random shocks' },
      { key: 'sigma_turnout', label: 'Turnout Noise', min: 0, max: 0.3, step: 0.01, tooltip: 'SD of national turnout noise on logit scale' },
      { key: 'sigma_turnout_regional', label: 'Regional Turnout Noise', min: 0, max: 0.3, step: 0.01, tooltip: 'SD of regional turnout noise' },
    ],
  },
];

const ALL_PARAMS = PARAM_GROUPS.flatMap(g => g.params);

const PRESETS: { name: string; desc: string; values: Partial<EngineParams> }[] = [
  { name: 'Default Static', desc: 'Calibrated for one-shot elections', values: { tau_0: 4.5, scale: 1.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, kappa: 200, sigma_national: 0.10, sigma_regional: 0.15 } },
  { name: 'Campaign Mode', desc: 'Lower tau for first-election-in-decades', values: { tau_0: 3.0, scale: 1.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, kappa: 200, sigma_national: 0.10, sigma_regional: 0.15 } },
  { name: 'High Turnout', desc: 'Energized electorate', values: { tau_0: 2.0, tau_1: 0.1, tau_2: 0.2 } },
  { name: 'Low Turnout', desc: 'Voter apathy scenario', values: { tau_0: 5.0, tau_1: 0.5, tau_2: 0.8 } },
  { name: 'Identity-Driven', desc: 'Ethnic/religious voting dominates', values: { alpha_e: 4.5, alpha_r: 3.5, beta_s: 1.5, beta_econ: 0.1 } },
  { name: 'Policy-Driven', desc: 'Issue positions matter most', values: { alpha_e: 1.0, alpha_r: 0.5, beta_s: 4.5, beta_econ: 0.8 } },
];

interface Props {
  params: EngineParams;
  onChange: (params: EngineParams) => void;
}

export function ParamsEditor({ params, onChange }: Props) {
  const update = (key: keyof EngineParams, value: number) => {
    onChange({ ...params, [key]: value });
  };

  const applyPreset = (preset: typeof PRESETS[number]) => {
    onChange({ ...params, ...preset.values });
  };

  const modifiedCount = ALL_PARAMS.filter(p => params[p.key] !== DEFAULT_PARAMS[p.key]).length;

  // Check which preset is active (all preset values match current params)
  const activePreset = useMemo(() => {
    return PRESETS.find(preset =>
      Object.entries(preset.values).every(([k, v]) => params[k as keyof EngineParams] === v)
    )?.name ?? null;
  }, [params]);

  const resetGroup = (group: ParamGroup) => {
    const updated = { ...params };
    for (const p of group.params) {
      (updated as Record<string, unknown>)[p.key] = DEFAULT_PARAMS[p.key];
    }
    onChange(updated as EngineParams);
  };

  return (
    <div className="space-y-5">
      {/* Presets */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] text-text-secondary uppercase tracking-[0.1em] font-medium">Presets</span>
          {modifiedCount > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 bg-accent/10 text-accent rounded">{modifiedCount} modified</span>
          )}
        </div>
        <div className="flex gap-2 flex-wrap">
          {PRESETS.map(preset => {
            const isActive = activePreset === preset.name;
            return (
              <button key={preset.name} onClick={() => applyPreset(preset)}
                className={`px-3 py-1.5 text-xs border rounded-md transition-colors ${
                  isActive
                    ? 'bg-accent/15 border-accent/50 text-accent font-medium'
                    : 'bg-bg-tertiary border-bg-quaternary/30 hover:border-accent/50 hover:text-accent'
                }`}
                title={preset.desc}>
                {preset.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Parameter Groups */}
      {PARAM_GROUPS.map(group => {
        const groupModified = group.params.filter(p => params[p.key] !== DEFAULT_PARAMS[p.key]).length;
        return (
          <div key={group.title} className="border-t border-bg-tertiary/30 pt-4">
            <div className="flex items-center justify-between mb-0.5">
              <h4 className="text-xs font-semibold">{group.title}</h4>
              {groupModified > 0 && (
                <button onClick={() => resetGroup(group)}
                  className="text-[10px] text-text-secondary/50 hover:text-danger transition-colors">
                  Reset ({groupModified})
                </button>
              )}
            </div>
            <p className="text-[10px] text-text-secondary mb-3">{group.desc}</p>
            <div className="space-y-1">
              {group.params.map(p => {
                const val = params[p.key] as number;
                const isModified = val !== DEFAULT_PARAMS[p.key];
                const pct = ((val - p.min) / (p.max - p.min)) * 100;
                return (
                  <div key={p.key} className="flex items-center gap-3 py-1 px-2 -mx-2 rounded hover:bg-bg-tertiary/30 transition-colors group/param">
                    <span className={`w-48 text-xs shrink-0 flex items-center gap-1 ${isModified ? 'text-accent font-medium' : 'text-text-secondary'}`}>
                      {isModified && <span className="text-accent">*</span>}
                      {p.label}
                      <span className="relative">
                        <svg className="w-3 h-3 text-text-secondary/30 group-hover/param:text-text-secondary/60 transition-colors cursor-help" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                          <circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
                        </svg>
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 text-[10px] bg-bg-primary border border-bg-tertiary rounded text-text-secondary whitespace-nowrap opacity-0 group-hover/param:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                          {p.tooltip}
                        </span>
                      </span>
                    </span>
                    <div className="flex-1 relative">
                      <input type="range" min={p.min} max={p.max} step={p.step} value={val}
                        onChange={(e) => update(p.key, parseFloat(e.target.value))}
                        className="w-full h-1.5 accent-accent" />
                      {isModified && (
                        <div className="absolute -bottom-1 left-0 w-full h-0.5">
                          <div className="h-full bg-accent/30 rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                      )}
                    </div>
                    <input type="number" min={p.min} max={p.max} step={p.step} value={val}
                      onChange={(e) => update(p.key, parseFloat(e.target.value) || p.min)}
                      className={`w-20 bg-bg-tertiary border rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors ${isModified ? 'border-accent/40' : 'border-bg-quaternary/50'}`} />
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Simulation Settings */}
      <div className="border-t border-bg-tertiary/30 pt-4">
        <h4 className="text-xs font-semibold mb-0.5">Simulation</h4>
        <p className="text-[10px] text-text-secondary mb-3">Monte Carlo sampling and reproducibility</p>
        <div className="space-y-1">
          <div className="flex items-center gap-3 py-1 px-2 -mx-2 rounded hover:bg-bg-tertiary/30 transition-colors">
            <span className="w-48 text-xs text-text-secondary shrink-0">Monte Carlo Runs</span>
            <input type="number" min={1} max={1000} value={params.n_monte_carlo}
              onChange={(e) => update('n_monte_carlo', parseInt(e.target.value) || 100)}
              className="w-20 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
          </div>
          <div className="flex items-center gap-3 py-1 px-2 -mx-2 rounded hover:bg-bg-tertiary/30 transition-colors">
            <span className="w-48 text-xs text-text-secondary shrink-0">Random Seed</span>
            <input type="number" value={params.seed ?? ''} placeholder="(random)"
              onChange={(e) => onChange({ ...params, seed: e.target.value ? parseInt(e.target.value) : null })}
              className="w-20 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
          </div>
        </div>
      </div>
    </div>
  );
}

export const DEFAULT_PARAMS: EngineParams = {
  q: 0.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, scale: 1.5,
  tau_0: 4.5, tau_1: 0.3, tau_2: 0.5, beta_econ: 0.3,
  kappa: 200, sigma_national: 0.10, sigma_regional: 0.15,
  sigma_turnout: 0.0, sigma_turnout_regional: 0.0,
  n_monte_carlo: 100, seed: null,
};

export default function ParamsPage() {
  const [params, setParams] = useState<EngineParams>(DEFAULT_PARAMS);
  const [defaults, setDefaults] = useState<EngineParams | null>(null);

  useEffect(() => {
    fetchEngineParamsDefaults().then(d => {
      const full = { ...DEFAULT_PARAMS, ...d };
      setDefaults(full);
      setParams(full);
    });
  }, []);

  const resetToDefaults = () => { if (defaults) setParams({ ...defaults }); };

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold">Engine Parameters</h2>
        <button onClick={resetToDefaults}
          className="px-3 py-1.5 text-sm bg-bg-tertiary border border-bg-quaternary/30 rounded-md hover:border-danger/50 hover:text-danger transition-colors flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M1 4v6h6" /><path d="M3.51 15a9 9 0 102.13-9.36L1 10" /></svg>
          Reset All
        </button>
      </div>
      <p className="text-xs text-text-secondary mb-6">
        Tune the Merrill-Grofman spatial voting model. Changes apply to the next election or campaign run.
        Hover over <span className="inline-flex items-center"><svg className="w-3 h-3 text-text-secondary/50 mx-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><circle cx="12" cy="12" r="10" /></svg></span> for parameter details.
      </p>
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary/50">
        <ParamsEditor params={params} onChange={setParams} />
      </div>
    </div>
  );
}
