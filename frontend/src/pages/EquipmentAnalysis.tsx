import React, { useState, useMemo } from 'react';
import {
  Download,
  RefreshCw,
  Eye,
  CheckCircle,
  AlertCircle,
  XCircle,
} from 'lucide-react';
import { DataTable, FilterBar } from '../components';
import { EquipmentData, EquipmentType } from '../types';
import { mockEquipmentData, mockVendors } from '../utils/mockData';
import {
  formatCurrency,
  getTBEScoreColor,
  cn,
  sortByKey,
  filterBySearch,
} from '../utils';

export const EquipmentAnalysis: React.FC = () => {
  const [data] = useState<EquipmentData[]>(mockEquipmentData);
  const [search, setSearch] = useState('');
  const [equipmentType, setEquipmentType] = useState<EquipmentType | undefined>();
  const [vendorId, setVendorId] = useState<string | undefined>();
  const [sortKey, setSortKey] = useState<string>('');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [selectedRow, setSelectedRow] = useState<EquipmentData | null>(null);

  // Filter and sort data
  const filteredData = useMemo(() => {
    let result = [...data];

    // Apply search filter
    if (search) {
      result = filterBySearch(result, search, [
        'equipment',
        'vendor',
      ] as (keyof EquipmentData)[]);
    }

    // Apply equipment type filter
    if (equipmentType) {
      result = result.filter((item) => item.equipment_type === equipmentType);
    }

    // Apply vendor filter
    if (vendorId) {
      result = result.filter((item) => item.vendor_id === vendorId);
    }

    // Apply sorting
    if (sortKey) {
      result = sortByKey(result, sortKey as keyof EquipmentData, sortDir);
    }

    return result;
  }, [data, search, equipmentType, vendorId, sortKey, sortDir]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const vendors = mockVendors.map((v) => ({ id: v.id, name: v.company_name }));

  const getComplianceIcon = (status: EquipmentData['compliance_status']) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'partial':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'non-compliant':
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const columns = [
    {
      key: 'equipment',
      header: 'Equipment',
      sortable: true,
      render: (value: unknown, row: EquipmentData) => (
        <div>
          <p className="font-medium text-gray-900">{row.equipment}</p>
          <p className="text-xs text-gray-500">{row.equipment_type}</p>
        </div>
      ),
    },
    {
      key: 'vendor',
      header: 'Vendor',
      sortable: true,
      render: (value: unknown, row: EquipmentData) => (
        <div>
          <p className="font-medium text-gray-900">{row.vendor}</p>
          <p className="text-xs text-gray-500">
            {row.technical_specs.manufacturer}
          </p>
        </div>
      ),
    },
    {
      key: 'technical_specs',
      header: 'Technical Specs',
      render: (value: unknown, row: EquipmentData) => (
        <div className="max-w-xs">
          <p className="text-sm text-gray-900 font-medium">
            {row.technical_specs.model}
          </p>
          <p className="text-xs text-gray-500 truncate">
            {row.technical_specs.specifications[0]}
          </p>
        </div>
      ),
    },
    {
      key: 'price',
      header: 'Price',
      sortable: true,
      render: (value: unknown, row: EquipmentData) => (
        <span className="font-semibold text-gray-900">
          {formatCurrency(row.price, row.currency)}
        </span>
      ),
    },
    {
      key: 'timeline',
      header: 'Timeline',
      render: (value: unknown, row: EquipmentData) => (
        <div>
          <p className="text-sm text-gray-900">
            {row.timeline.lead_time_days} days lead time
          </p>
          <p className="text-xs text-gray-500">
            Delivery: {row.timeline.delivery_date || 'TBD'}
          </p>
        </div>
      ),
    },
    {
      key: 'tbe_score',
      header: 'TBE Score',
      sortable: true,
      render: (value: unknown, row: EquipmentData) => (
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span
                className={cn('font-bold text-lg', getTBEScoreColor(row.tbe_score.overall))}
              >
                {row.tbe_score.overall}
              </span>
              {row.tbe_score.rank && (
                <span className="badge badge-info">#{row.tbe_score.rank}</span>
              )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className={cn(
                  'h-1.5 rounded-full',
                  row.tbe_score.overall >= 80
                    ? 'bg-green-500'
                    : row.tbe_score.overall >= 60
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                )}
                style={{ width: `${row.tbe_score.overall}%` }}
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      key: 'compliance_status',
      header: 'Status',
      render: (value: unknown, row: EquipmentData) => (
        <div className="flex items-center gap-2">
          {getComplianceIcon(row.compliance_status)}
          <span className="text-sm capitalize">{row.compliance_status}</span>
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (_: unknown, row: EquipmentData) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setSelectedRow(row);
          }}
          className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
        >
          <Eye className="w-4 h-4" />
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Equipment Analysis</h1>
          <p className="text-gray-500 mt-1">
            Parsed data from SharePoint Excel files
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync Data
          </button>
          <button className="btn btn-primary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-sm text-gray-500">Total Items</p>
          <p className="text-2xl font-bold text-gray-900">{filteredData.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Avg TBE Score</p>
          <p className="text-2xl font-bold text-green-600">
            {filteredData.length > 0
              ? Math.round(
                  filteredData.reduce((acc, item) => acc + item.tbe_score.overall, 0) /
                    filteredData.length
                )
              : 0}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Total Value</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(
              filteredData.reduce((acc, item) => acc + item.price, 0)
            )}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Compliant</p>
          <p className="text-2xl font-bold text-green-600">
            {filteredData.filter((item) => item.compliance_status === 'compliant').length}
            <span className="text-sm text-gray-500 font-normal ml-1">
              / {filteredData.length}
            </span>
          </p>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card p-4">
        <FilterBar
          search={search}
          onSearchChange={setSearch}
          equipmentType={equipmentType}
          onEquipmentTypeChange={setEquipmentType}
          vendorId={vendorId}
          vendors={vendors}
          onVendorChange={setVendorId}
        />
      </div>

      {/* Data table */}
      <div className="card">
        <DataTable
          data={filteredData}
          columns={columns}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={handleSort}
          onRowClick={(row) => setSelectedRow(row)}
          emptyMessage="No equipment data matches your filters"
        />
      </div>

      {/* Detail modal */}
      {selectedRow && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-gray-900 bg-opacity-50"
            onClick={() => setSelectedRow(null)}
          />
          <div className="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">
                {selectedRow.equipment}
              </h2>
              <p className="text-gray-500">{selectedRow.vendor}</p>
            </div>
            <div className="p-6 space-y-6">
              {/* Technical Specs */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Technical Specifications</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Model</p>
                      <p className="font-medium">{selectedRow.technical_specs.model}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Manufacturer</p>
                      <p className="font-medium">{selectedRow.technical_specs.manufacturer}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Warranty</p>
                      <p className="font-medium">
                        {selectedRow.technical_specs.warranty_months} months
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Specifications</p>
                    <ul className="list-disc list-inside text-sm space-y-1">
                      {selectedRow.technical_specs.specifications.map((spec, i) => (
                        <li key={i}>{spec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* TBE Scores */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">TBE Scores</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {['technical', 'commercial', 'delivery', 'compliance'].map((key) => (
                    <div key={key} className="text-center">
                      <p className="text-sm text-gray-500 capitalize">{key}</p>
                      <p
                        className={cn(
                          'text-2xl font-bold',
                          getTBEScoreColor(
                            selectedRow.tbe_score[key as keyof typeof selectedRow.tbe_score] as number
                          )
                        )}
                      >
                        {selectedRow.tbe_score[key as keyof typeof selectedRow.tbe_score]}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pricing & Timeline */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Pricing</h3>
                  <p className="text-3xl font-bold text-gray-900">
                    {formatCurrency(selectedRow.price, selectedRow.currency)}
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Timeline</h3>
                  <div className="space-y-2 text-sm">
                    <p>Lead Time: {selectedRow.timeline.lead_time_days} days</p>
                    <p>Installation: {selectedRow.timeline.installation_days || 'N/A'} days</p>
                    <p>Training: {selectedRow.timeline.training_days || 'N/A'} days</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setSelectedRow(null)}
                className="btn btn-secondary"
              >
                Close
              </button>
              <button className="btn btn-primary">Generate Report</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EquipmentAnalysis;
