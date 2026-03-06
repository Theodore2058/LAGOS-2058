import api from './client';
import type { Party } from '../types';

export async function fetchParties(): Promise<Party[]> {
  const res = await api.get('/parties');
  return res.data.parties;
}

export async function createParty(party: Party): Promise<Party> {
  const res = await api.post('/parties', party);
  return res.data;
}

export async function updateParty(originalName: string, party: Party): Promise<Party> {
  const res = await api.put(`/parties/${encodeURIComponent(originalName)}`, party);
  return res.data;
}

export async function deleteParty(name: string): Promise<void> {
  await api.delete(`/parties/${encodeURIComponent(name)}`);
}

export async function loadExampleParties(): Promise<Party[]> {
  const res = await api.post('/parties/load-examples');
  return res.data.parties;
}

export async function exportParties(): Promise<Party[]> {
  const res = await api.get('/parties/export');
  return res.data.parties;
}

export async function importParties(parties: Party[]): Promise<Party[]> {
  const res = await api.post('/parties/import', { parties });
  return res.data.parties;
}
