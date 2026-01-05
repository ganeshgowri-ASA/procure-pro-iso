import { useState } from 'react';
import {
  Download,
  Calculator,
  DollarSign,
  Truck,
  Shield,
  Clock,
  TrendingDown,
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
  ComposedChart,
  Line,
} from 'recharts';
import { Card, Badge, Button, Table, TableHeader, TableBody, TableRow, TableCell } from '../components/ui';
import { commercialEvaluationData } from '../data/sampleData';

export default function CommercialEvaluation() {
  const [selectedMetric, setSelectedMetric] = useState('total');
  const { vendors, tcoComparison } = commercialEvaluationData;

  // Prepare TCO chart data
  const tcoChartData = tcoComparison.map((item) => {
    const data: Record<string, number | string> = { category: item.category };
    item.vendors.forEach((v) => {
      const vendor = vendors.find((vendor) => vendor.vendorId === v.vendorId);
      if (vendor) {
        data[vendor.vendorName.split(' ')[0]] = v.amount;
      }
    });
    return data;
  });

  // Calculate TCO totals
  const tcoTotals = vendors.map((vendor) => {
    const total = tcoComparison.reduce((sum, item) => {
      const vendorData = item.vendors.find((v) => v.vendorId === vendor.vendorId);
      return sum + (vendorData?.amount || 0);
    }, 0);
    return { vendorId: vendor.vendorId, vendorName: vendor.vendorName, total };
  });

  // Find lowest TCO
  const lowestTCO = Math.min(...tcoTotals.map((t) => t.total));

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    }
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{commercialEvaluationData.rfqTitle}</h2>
          <p className="text-sm text-gray-500">Commercial Bid Evaluation</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download size={16} className="mr-2" />
            Export Report
          </Button>
          <Button>
            <Calculator size={16} className="mr-2" />
            Recalculate TCO
          </Button>
        </div>
      </div>

      {/* Price Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {vendors.map((vendor, index) => {
          const tcoTotal = tcoTotals.find((t) => t.vendorId === vendor.vendorId)?.total || 0;
          const isLowest = tcoTotal === lowestTCO;

          return (
            <Card
              key={vendor.vendorId}
              className={`relative ${isLowest ? 'ring-2 ring-green-500' : ''}`}
            >
              {isLowest && (
                <div className="absolute -top-3 -right-3 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
                  <Award className="text-white" size={16} />
                </div>
              )}

              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-900">{vendor.vendorName}</p>
                  {isLowest && (
                    <Badge variant="success" size="sm">
                      Lowest TCO
                    </Badge>
                  )}
                </div>
              </div>

              {/* Main Price */}
              <div className="text-center py-4 bg-gray-50 rounded-lg mb-4">
                <p className="text-3xl font-bold text-gray-900">
                  {formatCurrency(vendor.total)}
                </p>
                <p className="text-sm text-gray-500">Initial Quote</p>
              </div>

              {/* Price Breakdown */}
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Unit Price</span>
                  <span className="font-medium">${vendor.unitPrice.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Quantity</span>
                  <span className="font-medium">{vendor.quantity} units</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Discount</span>
                  <span className="font-medium text-green-600">-{vendor.discount}%</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Tax</span>
                  <span className="font-medium">{vendor.tax}%</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Shipping</span>
                  <span className="font-medium">${vendor.shipping.toLocaleString()}</span>
                </div>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <Clock size={16} className="mx-auto text-gray-400 mb-1" />
                  <p className="text-sm font-medium">{vendor.deliveryDays}d</p>
                  <p className="text-xs text-gray-500">Delivery</p>
                </div>
                <div className="text-center">
                  <DollarSign size={16} className="mx-auto text-gray-400 mb-1" />
                  <p className="text-sm font-medium">{vendor.paymentTerms}</p>
                  <p className="text-xs text-gray-500">Terms</p>
                </div>
                <div className="text-center">
                  <Shield size={16} className="mx-auto text-gray-400 mb-1" />
                  <p className="text-sm font-medium">{vendor.warranty}</p>
                  <p className="text-xs text-gray-500">Warranty</p>
                </div>
              </div>

              {/* TCO Total */}
              <div className="mt-4 p-3 bg-purple-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-purple-700">5-Year TCO</span>
                  <span className="text-lg font-bold text-purple-900">
                    {formatCurrency(tcoTotal)}
                  </span>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* TCO Comparison Chart */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Total Cost of Ownership Breakdown</h3>
          <div className="flex items-center gap-2">
            <TrendingDown size={18} className="text-green-500" />
            <span className="text-sm text-gray-600">Lower is better</span>
          </div>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tcoChartData} layout="vertical" barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={true} vertical={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <YAxis
                type="category"
                dataKey="category"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                width={120}
              />
              <Tooltip
                formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Bar
                dataKey={vendors[0].vendorName.split(' ')[0]}
                fill="#8b5cf6"
                radius={[0, 4, 4, 0]}
              />
              <Bar
                dataKey={vendors[1].vendorName.split(' ')[0]}
                fill="#3b82f6"
                radius={[0, 4, 4, 0]}
              />
              <Bar
                dataKey={vendors[2].vendorName.split(' ')[0]}
                fill="#22c55e"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Detailed Price Comparison Table */}
      <Card padding="none">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Detailed Price Comparison</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader>Component</TableCell>
              {vendors.map((vendor) => (
                <TableCell key={vendor.vendorId} isHeader className="text-right">
                  {vendor.vendorName}
                </TableCell>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {tcoComparison.map((item) => (
              <TableRow key={item.category}>
                <TableCell>
                  <span className="font-medium text-gray-900">{item.category}</span>
                </TableCell>
                {vendors.map((vendor) => {
                  const vendorData = item.vendors.find((v) => v.vendorId === vendor.vendorId);
                  const amount = vendorData?.amount || 0;
                  const minAmount = Math.min(...item.vendors.map((v) => v.amount));
                  const isLowest = amount === minAmount && amount > 0;

                  return (
                    <TableCell key={vendor.vendorId} className="text-right">
                      <span
                        className={`font-medium ${
                          isLowest ? 'text-green-600' : 'text-gray-900'
                        }`}
                      >
                        ${amount.toLocaleString()}
                        {isLowest && amount > 0 && (
                          <span className="ml-1 text-xs text-green-500">✓</span>
                        )}
                      </span>
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
            <TableRow className="bg-gray-50 font-semibold">
              <TableCell>
                <span className="font-bold text-gray-900">5-Year TCO Total</span>
              </TableCell>
              {tcoTotals.map((tco) => {
                const isLowest = tco.total === lowestTCO;
                return (
                  <TableCell key={tco.vendorId} className="text-right">
                    <span
                      className={`text-lg font-bold ${
                        isLowest ? 'text-green-600' : 'text-gray-900'
                      }`}
                    >
                      {formatCurrency(tco.total)}
                    </span>
                  </TableCell>
                );
              })}
            </TableRow>
          </TableBody>
        </Table>
      </Card>

      {/* TCO Calculator */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">TCO Calculator Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Period (Years)
            </label>
            <input
              type="number"
              defaultValue={5}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Discount Rate (%)
            </label>
            <input
              type="number"
              defaultValue={8}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Annual Maintenance (%)
            </label>
            <input
              type="number"
              defaultValue={5}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button>
            <Calculator size={16} className="mr-2" />
            Recalculate
          </Button>
        </div>
      </Card>

      {/* Summary */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-none">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white rounded-lg shadow-sm">
            <Award className="text-purple-brand" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recommendation</h3>
            <p className="text-gray-600 mt-1">
              Based on the comprehensive TCO analysis, <strong>{tcoTotals.find((t) => t.total === lowestTCO)?.vendorName}</strong>{' '}
              offers the best value with a 5-year TCO of{' '}
              <strong>{formatCurrency(lowestTCO)}</strong>. This includes the lowest combined cost
              for initial purchase, installation, training, and ongoing maintenance.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
