import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { FileText, Clock, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';
import { Card, KPICard, Badge } from '../components/ui';
import {
  dashboardKPIs,
  budgetTrendData,
  rfqStatusData,
  categoryData,
  recentActivity,
  rfqData,
} from '../data/sampleData';

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {dashboardKPIs.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Budget Trend Chart */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Budget vs Spending</h3>
            <select className="text-sm border border-gray-200 rounded-lg px-3 py-1.5">
              <option>Last 6 months</option>
              <option>Last 12 months</option>
              <option>This year</option>
            </select>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={budgetTrendData}>
                <defs>
                  <linearGradient id="colorBudget" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorSpent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#6b7280' }} />
                <YAxis
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                />
                <Tooltip
                  formatter={(value: number) => `$${value.toLocaleString()}`}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="budget"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  fill="url(#colorBudget)"
                  name="Budget"
                />
                <Area
                  type="monotone"
                  dataKey="spent"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#colorSpent)"
                  name="Spent"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* RFQ Status Pie Chart */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">RFQ Status Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={rfqStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {rfqStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value) => (
                    <span className="text-sm text-gray-600">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent RFQs */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Active RFQs</h3>
            <button className="text-sm text-purple-brand hover:text-purple-deep flex items-center gap-1">
              View all <ArrowRight size={14} />
            </button>
          </div>
          <div className="space-y-3">
            {rfqData.slice(0, 4).map((rfq) => (
              <div
                key={rfq.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <FileText className="text-purple-brand" size={20} />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{rfq.rfqNumber}</p>
                    <p className="text-sm text-gray-500">{rfq.title}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      ${rfq.estimatedValue.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {rfq.responsesReceived}/{rfq.vendorsInvited} responses
                    </p>
                  </div>
                  <Badge
                    variant={
                      rfq.status === 'Open'
                        ? 'info'
                        : rfq.status === 'Closed'
                        ? 'success'
                        : rfq.status === 'Awarded'
                        ? 'purple'
                        : 'default'
                    }
                  >
                    {rfq.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Activity */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3">
                <div
                  className={`p-2 rounded-full ${
                    activity.type === 'rfq'
                      ? 'bg-blue-100 text-blue-600'
                      : activity.type === 'approval'
                      ? 'bg-green-100 text-green-600'
                      : activity.type === 'vendor'
                      ? 'bg-purple-100 text-purple-600'
                      : activity.type === 'equipment'
                      ? 'bg-orange-100 text-orange-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {activity.type === 'rfq' && <FileText size={16} />}
                  {activity.type === 'approval' && <CheckCircle2 size={16} />}
                  {activity.type === 'vendor' && <AlertCircle size={16} />}
                  {activity.type === 'equipment' && <Clock size={16} />}
                  {activity.type === 'evaluation' && <CheckCircle2 size={16} />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700">{activity.message}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Category Distribution */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Equipment by Category</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {categoryData.map((category, index) => (
            <div
              key={index}
              className="p-4 rounded-lg border border-gray-200 hover:border-purple-brand/30 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-600">{category.name}</span>
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: category.color }}
                />
              </div>
              <p className="text-2xl font-bold text-gray-900">{category.value}</p>
              <p className="text-xs text-gray-500">items in category</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
