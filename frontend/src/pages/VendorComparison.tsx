import React, { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell,
} from 'recharts';
import { Download, RefreshCw, Check, Star } from 'lucide-react';
import { FilterBar } from '../components';
import { VendorComparison as VendorComparisonType, EquipmentType } from '../types';
import { mockVendorComparisons, mockEquipmentData, mockVendors } from '../utils/mockData';
import { formatCurrency, cn, getTBEScoreColor } from '../utils';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export const VendorComparison: React.FC = () => {
  const [comparisons] = useState<VendorComparisonType[]>(mockVendorComparisons);
  const [selectedVendors, setSelectedVendors] = useState<string[]>(
    mockVendorComparisons.map((v) => v.vendor_id)
  );
  const [equipmentType, setEquipmentType] = useState<EquipmentType | undefined>();
  const [search, setSearch] = useState('');

  // Filter comparisons based on selected vendors
  const filteredComparisons = useMemo(() => {
    return comparisons.filter((c) => selectedVendors.includes(c.vendor_id));
  }, [comparisons, selectedVendors]);

  // Prepare price comparison data for bar chart
  const priceData = useMemo(() => {
    return filteredComparisons.map((c) => ({
      name: c.vendor_name,
      price: c.total_price,
      tbe_score: c.average_tbe_score,
    }));
  }, [filteredComparisons]);

  // Prepare radar chart data
  const radarData = useMemo(() => {
    const categories = ['Technical', 'Delivery', 'Compliance', 'Commercial'];
    return categories.map((category) => {
      const dataPoint: Record<string, unknown> = { category };
      filteredComparisons.forEach((c) => {
        const key = category.toLowerCase() as keyof VendorComparisonType;
        dataPoint[c.vendor_name] = c[`${key}_score` as keyof VendorComparisonType] || 0;
      });
      return dataPoint;
    });
  }, [filteredComparisons]);

  // Toggle vendor selection
  const toggleVendor = (vendorId: string) => {
    setSelectedVendors((prev) =>
      prev.includes(vendorId)
        ? prev.filter((id) => id !== vendorId)
        : [...prev, vendorId]
    );
  };

  const vendors = mockVendors.map((v) => ({ id: v.id, name: v.company_name }));

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vendor Comparison</h1>
          <p className="text-gray-500 mt-1">
            Side-by-side analysis of vendor quotations and TBE scores
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Vendor selection */}
      <div className="card p-4">
        <h3 className="font-semibold text-gray-900 mb-4">Select Vendors to Compare</h3>
        <div className="flex flex-wrap gap-3">
          {comparisons.map((c, index) => (
            <button
              key={c.vendor_id}
              onClick={() => toggleVendor(c.vendor_id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all',
                selectedVendors.includes(c.vendor_id)
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
              )}
            >
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              {c.vendor_name}
              {selectedVendors.includes(c.vendor_id) && (
                <Check className="w-4 h-4" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Filter bar */}
      <div className="card p-4">
        <FilterBar
          search={search}
          onSearchChange={setSearch}
          equipmentType={equipmentType}
          onEquipmentTypeChange={setEquipmentType}
          vendors={vendors}
        />
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Comparison Bar Chart */}
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Price Comparison</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  type="number"
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), 'Price']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="price" radius={[0, 4, 4, 0]}>
                  {priceData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Technical Suitability Radar Chart */}
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Technical Suitability</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="category" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                {filteredComparisons.map((c, index) => (
                  <Radar
                    key={c.vendor_id}
                    name={c.vendor_name}
                    dataKey={c.vendor_name}
                    stroke={COLORS[index % COLORS.length]}
                    fill={COLORS[index % COLORS.length]}
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                ))}
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* TBE Scores Visualization */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4">TBE Scores Overview</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip
                formatter={(value: number) => [value, 'TBE Score']}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="tbe_score" radius={[4, 4, 0, 0]}>
                {priceData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      entry.tbe_score >= 80
                        ? '#22c55e'
                        : entry.tbe_score >= 60
                        ? '#f59e0b'
                        : '#ef4444'
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Comparison Table */}
      <div className="card overflow-hidden">
        <div className="card-header">
          <h3 className="font-semibold text-gray-900">Detailed Comparison</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Criteria
                </th>
                {filteredComparisons.map((c, index) => (
                  <th
                    key={c.vendor_id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      {c.vendor_name}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Total Price
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-bold text-gray-900">
                      {formatCurrency(c.total_price)}
                    </span>
                  </td>
                ))}
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Overall TBE Score
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span
                        className={cn(
                          'text-lg font-bold',
                          getTBEScoreColor(c.average_tbe_score)
                        )}
                      >
                        {c.average_tbe_score}
                      </span>
                      {c.average_tbe_score >= 90 && (
                        <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                      )}
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Technical Score
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-24">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${c.technical_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{c.technical_score}</span>
                    </div>
                  </td>
                ))}
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Delivery Score
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-24">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${c.delivery_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{c.delivery_score}</span>
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Compliance Score
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-24">
                        <div
                          className="bg-purple-500 h-2 rounded-full"
                          style={{ width: `${c.compliance_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{c.compliance_score}</span>
                    </div>
                  </td>
                ))}
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Items Quoted
                </td>
                {filteredComparisons.map((c) => (
                  <td key={c.vendor_id} className="px-6 py-4 whitespace-nowrap">
                    <span className="badge badge-info">{c.items_quoted} items</span>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendation Section */}
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Recommendation</h3>
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Star className="w-6 h-6 text-green-600 fill-green-600" />
            </div>
            <div>
              <h4 className="font-semibold text-green-800 text-lg">
                {filteredComparisons[0]?.vendor_name || 'TA Instruments'} - Recommended
              </h4>
              <p className="text-green-700 mt-1">
                Based on the TBE analysis, this vendor offers the best combination of
                technical capabilities, pricing, and delivery terms. With an overall
                score of {filteredComparisons[0]?.average_tbe_score || 92}, they meet
                all compliance requirements and provide competitive pricing.
              </p>
              <div className="mt-4 flex items-center gap-4">
                <button className="btn btn-success">
                  <Check className="w-4 h-4 mr-2" />
                  Select Vendor
                </button>
                <button className="btn btn-secondary">Request Clarification</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorComparison;
