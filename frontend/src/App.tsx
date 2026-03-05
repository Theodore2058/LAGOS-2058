import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';

function Placeholder({ title }: { title: string }) {
  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <p className="text-text-secondary">Coming soon...</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/parties" element={<Placeholder title="Parties" />} />
            <Route path="/params" element={<Placeholder title="Engine Parameters" />} />
            <Route path="/election" element={<Placeholder title="Static Election" />} />
            <Route path="/campaign" element={<Placeholder title="Campaign" />} />
            <Route path="/crises" element={<Placeholder title="Crises" />} />
            <Route path="/results" element={<Placeholder title="Results" />} />
            <Route path="/map" element={<Placeholder title="Map" />} />
            <Route path="/scenarios" element={<Placeholder title="Scenarios" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
