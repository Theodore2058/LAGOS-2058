import api from './client';
import type { CrisisInput } from '../types';

export interface CrisisTemplate {
  name: string;
  description: string;
  affected_azs: number[] | null;
  salience_shifts: Record<string, number>;
  valence_effects: Record<string, number> | null;
  awareness_boost: Record<string, number> | null;
  tau_modifier: number;
}

export interface StoredCrisis extends CrisisInput {
  id: number;
}

export async function fetchTemplates(): Promise<CrisisTemplate[]> {
  const res = await api.get('/crises/templates');
  return res.data;
}

export async function fetchCrises(): Promise<StoredCrisis[]> {
  const res = await api.get('/crises');
  return res.data.crises;
}

export async function createCrisis(crisis: CrisisInput): Promise<StoredCrisis> {
  const res = await api.post('/crises', crisis);
  return res.data;
}

export async function updateCrisis(id: number, crisis: CrisisInput): Promise<StoredCrisis> {
  const res = await api.put(`/crises/${id}`, crisis);
  return res.data;
}

export async function deleteCrisis(id: number): Promise<void> {
  await api.delete(`/crises/${id}`);
}
