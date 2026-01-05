import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout';
import {
  Dashboard,
  EquipmentMaster,
  RFQManagement,
  VendorManagement,
  TechnicalEvaluation,
  CommercialEvaluation,
  Settings,
  Help,
} from './pages';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="equipment" element={<EquipmentMaster />} />
        <Route path="rfq" element={<RFQManagement />} />
        <Route path="vendors" element={<VendorManagement />} />
        <Route path="technical-evaluation" element={<TechnicalEvaluation />} />
        <Route path="commercial-evaluation" element={<CommercialEvaluation />} />
        <Route path="settings" element={<Settings />} />
        <Route path="help" element={<Help />} />
      </Route>
    </Routes>
  );
}

export default App;
