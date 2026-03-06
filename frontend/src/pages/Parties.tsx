import { useState, useEffect, useCallback } from 'react';
import type { Party } from '../types';
import { fetchParties, createParty, updateParty, deleteParty, loadExampleParties, exportParties, importParties } from '../api/parties';
import { fetchIssueNames, fetchEthnicGroups, fetchReligiousGroups, fetchAdminZones } from '../api/config';
import PartyForm from '../components/PartyForm';
import PartyComparison from '../components/PartyComparison';
import { useToast } from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';

const BLANK_PARTY: Party = {
  name: '', full_name: '', positions: new Array(28).fill(0),
  valence: 0, leader_ethnicity: '', religious_alignment: '',
  demographic_coefficients: null, regional_strongholds: null,
  economic_positioning: 0, color: '#3b82f6',
};

type Tab = 'editor' | 'compare';

export default function Parties() {
  const [parties, setParties] = useState<Party[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [editing, setEditing] = useState<Party | null>(null);
  const [isNew, setIsNew] = useState(false);
  const [tab, setTab] = useState<Tab>('editor');
  const [compareSelected, setCompareSelected] = useState<Set<string>>(new Set());
  const [issueNames, setIssueNames] = useState<string[]>([]);
  const [ethnicGroups, setEthnicGroups] = useState<string[]>([]);
  const [religiousGroups, setReligiousGroups] = useState<string[]>([]);
  const [adminZones, setAdminZones] = useState<{ id: number; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const { toast } = useToast();

  const loadParties = useCallback(async () => {
    try {
      const data = await fetchParties();
      setParties(data);
    } catch (e) { console.error('Failed to load parties:', e); setError('Failed to load parties'); }
  }, []);

  useEffect(() => {
    loadParties();
    fetchIssueNames().then(setIssueNames).catch(e => console.error('Failed to fetch issue names:', e));
    fetchEthnicGroups().then(setEthnicGroups).catch(e => console.error('Failed to fetch ethnic groups:', e));
    fetchReligiousGroups().then(setReligiousGroups).catch(e => console.error('Failed to fetch religious groups:', e));
    fetchAdminZones().then(setAdminZones).catch(e => console.error('Failed to fetch admin zones:', e));
  }, [loadParties]);

  const handleSelect = (name: string) => {
    setSelected(name);
    const party = parties.find(p => p.name === name);
    if (party) { setEditing({ ...party }); setIsNew(false); }
  };

  const handleNew = () => {
    setEditing({ ...BLANK_PARTY });
    setIsNew(true);
    setSelected(null);
  };

  const handleDuplicate = (p: Party) => {
    setEditing({ ...p, name: p.name + '_COPY', full_name: p.full_name + ' (Copy)' });
    setIsNew(true);
    setSelected(null);
  };

  const handleSave = async (party: Party) => {
    setLoading(true);
    setError(null);
    try {
      if (isNew) {
        await createParty(party);
      } else if (selected) {
        await updateParty(selected, party);
      }
      await loadParties();
      setSelected(party.name);
      setEditing(party);
      setIsNew(false);
      toast(`${isNew ? 'Created' : 'Updated'} "${party.name}"`, 'success');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Save failed';
      setError(msg);
    } finally { setLoading(false); }
  };

  const handleDelete = async (name: string) => {
    try {
      await deleteParty(name);
      if (selected === name) { setSelected(null); setEditing(null); }
      await loadParties();
      toast(`Deleted "${name}"`, 'success');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete party');
    }
  };

  const handleLoadExamples = async () => {
    setLoading(true);
    try {
      const data = await loadExampleParties();
      setParties(data);
      toast(`Loaded ${data.length} example parties`, 'success');
    } catch (e) { console.error('Failed to load examples:', e); setError('Failed to load examples'); }
    setLoading(false);
  };

  const handleExport = async () => {
    const data = await exportParties();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'lagos2058_parties.json'; a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const text = await file.text();
      try {
        const data = JSON.parse(text);
        const partyList = Array.isArray(data) ? data : data.parties ?? [];
        await importParties(partyList);
        await loadParties();
      } catch (e) { console.error('Import failed:', e); setError('Invalid JSON file'); }
    };
    input.click();
  };

  const toggleCompare = (name: string) => {
    const next = new Set(compareSelected);
    if (next.has(name)) next.delete(name); else next.add(name);
    setCompareSelected(next);
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 bg-bg-secondary border-r border-bg-tertiary flex flex-col shrink-0">
        <div className="p-3 border-b border-bg-tertiary">
          <div className="flex gap-2 mb-2">
            <button onClick={handleNew} className="flex-1 px-2 py-1.5 text-xs bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium">+ Add</button>
            <button onClick={handleLoadExamples} className="flex-1 px-2 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80" disabled={loading}>Load Examples</button>
          </div>
          <div className="flex gap-2">
            <button onClick={handleExport} className="flex-1 px-2 py-1 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Export</button>
            <button onClick={handleImport} className="flex-1 px-2 py-1 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80">Import</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {parties.map(p => (
            <div key={p.name}
              className={`flex items-center gap-2 px-3 py-2.5 cursor-pointer border-b border-bg-tertiary/30 transition-colors ${selected === p.name ? 'bg-accent/15 border-l-2 border-l-accent' : 'hover:bg-bg-tertiary/30'}`}
              onClick={() => handleSelect(p.name)}>
              {tab === 'compare' && (
                <input type="checkbox" checked={compareSelected.has(p.name)}
                  onChange={(e) => { e.stopPropagation(); toggleCompare(p.name); }}
                  className="accent-accent" />
              )}
              <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: p.color }} />
              <span className="text-sm flex-1 truncate">{p.name}</span>
              <span className="text-xs text-text-secondary truncate max-w-20">{p.leader_ethnicity}</span>
              <button onClick={(e) => { e.stopPropagation(); setDeleteTarget(p.name); }}
                className="text-danger/60 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors" aria-label={`Delete ${p.name}`}>
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
              </button>
            </div>
          ))}
          {parties.length === 0 && (
            <p className="p-3 text-xs text-text-secondary">No parties. Click "Add" or "Load Examples".</p>
          )}
        </div>
        <div className="p-2 border-t border-bg-tertiary text-xs text-text-secondary text-center">
          {parties.length} parties
        </div>
      </div>

      {/* Main panel */}
      <div className="flex-1 overflow-y-auto">
        {/* Tabs */}
        <div className="flex border-b border-bg-tertiary px-4">
          <button onClick={() => setTab('editor')}
            className={`px-4 py-2 text-sm ${tab === 'editor' ? 'border-b-2 border-accent text-accent' : 'text-text-secondary'}`}>Editor</button>
          <button onClick={() => setTab('compare')}
            className={`px-4 py-2 text-sm ${tab === 'compare' ? 'border-b-2 border-accent text-accent' : 'text-text-secondary'}`}>Compare</button>
        </div>

        {error && <div className="mx-4 mt-2 p-2 bg-danger/20 text-danger text-sm rounded flex items-center justify-between border border-danger/30">{error}<button onClick={() => setError(null)} className="text-danger/60 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-colors shrink-0 ml-2" aria-label="Dismiss error"><svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg></button></div>}

        <div className="p-4">
          {tab === 'editor' && editing && (
            <div>
              <PartyForm
                party={editing}
                issueNames={issueNames}
                ethnicGroups={ethnicGroups}
                religiousGroups={religiousGroups}
                adminZones={adminZones}
                onSave={handleSave}
                onCancel={() => { setEditing(null); setSelected(null); }}
                isNew={isNew}
              />
              {!isNew && (
                <button onClick={() => handleDuplicate(editing)}
                  className="mt-4 px-3 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80">
                  Duplicate Party
                </button>
              )}
            </div>
          )}
          {tab === 'editor' && !editing && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <svg className="w-12 h-12 text-text-secondary/30 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2m8-4a4 4 0 100-8 4 4 0 000 8zm10 0l2 2m-2-2l-2 2m2-2l2-2m-2 2l-2-2" />
              </svg>
              <p className="text-text-secondary mb-1">No party selected</p>
              <p className="text-xs text-text-secondary/60">Select a party from the list or click "+ Add" to create a new one.</p>
            </div>
          )}
          {tab === 'compare' && (
            <PartyComparison
              parties={parties.filter(p => compareSelected.has(p.name))}
              issueNames={issueNames}
            />
          )}
        </div>
      </div>

      <ConfirmModal
        open={!!deleteTarget}
        title="Delete Party"
        message={`Permanently delete "${deleteTarget}"? This cannot be undone.`}
        confirmLabel="Delete"
        confirmDanger
        onConfirm={() => {
          if (deleteTarget) handleDelete(deleteTarget);
          setDeleteTarget(null);
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
