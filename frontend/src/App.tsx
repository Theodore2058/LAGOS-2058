import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import CheatSheet from './components/CheatSheet';

// Lazy-load heavy pages (Recharts, Leaflet) for faster initial load
const Parties = lazy(() => import('./pages/Parties'));
const ParamsPage = lazy(() => import('./pages/Params'));
const Election = lazy(() => import('./pages/Election'));
const Campaign = lazy(() => import('./pages/Campaign'));
const Crises = lazy(() => import('./pages/Crises'));
const Results = lazy(() => import('./pages/Results'));
const MapPage = lazy(() => import('./pages/Map'));
const Scenarios = lazy(() => import('./pages/Scenarios'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-[3px] border-accent/30 border-t-accent rounded-full mx-auto mb-3" />
        <p className="text-sm text-text-secondary">Loading...</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/parties" element={<Parties />} />
              <Route path="/params" element={<ParamsPage />} />
              <Route path="/election" element={<Election />} />
              <Route path="/campaign" element={<Campaign />} />
              <Route path="/crises" element={<Crises />} />
              <Route path="/results" element={<Results />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/scenarios" element={<Scenarios />} />
            </Routes>
          </Suspense>
        </main>
        <CheatSheet />
      </div>
    </BrowserRouter>
  );
}
