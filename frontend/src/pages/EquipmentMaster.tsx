import { useState } from 'react';
import { Search, Filter, Download, Plus, Upload, Eye, Edit2, Trash2 } from 'lucide-react';
import {
  Card,
  Badge,
  Button,
  FileUpload,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
} from '../components/ui';
import { equipmentData } from '../data/sampleData';

export default function EquipmentMaster() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState<string | null>(null);

  const filteredEquipment = equipmentData.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.equipmentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.manufacturer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const categories = [...new Set(equipmentData.map((item) => item.category))];
  const statuses = [...new Set(equipmentData.map((item) => item.status))];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Active':
        return <Badge variant="success">{status}</Badge>;
      case 'Pending':
        return <Badge variant="warning">{status}</Badge>;
      case 'Ordered':
        return <Badge variant="info">{status}</Badge>;
      case 'Delivered':
        return <Badge variant="purple">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getRFQStatusBadge = (status: string) => {
    switch (status) {
      case 'Completed':
        return <Badge variant="success">{status}</Badge>;
      case 'Assigned':
        return <Badge variant="info">{status}</Badge>;
      case 'Pending':
        return <Badge variant="warning">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-1 gap-3">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search equipment..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>

          {/* Category Filter */}
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

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
          >
            <option value="all">All Status</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
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
            Add Equipment
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Equipment</p>
          <p className="text-2xl font-bold text-gray-900">{equipmentData.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Value</p>
          <p className="text-2xl font-bold text-gray-900">
            ${equipmentData.reduce((sum, item) => sum + item.totalPrice, 0).toLocaleString()}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Active Items</p>
          <p className="text-2xl font-bold text-green-600">
            {equipmentData.filter((item) => item.status === 'Active').length}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Pending RFQs</p>
          <p className="text-2xl font-bold text-orange-600">
            {equipmentData.filter((item) => item.rfqStatus === 'Pending').length}
          </p>
        </Card>
      </div>

      {/* Equipment Table */}
      <Card padding="none">
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader>Equipment ID</TableCell>
              <TableCell isHeader>Name / Model</TableCell>
              <TableCell isHeader>Category</TableCell>
              <TableCell isHeader>Manufacturer</TableCell>
              <TableCell isHeader>Qty</TableCell>
              <TableCell isHeader>Total Price</TableCell>
              <TableCell isHeader>Status</TableCell>
              <TableCell isHeader>RFQ Status</TableCell>
              <TableCell isHeader>Documents</TableCell>
              <TableCell isHeader>Actions</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredEquipment.map((item) => (
              <TableRow key={item.id}>
                <TableCell>
                  <span className="font-medium text-purple-brand">{item.equipmentId}</span>
                </TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.model}</p>
                  </div>
                </TableCell>
                <TableCell>{item.category}</TableCell>
                <TableCell>{item.manufacturer}</TableCell>
                <TableCell className="text-center">{item.quantity}</TableCell>
                <TableCell>
                  <span className="font-medium">${item.totalPrice.toLocaleString()}</span>
                </TableCell>
                <TableCell>{getStatusBadge(item.status)}</TableCell>
                <TableCell>{getRFQStatusBadge(item.rfqStatus)}</TableCell>
                <TableCell>
                  <button
                    onClick={() => setShowUploadModal(item.id)}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-purple-brand hover:text-purple-deep border border-purple-brand/30 rounded hover:bg-purple-50 transition-colors"
                  >
                    <Upload size={12} />
                    Upload
                  </button>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <button className="p-1.5 text-gray-400 hover:text-purple-brand transition-colors">
                      <Eye size={16} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors">
                      <Edit2 size={16} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-red-600 transition-colors">
                      <Trash2 size={16} />
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
            Showing {filteredEquipment.length} of {equipmentData.length} items
          </p>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
              Previous
            </button>
            <button className="px-3 py-1.5 text-sm text-white bg-purple-brand rounded hover:opacity-90 transition-opacity">
              1
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
              2
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
              Next
            </button>
          </div>
        </div>
      </Card>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Upload Documents</h3>
              <button
                onClick={() => setShowUploadModal(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <FileUpload
              onFilesChange={(files) => console.log('Files:', files)}
              accept=".pdf,.doc,.docx,.xlsx,.xls"
            />
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setShowUploadModal(null)}>
                Cancel
              </Button>
              <Button onClick={() => setShowUploadModal(null)}>Upload</Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
