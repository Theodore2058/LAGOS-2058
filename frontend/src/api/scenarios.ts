import api from './client';

export async function saveScenario(name: string) {
  const res = await api.post('/scenarios/save', { name });
  return res.data;
}

export async function listScenarios() {
  const res = await api.get('/scenarios/list');
  return res.data;
}

export async function getScenario(name: string) {
  const res = await api.get(`/scenarios/${encodeURIComponent(name)}`);
  return res.data;
}

export async function deleteScenario(name: string) {
  await api.delete(`/scenarios/${encodeURIComponent(name)}`);
}

export async function restoreScenario(name: string) {
  const res = await api.post(`/scenarios/${encodeURIComponent(name)}/restore`);
  return res.data;
}

export async function compareScenarios(a: string, b: string) {
  const res = await api.get(`/scenarios/compare/${encodeURIComponent(a)}/${encodeURIComponent(b)}`);
  return res.data;
}

export async function exportSession() {
  const res = await api.get('/scenarios/export/session');
  const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'lagos2058_session.json'; a.click();
  URL.revokeObjectURL(url);
}

export async function importSession(file: File) {
  const text = await file.text();
  const data = JSON.parse(text);
  const res = await api.post('/scenarios/import/session', { parties: data.parties ?? [] });
  return res.data;
}
