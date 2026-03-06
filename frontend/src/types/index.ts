export interface Party {
  name: string;
  full_name: string;
  positions: number[];
  valence: number;
  leader_ethnicity: string;
  religious_alignment: string;
  demographic_coefficients: Record<string, Record<string, number>> | null;
  regional_strongholds: Record<string, number> | null;
  economic_positioning: number;
  color: string;
}

export interface EngineParams {
  q: number;
  beta_s: number;
  alpha_e: number;
  alpha_r: number;
  scale: number;
  tau_0: number;
  tau_1: number;
  tau_2: number;
  beta_econ: number;
  kappa: number;
  sigma_national: number;
  sigma_regional: number;
  sigma_turnout: number;
  sigma_turnout_regional: number;
  n_monte_carlo: number;
  seed: number | null;
}

export interface ElectionResults {
  national_vote_shares: Record<string, number>;
  national_vote_counts: Record<string, number>;
  national_turnout: number;
  seat_counts: Record<string, number>;
  seat_std: Record<string, number>;
  win_probability: Record<string, number>;
  enp: number;
  spread_check: Record<string, SpreadCheck>;
  zonal_results: ZonalResult[];
  state_results: StateResult[];
  lga_results: LGAResult[];
  swing_lgas: SwingLGA[];
}

export interface SpreadCheck {
  states_above_25: number;
  met: boolean;
}

export interface ZonalResult {
  az: number;
  az_name: string;
  turnout: number;
  vote_shares: Record<string, number>;
  winner: string;
}

export interface StateResult {
  state: string;
  az: number;
  turnout: number;
  vote_shares: Record<string, number>;
  winner: string;
}

export interface LGAResult {
  lga: string;
  state: string;
  az: number;
  turnout: number;
  vote_shares: Record<string, number>;
  winner: string;
}

export interface SwingLGA {
  lga: string;
  state: string;
  margin: number;
  top_parties: string[];
}

export interface ActionInput {
  party: string;
  action_type: string;
  target_lgas: number[] | null;
  target_azs: number[] | null;
  target_party: string | null;
  parameters: Record<string, unknown>;
}

export interface CrisisInput {
  name: string;
  turn: number;
  affected_azs: number[] | null;
  affected_lgas: number[] | null;
  salience_shifts: Record<string, number>;
  valence_effects: Record<string, number> | null;
  awareness_boost: Record<string, number> | null;
  tau_modifier: number;
  description: string;
}

export interface CampaignState {
  turn: number;
  political_capital: Record<string, number>;
  exposure: Record<string, number>;
  cohesion: Record<string, number>;
  momentum: Record<string, number>;
  momentum_direction: Record<string, string>;
  previous_shares: Record<string, number>;
  scandal_history: unknown[];
  poll_results: unknown[];
}

export interface ActionType {
  name: string;
  base_cost: number;
  description: string;
  scope: 'lga' | 'regional' | 'none';
  parameters: Record<string, unknown>;
}

export const ADMIN_ZONES: Record<number, string> = {
  1: 'Lagos (Southwest urban)',
  2: 'Niger (Southwest rural)',
  3: 'Confluence (South-Central)',
  4: 'Littoral (South-South)',
  5: 'Eastern (Southeast)',
  6: 'Central (North-Central)',
  7: 'Chad (Northeast)',
  8: 'Savanna (Northwest)',
};
