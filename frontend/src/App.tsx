import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components';
import { Dashboard, EquipmentAnalysis, VendorComparison, TimelineView } from './pages';

const App: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/equipment" element={<EquipmentAnalysis />} />
        <Route path="/vendors" element={<VendorComparison />} />
        <Route path="/timeline" element={<TimelineView />} />

        {/* Fallback route */}
        <Route
          path="*"
          element={
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
              <p className="text-gray-500 mb-8">Page not found</p>
              <a href="/" className="btn btn-primary">
                Go to Dashboard
              </a>
            </div>
          }
        />
      </Routes>
    </Layout>
  );
};

export default App;
