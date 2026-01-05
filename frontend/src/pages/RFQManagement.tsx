import { useState } from 'react';
import {
  Search,
  Plus,
  Calendar,
  Users,
  FileText,
  DollarSign,
  Clock,
  Eye,
  Edit2,
  Send,
  ChevronRight,
} from 'lucide-react';
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
import { rfqData } from '../data/sampleData';

export default function RFQManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredRFQs = rfqData.filter((rfq) => {
    const matchesSearch =
      rfq.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rfq.rfqNumber.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || rfq.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Open':
        return <Badge variant="info">{status}</Badge>;
      case 'Closed':
        return <Badge variant="success">{status}</Badge>;
      case 'Draft':
        return <Badge variant="default">{status}</Badge>;
      case 'Awarded':
        return <Badge variant="purple">{status}</Badge>;
      case 'Cancelled':
        return <Badge variant="danger">{status}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return <Badge variant="danger">{priority}</Badge>;
      case 'High':
        return <Badge variant="warning">{priority}</Badge>;
      case 'Normal':
        return <Badge variant="info">{priority}</Badge>;
      case 'Low':
        return <Badge variant="default">{priority}</Badge>;
      default:
        return <Badge>{priority}</Badge>;
    }
  };

  // Calculate stats
  const openRFQs = rfqData.filter((r) => r.status === 'Open').length;
  const totalValue = rfqData.reduce((sum, r) => sum + r.estimatedValue, 0);
  const avgResponseRate = Math.round(
    (rfqData.reduce((sum, r) => sum + (r.vendorsInvited > 0 ? r.responsesReceived / r.vendorsInvited : 0), 0) /
      rfqData.length) * 100
  );

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-blue-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <FileText className="text-blue-500" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{rfqData.length}</p>
              <p className="text-sm text-gray-500">Total RFQs</p>
            </div>
          </div>
        </Card>
        <Card className="p-4 border-l-4 border-l-green-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <Clock className="text-green-500" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{openRFQs}</p>
              <p className="text-sm text-gray-500">Open RFQs</p>
            </div>
          </div>
        </Card>
        <Card className="p-4 border-l-4 border-l-purple-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <DollarSign className="text-purple-500" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">${(totalValue / 1000000).toFixed(2)}M</p>
              <p className="text-sm text-gray-500">Total Value</p>
            </div>
          </div>
        </Card>
        <Card className="p-4 border-l-4 border-l-orange-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-50 rounded-lg">
              <Users className="text-orange-500" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{avgResponseRate}%</p>
              <p className="text-sm text-gray-500">Avg Response Rate</p>
            </div>
          </div>
        </Card>
      </div>

      {/* File Upload Section */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload RFQ Documents</h3>
        <FileUpload
          onFilesChange={(files) => console.log('RFQ Files:', files)}
          accept=".pdf,.doc,.docx,.xlsx,.xls"
        />
      </Card>

      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-1 gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search RFQs..."
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
            <option value="Draft">Draft</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Awarded">Awarded</option>
          </select>
        </div>
        <Button>
          <Plus size={16} className="mr-2" />
          Create RFQ
        </Button>
      </div>

      {/* RFQ Table */}
      <Card padding="none">
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader>RFQ Number</TableCell>
              <TableCell isHeader>Title</TableCell>
              <TableCell isHeader>Priority</TableCell>
              <TableCell isHeader>Issue Date</TableCell>
              <TableCell isHeader>Closing Date</TableCell>
              <TableCell isHeader>Est. Value</TableCell>
              <TableCell isHeader>Vendors</TableCell>
              <TableCell isHeader>Status</TableCell>
              <TableCell isHeader>Actions</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredRFQs.map((rfq) => (
              <TableRow key={rfq.id}>
                <TableCell>
                  <span className="font-medium text-purple-brand">{rfq.rfqNumber}</span>
                </TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium text-gray-900">{rfq.title}</p>
                    <p className="text-xs text-gray-500 truncate max-w-xs">{rfq.description}</p>
                  </div>
                </TableCell>
                <TableCell>{getPriorityBadge(rfq.priority)}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5 text-sm text-gray-600">
                    <Calendar size={14} />
                    {rfq.issueDate}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5 text-sm text-gray-600">
                    <Clock size={14} />
                    {rfq.closingDate}
                  </div>
                </TableCell>
                <TableCell>
                  <span className="font-medium">${rfq.estimatedValue.toLocaleString()}</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5">
                    <Users size={14} className="text-gray-400" />
                    <span className="text-sm">
                      {rfq.responsesReceived}/{rfq.vendorsInvited}
                    </span>
                  </div>
                </TableCell>
                <TableCell>{getStatusBadge(rfq.status)}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <button className="p-1.5 text-gray-400 hover:text-purple-brand transition-colors">
                      <Eye size={16} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors">
                      <Edit2 size={16} />
                    </button>
                    {rfq.status === 'Draft' && (
                      <button className="p-1.5 text-gray-400 hover:text-green-600 transition-colors">
                        <Send size={16} />
                      </button>
                    )}
                    <button className="p-1.5 text-gray-400 hover:text-purple-brand transition-colors">
                      <ChevronRight size={16} />
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
            Showing {filteredRFQs.length} of {rfqData.length} RFQs
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
