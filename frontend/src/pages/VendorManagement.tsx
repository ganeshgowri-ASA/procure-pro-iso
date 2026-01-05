import { useState } from 'react';
import {
  Search,
  Plus,
  Filter,
  Download,
  Eye,
  Edit2,
  Mail,
  Phone,
  MapPin,
  Award,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  Card,
  Badge,
  Button,
  StarRating,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
} from '../components/ui';
import { vendorData, vendorPerformanceData } from '../data/sampleData';

export default function VendorManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const filteredVendors = vendorData.filter((vendor) => {
    const matchesSearch =
      vendor.companyName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.vendorCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.contactPerson.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || vendor.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || vendor.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const categories = [...new Set(vendorData.map((v) => v.category))];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Approved':
        return <Badge variant="success">{status}</Badge>;
      case 'Pending':
        return <Badge variant="warning">{status}</Badge>;
      case 'Blacklisted':
        return <Badge variant="danger">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  // Stats
  const approvedVendors = vendorData.filter((v) => v.status === 'Approved').length;
  const avgRating = (
    vendorData.reduce((sum, v) => sum + v.rating, 0) / vendorData.filter((v) => v.rating > 0).length
  ).toFixed(1);
  const totalValue = vendorData.reduce((sum, v) => sum + v.totalValue, 0);

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-blue-500">
          <p className="text-sm text-gray-500">Total Vendors</p>
          <p className="text-2xl font-bold text-gray-900">{vendorData.length}</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-green-500">
          <p className="text-sm text-gray-500">Approved Vendors</p>
          <p className="text-2xl font-bold text-green-600">{approvedVendors}</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-yellow-500">
          <p className="text-sm text-gray-500">Average Rating</p>
          <p className="text-2xl font-bold text-gray-900">{avgRating} / 5.0</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-purple-500">
          <p className="text-sm text-gray-500">Total Order Value</p>
          <p className="text-2xl font-bold text-gray-900">${(totalValue / 1000000).toFixed(1)}M</p>
        </Card>
      </div>

      {/* Performance Chart */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Vendor Performance Overview</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={vendorPerformanceData} barGap={8}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Bar dataKey="onTime" name="On-Time Delivery %" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="quality" name="Quality Score %" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-1 gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search vendors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
          >
            <option value="all">All Status</option>
            <option value="Approved">Approved</option>
            <option value="Pending">Pending</option>
            <option value="Blacklisted">Blacklisted</option>
          </select>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
          >
            <option value="all">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download size={16} className="mr-2" />
            Export
          </Button>
          <Button>
            <Plus size={16} className="mr-2" />
            Add Vendor
          </Button>
        </div>
      </div>

      {/* Vendor Table */}
      <Card padding="none">
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader>Vendor</TableCell>
              <TableCell isHeader>Contact</TableCell>
              <TableCell isHeader>Category</TableCell>
              <TableCell isHeader>Rating</TableCell>
              <TableCell isHeader>Orders</TableCell>
              <TableCell isHeader>On-Time %</TableCell>
              <TableCell isHeader>Quality %</TableCell>
              <TableCell isHeader>Certifications</TableCell>
              <TableCell isHeader>Status</TableCell>
              <TableCell isHeader>Actions</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredVendors.map((vendor) => (
              <TableRow key={vendor.id}>
                <TableCell>
                  <div>
                    <p className="font-medium text-gray-900">{vendor.companyName}</p>
                    <p className="text-xs text-gray-500">{vendor.vendorCode}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-900">{vendor.contactPerson}</p>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Mail size={10} />
                      {vendor.email}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <MapPin size={10} />
                      {vendor.country}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{vendor.category}</span>
                </TableCell>
                <TableCell>
                  {vendor.rating > 0 ? (
                    <StarRating rating={vendor.rating} size="sm" />
                  ) : (
                    <span className="text-xs text-gray-400">N/A</span>
                  )}
                </TableCell>
                <TableCell>
                  <span className="font-medium">{vendor.totalOrders}</span>
                </TableCell>
                <TableCell>
                  {vendor.onTimeDelivery > 0 ? (
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${vendor.onTimeDelivery}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{vendor.onTimeDelivery}%</span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">N/A</span>
                  )}
                </TableCell>
                <TableCell>
                  {vendor.qualityScore > 0 ? (
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 rounded-full"
                          style={{ width: `${vendor.qualityScore}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{vendor.qualityScore}%</span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">N/A</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {vendor.certifications.length > 0 ? (
                      vendor.certifications.slice(0, 2).map((cert, i) => (
                        <span
                          key={i}
                          className="px-1.5 py-0.5 text-xs bg-blue-50 text-blue-700 rounded"
                        >
                          {cert}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-gray-400">None</span>
                    )}
                    {vendor.certifications.length > 2 && (
                      <span className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                        +{vendor.certifications.length - 2}
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell>{getStatusBadge(vendor.status)}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <button className="p-1.5 text-gray-400 hover:text-purple-brand transition-colors">
                      <Eye size={16} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors">
                      <Edit2 size={16} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-green-600 transition-colors">
                      <Award size={16} />
                    </button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Showing {filteredVendors.length} of {vendorData.length} vendors
          </p>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
              Previous
            </button>
            <button className="px-3 py-1.5 text-sm text-white bg-purple-brand rounded hover:opacity-90 transition-opacity">
              1
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
              Next
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
