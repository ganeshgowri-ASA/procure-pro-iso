import React, { useState, useEffect } from 'react';
import {
  FileText,
  Users,
  ShoppingCart,
  DollarSign,
  TrendingUp,
  Clock,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { StatCard, RFQCard, ActivityFeed } from '../components';
import { DashboardStats, RFQ, ActivityItem } from '../types';
import { dashboardApi, rfqApi } from '../services/api';
import {
  mockDashboardStats,
  mockRFQs,
  mockActivityFeed,
} from '../utils/mockData';
import { formatCurrency } from '../utils';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>(mockDashboardStats);
  const [rfqs, setRfqs] = useState<RFQ[]>(mockRFQs);
  const [activities, setActivities] = useState<ActivityItem[]>(mockActivityFeed);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Try to fetch from API, fall back to mock data
      const [statsRes, rfqsRes] = await Promise.allSettled([
        dashboardApi.getStats(),
        rfqApi.list({ limit: 6 }),
      ]);

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      }
      if (rfqsRes.status === 'fulfilled') {
        setRfqs(rfqsRes.value.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Keep using mock data
    } finally {
      setLoading(false);
    }
  };

  const openRfqs = rfqs.filter((rfq) => rfq.status === 'open');

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procurement Dashboard</h1>
          <p className="text-gray-500 mt-1">
            Overview of RFQs, vendors, and procurement activities
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="btn btn-secondary"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            New RFQ
          </button>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Open RFQs"
          value={stats.open_rfqs}
          icon={FileText}
          color="blue"
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="Approved Vendors"
          value={stats.approved_vendors}
          icon={Users}
          color="green"
          trend={{ value: 5, isPositive: true }}
        />
        <StatCard
          title="Active POs"
          value={stats.active_pos}
          icon={ShoppingCart}
          color="purple"
          trend={{ value: 8, isPositive: true }}
        />
        <StatCard
          title="Total PO Value"
          value={formatCurrency(stats.total_po_value)}
          icon={DollarSign}
          color="orange"
          trend={{ value: 15, isPositive: true }}
        />
      </div>

      {/* Quick stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Recent Quotations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.recent_quotations}</p>
              <p className="text-xs text-gray-400">Last 7 days</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pending Approvals</p>
              <p className="text-2xl font-bold text-gray-900">
                {rfqs.filter((r) => r.status === 'closed').length}
              </p>
              <p className="text-xs text-gray-400">Awaiting TBE</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <FileText className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Active Projects</p>
              <p className="text-2xl font-bold text-gray-900">{stats.active_projects}</p>
              <p className="text-xs text-gray-400">In progress</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* RFQ Cards Section */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Equipment RFQs</h2>
            <a
              href="/equipment"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All
            </a>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="card p-6 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-full mb-4"></div>
                  <div className="h-20 bg-gray-100 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {openRfqs.slice(0, 4).map((rfq) => (
                <RFQCard key={rfq.id} rfq={rfq} />
              ))}
            </div>
          )}

          {/* Additional RFQs list */}
          {rfqs.filter((r) => r.status !== 'open').length > 0 && (
            <div className="card">
              <div className="card-header flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Other RFQs</h3>
                <span className="text-sm text-gray-500">
                  {rfqs.filter((r) => r.status !== 'open').length} items
                </span>
              </div>
              <div className="divide-y divide-gray-100">
                {rfqs
                  .filter((r) => r.status !== 'open')
                  .slice(0, 5)
                  .map((rfq) => (
                    <div
                      key={rfq.id}
                      className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{rfq.title}</p>
                          <p className="text-sm text-gray-500">{rfq.rfq_number}</p>
                        </div>
                        <span
                          className={`badge ${
                            rfq.status === 'awarded'
                              ? 'badge-success'
                              : rfq.status === 'closed'
                              ? 'badge-warning'
                              : 'badge-neutral'
                          }`}
                        >
                          {rfq.status}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        {/* Activity Feed */}
        <div className="lg:col-span-1">
          <ActivityFeed activities={activities} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
