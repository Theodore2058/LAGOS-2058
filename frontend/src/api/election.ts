import api from './client';
import type { Party, EngineParams, ElectionResults } from '../types';

export interface RunElectionRequest {
  params: Omit<EngineParams, 'n_monte_carlo' | 'seed'>;
  parties: Party[];
  n_monte_carlo: number;
  seed: number | null;
}

export async function runElection(req: RunElectionRequest): Promise<ElectionResults> {
  const res = await api.post('/election/run', req, { timeout: 120000 });
  return res.data;
}
