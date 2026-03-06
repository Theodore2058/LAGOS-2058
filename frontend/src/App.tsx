import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Parties from './pages/Parties';
import ParamsPage from './pages/Params';
import Election from './pages/Election';
import Campaign from './pages/Campaign';
import Crises from './pages/Crises';
import Results from './pages/Results';
import MapPage from './pages/Map';
import Scenarios from './pages/Scenarios';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
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
        </main>
      </div>
    </BrowserRouter>
  );
}
