import api from './client';

export async function fetchIssueNames(): Promise<string[]> {
  const res = await api.get('/issue-names');
  return res.data.issue_names;
}

export async function fetchEngineParamsDefaults() {
  const res = await api.get('/engine-params/defaults');
  return res.data;
}

export async function fetchEthnicGroups(): Promise<string[]> {
  const res = await api.get('/ethnic-groups');
  return res.data.groups;
}

export async function fetchReligiousGroups(): Promise<string[]> {
  const res = await api.get('/religious-groups');
  return res.data.groups;
}

export async function fetchAdminZones(): Promise<{ id: number; name: string }[]> {
  const res = await api.get('/admin-zones');
  return res.data.zones;
}

export async function fetchActionTypes() {
  const res = await api.get('/action-types');
  return res.data.action_types;
}

export async function fetchPCConstants() {
  const res = await api.get('/pc-constants');
  return res.data;
}

export interface LGAInfo {
  index: number;
  name: string;
  state: string;
  az: number;
}

export async function fetchLGAs(): Promise<LGAInfo[]> {
  const res = await api.get('/lgas');
  return res.data.lgas;
}
