import { useState, useEffect } from 'react';
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

const PARAMS: SliderParam[] = [
  { key: 'q', label: 'Proximity-Directional Mix', min: 0, max: 1, step: 0.05, tooltip: 'q=0 pure directional, q=1 pure proximity' },
  { key: 'beta_s', label: 'Spatial Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on spatial (issue) distance in utility' },
  { key: 'alpha_e', label: 'Ethnic Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on ethnic affinity between voter and party leader' },
  { key: 'alpha_r', label: 'Religious Sensitivity', min: 0, max: 5, step: 0.1, tooltip: 'Weight on religious affinity' },
  { key: 'scale', label: 'Voter Rationality', min: 0.1, max: 10, step: 0.1, tooltip: 'Softmax scale: higher = more deterministic voting' },
  { key: 'tau_0', label: 'Baseline Abstention', min: 0, max: 5, step: 0.1, tooltip: 'Utility of abstaining. Higher = lower turnout' },
  { key: 'tau_1', label: 'Alienation Strength', min: 0, max: 2, step: 0.05, tooltip: 'How much low max-utility reduces turnout' },
  { key: 'tau_2', label: 'Indifference Strength', min: 0, max: 2, step: 0.05, tooltip: 'How much small utility gaps reduce turnout' },
  { key: 'beta_econ', label: 'Economic Voting', min: 0, max: 2, step: 0.05, tooltip: 'Weight on economic positioning match' },
  { key: 'kappa', label: 'Noise Concentration', min: 50, max: 1000, step: 10, tooltip: 'Dirichlet concentration. Higher = less MC noise' },
  { key: 'sigma_national', label: 'National Swing', min: 0, max: 0.5, step: 0.01, tooltip: 'SD of national-level random shock to vote shares' },
  { key: 'sigma_regional', label: 'Regional Swing', min: 0, max: 0.5, step: 0.01, tooltip: 'SD of regional random shocks' },
  { key: 'sigma_turnout', label: 'Turnout Noise', min: 0, max: 0.3, step: 0.01, tooltip: 'SD of national turnout noise on logit scale' },
  { key: 'sigma_turnout_regional', label: 'Regional Turnout Noise', min: 0, max: 0.3, step: 0.01, tooltip: 'SD of regional turnout noise' },
];

const PRESETS: Record<string, Partial<EngineParams>> = {
  'Default Static': { tau_0: 4.5, scale: 1.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, kappa: 200, sigma_national: 0.10, sigma_regional: 0.15 },
  'Campaign Mode': { tau_0: 3.0, scale: 1.5, beta_s: 3.0, alpha_e: 3.0, alpha_r: 2.0, kappa: 200, sigma_national: 0.10, sigma_regional: 0.15 },
  'High Turnout': { tau_0: 2.0, tau_1: 0.1, tau_2: 0.2 },
  'Low Turnout': { tau_0: 5.0, tau_1: 0.5, tau_2: 0.8 },
  'Identity-Driven': { alpha_e: 4.5, alpha_r: 3.5, beta_s: 1.5, beta_econ: 0.1 },
  'Policy-Driven': { alpha_e: 1.0, alpha_r: 0.5, beta_s: 4.5, beta_econ: 0.8 },
};

interface Props {
  params: EngineParams;
  onChange: (params: EngineParams) => void;
}

export function ParamsEditor({ params, onChange }: Props) {
  const update = (key: keyof EngineParams, value: number) => {
    onChange({ ...params, [key]: value });
  };

  const applyPreset = (name: string) => {
    const preset = PRESETS[name];
    if (preset) onChange({ ...params, ...preset });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-text-secondary">Presets:</span>
        {Object.keys(PRESETS).map(name => (
          <button key={name} onClick={() => applyPreset(name)}
            className="px-2 py-1 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80">{name}</button>
        ))}
      </div>

      <div className="space-y-2">
        {PARAMS.map(p => {
          const val = params[p.key] as number;
          return (
            <div key={p.key} className="flex items-center gap-3 group" title={p.tooltip}>
              <span className="w-48 text-xs text-text-secondary">{p.label}</span>
              <input type="range" min={p.min} max={p.max} step={p.step} value={val}
                onChange={(e) => update(p.key, parseFloat(e.target.value))}
                className="flex-1 h-1.5 accent-accent" />
              <input type="number" min={p.min} max={p.max} step={p.step} value={val}
                onChange={(e) => update(p.key, parseFloat(e.target.value) || p.min)}
                className="w-20 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
            </div>
          );
        })}

        {/* MC and seed */}
        <div className="flex items-center gap-3">
          <span className="w-48 text-xs text-text-secondary">Monte Carlo Runs</span>
          <input type="number" min={1} max={1000} value={params.n_monte_carlo}
            onChange={(e) => update('n_monte_carlo', parseInt(e.target.value) || 100)}
            className="w-20 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
        </div>
        <div className="flex items-center gap-3">
          <span className="w-48 text-xs text-text-secondary">Random Seed</span>
          <input type="number" value={params.seed ?? ''} placeholder="(random)"
            onChange={(e) => update('seed', e.target.value ? parseInt(e.target.value) : null as unknown as number)}
            className="w-20 bg-bg-tertiary border border-bg-quaternary/50 rounded-md px-2 py-0.5 text-xs text-center focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors" />
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
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Engine Parameters</h2>
        <button onClick={resetToDefaults}
          className="px-3 py-1.5 text-sm bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Reset to Defaults</button>
      </div>
      <div className="bg-bg-secondary rounded-lg p-6 border border-bg-tertiary">
        <ParamsEditor params={params} onChange={setParams} />
      </div>
    </div>
  );
}
