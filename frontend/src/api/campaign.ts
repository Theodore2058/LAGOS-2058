import api from './client';
import type { Party, EngineParams, ActionInput, CrisisInput } from '../types';

export interface PartyStatus {
  name: string;
  pc: number;
  cohesion: number;
  exposure: number;
  momentum: number;
  momentum_direction: string;
  vote_share: number;
  seats: number;
  awareness: number;
  eto_score: number;
}

export interface CampaignStateResponse {
  turn: number;
  n_turns: number;
  phase: string;
  party_statuses: PartyStatus[];
  scandal_history: Record<string, unknown>[];
  poll_results: Record<string, unknown>[];
}

export interface TurnResult {
  turn: number;
  state: CampaignStateResponse;
  national_vote_shares: Record<string, number>;
  national_turnout: number;
  seat_counts: Record<string, number>;
  total_seats: number;
  actions_resolved: Record<string, unknown>[];
  synergies: Record<string, unknown>[];
  scandals: Record<string, unknown>[];
}

export async function newCampaign(parties: Party[], params: Omit<EngineParams, 'n_monte_carlo' | 'seed'>,
  n_monte_carlo: number, seed: number | null, n_turns: number): Promise<CampaignStateResponse> {
  const res = await api.post('/campaign/new', { parties, params, n_monte_carlo, seed, n_turns });
  return res.data;
}

export async function getCampaignState(): Promise<CampaignStateResponse> {
  const res = await api.get('/campaign/state');
  return res.data;
}

export async function advanceTurn(actions: ActionInput[], crises: CrisisInput[]): Promise<TurnResult> {
  const res = await api.post('/campaign/advance', { actions, crises }, { timeout: 120000 });
  return res.data;
}

export async function resetCampaign(): Promise<CampaignStateResponse> {
  const res = await api.post('/campaign/reset');
  return res.data;
}

export async function getCampaignHistory(): Promise<TurnResult[]> {
  const res = await api.get('/campaign/history');
  return res.data;
}
