import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const pageTitles: Record<string, { title: string; subtitle?: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Overview of procurement activities' },
  '/equipment': { title: 'Equipment Master List', subtitle: 'Manage equipment inventory' },
  '/rfq': { title: 'RFQ Management', subtitle: 'Request for quotations' },
  '/vendors': { title: 'Vendor Management', subtitle: 'Supplier directory & performance' },
  '/technical-evaluation': { title: 'Technical Evaluation', subtitle: 'TBE analysis & scoring' },
  '/commercial-evaluation': { title: 'Commercial Evaluation', subtitle: 'Pricing & TCO analysis' },
  '/settings': { title: 'Settings', subtitle: 'System configuration' },
  '/help': { title: 'Help & Support', subtitle: 'Documentation & assistance' },
};

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: 'Procure-Pro-ISO' };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onMenuClick={() => setSidebarOpen(true)}
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
        />

        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
