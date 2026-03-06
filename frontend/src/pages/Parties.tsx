import { useState, useEffect, useCallback, useMemo } from 'react';
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
  const [search, setSearch] = useState('');
  const { toast } = useToast();

  const filteredParties = useMemo(() => {
    if (!search.trim()) return parties;
    const q = search.toLowerCase();
    return parties.filter(p =>
      p.name.toLowerCase().includes(q) || p.full_name.toLowerCase().includes(q) || p.leader_ethnicity.toLowerCase().includes(q)
    );
  }, [parties, search]);

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
        <div className="p-3 border-b border-bg-tertiary space-y-2">
          <div className="flex gap-2">
            <button onClick={handleNew} className="flex-1 px-2 py-1.5 text-xs bg-accent rounded hover:bg-accent-hover text-bg-primary font-medium btn-accent">+ Add</button>
            <button onClick={handleLoadExamples} className="flex-1 px-2 py-1.5 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors" disabled={loading}>
              {loading ? 'Loading...' : 'Load Examples'}
            </button>
          </div>
          <div className="flex gap-2">
            <button onClick={handleExport} className="flex-1 px-2 py-1 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center justify-center gap-1">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
              Export
            </button>
            <button onClick={handleImport} className="flex-1 px-2 py-1 text-xs bg-bg-tertiary rounded hover:bg-bg-tertiary/80 transition-colors flex items-center justify-center gap-1">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
              Import
            </button>
          </div>
          {parties.length > 5 && (
            <div className="relative">
              <svg className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-text-secondary/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Filter parties..."
                className="w-full bg-bg-tertiary border border-bg-quaternary/50 rounded px-2 pl-7 py-1 text-xs focus:border-accent transition-colors placeholder:text-text-secondary/30" />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-1.5 top-1/2 -translate-y-1/2 text-text-secondary/40 hover:text-text-secondary">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                </button>
              )}
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          {filteredParties.map(p => (
            <div key={p.name}
              className={`flex items-center gap-2 px-3 py-2 cursor-pointer border-b border-bg-tertiary/30 transition-colors group/party ${selected === p.name ? 'bg-accent/15 border-l-2 border-l-accent' : 'hover:bg-bg-tertiary/30'}`}
              onClick={() => handleSelect(p.name)}
              title={p.full_name || p.name}>
              {tab === 'compare' && (
                <input type="checkbox" checked={compareSelected.has(p.name)}
                  onChange={(e) => { e.stopPropagation(); toggleCompare(p.name); }}
                  className="accent-accent" />
              )}
              <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: p.color }} />
              <div className="flex-1 min-w-0">
                <span className="text-sm block truncate">{p.name}</span>
                <span className="text-[10px] text-text-secondary truncate block">
                  {p.leader_ethnicity}{p.valence !== 0 ? ` · v${p.valence > 0 ? '+' : ''}${p.valence.toFixed(1)}` : ''}
                </span>
              </div>
              <div className="flex items-center gap-0.5 shrink-0">
                <button onClick={(e) => { e.stopPropagation(); handleDuplicate(p); }}
                  className="opacity-0 group-hover/party:opacity-100 text-text-secondary/40 hover:text-accent p-0.5 rounded hover:bg-accent/10 transition-all" aria-label={`Duplicate ${p.name}`} title="Duplicate">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" /></svg>
                </button>
                <button onClick={(e) => { e.stopPropagation(); setDeleteTarget(p.name); }}
                  className="opacity-0 group-hover/party:opacity-100 text-danger/40 hover:text-danger p-0.5 rounded hover:bg-danger/10 transition-all" aria-label={`Delete ${p.name}`} title="Delete">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6L6 18M6 6l12 12" /></svg>
                </button>
              </div>
            </div>
          ))}
          {parties.length === 0 && (
            <div className="flex flex-col items-center py-8 text-center px-4">
              <svg className="w-8 h-8 text-text-secondary/20 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2m8-4a4 4 0 100-8 4 4 0 000 8z" /></svg>
              <p className="text-xs text-text-secondary">No parties loaded</p>
              <p className="text-[10px] text-text-secondary/40 mt-0.5">Click &ldquo;+ Add&rdquo; or &ldquo;Load Examples&rdquo; to get started.</p>
            </div>
          )}
          {parties.length > 0 && filteredParties.length === 0 && search && (
            <p className="p-3 text-xs text-text-secondary/50 text-center">No parties match &ldquo;{search}&rdquo;</p>
          )}
        </div>
        <div className="p-2 border-t border-bg-tertiary text-xs text-text-secondary text-center">
          {search ? `${filteredParties.length} / ${parties.length} parties` : `${parties.length} parties`}
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
