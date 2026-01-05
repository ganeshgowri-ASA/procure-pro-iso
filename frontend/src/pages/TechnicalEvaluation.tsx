import { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Download,
  FileText,
  Award,
  TrendingUp,
} from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Badge, Button, Table, TableHeader, TableBody, TableRow, TableCell } from '../components/ui';
import { technicalEvaluationData } from '../data/sampleData';

export default function TechnicalEvaluation() {
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);
  const { vendors, ctqMatrix } = technicalEvaluationData;

  // Prepare radar chart data
  const radarData = [
    { subject: 'Technical', fullMark: 100 },
    { subject: 'Quality', fullMark: 100 },
    { subject: 'Delivery', fullMark: 100 },
    { subject: 'Compliance', fullMark: 100 },
  ].map((item) => {
    const data: Record<string, number | string> = { ...item };
    vendors.forEach((vendor) => {
      const key = vendor.vendorName.split(' ')[0];
      switch (item.subject) {
        case 'Technical':
          data[key] = vendor.technicalScore;
          break;
        case 'Quality':
          data[key] = vendor.qualityScore;
          break;
        case 'Delivery':
          data[key] = vendor.deliveryScore;
          break;
        case 'Compliance':
          data[key] = vendor.complianceScore;
          break;
      }
    });
    return data;
  });

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 80) return 'bg-blue-50 border-blue-200';
    if (score >= 70) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'Recommended':
        return <Badge variant="success">{rec}</Badge>;
      case 'Acceptable':
        return <Badge variant="info">{rec}</Badge>;
      case 'Not Recommended':
        return <Badge variant="danger">{rec}</Badge>;
      default:
        return <Badge>{rec}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{technicalEvaluationData.rfqTitle}</h2>
          <p className="text-sm text-gray-500">RFQ ID: {technicalEvaluationData.rfqId}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download size={16} className="mr-2" />
            Export Report
          </Button>
          <Button>
            <FileText size={16} className="mr-2" />
            Generate TBE
          </Button>
        </div>
      </div>

      {/* Vendor Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {vendors.map((vendor, index) => (
          <Card
            key={vendor.vendorId}
            className={`relative cursor-pointer transition-all ${
              selectedVendor === vendor.vendorId
                ? 'ring-2 ring-purple-brand'
                : 'hover:shadow-lg'
            }`}
            onClick={() =>
              setSelectedVendor(selectedVendor === vendor.vendorId ? null : vendor.vendorId)
            }
          >
            {index === 0 && (
              <div className="absolute -top-3 -right-3 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg">
                <Award className="text-white" size={16} />
              </div>
            )}
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="font-semibold text-gray-900">{vendor.vendorName}</p>
                <p className="text-sm text-gray-500">Rank #{index + 1}</p>
              </div>
              {getRecommendationBadge(vendor.recommendation)}
            </div>

            <div
              className={`text-center py-6 rounded-lg border ${getScoreBg(vendor.overallScore)} mb-4`}
            >
              <p className={`text-4xl font-bold ${getScoreColor(vendor.overallScore)}`}>
                {vendor.overallScore.toFixed(1)}
              </p>
              <p className="text-sm text-gray-500 mt-1">Overall Score</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-lg font-semibold text-gray-900">{vendor.technicalScore}</p>
                <p className="text-xs text-gray-500">Technical</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-lg font-semibold text-gray-900">{vendor.qualityScore}</p>
                <p className="text-xs text-gray-500">Quality</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-lg font-semibold text-gray-900">{vendor.deliveryScore}</p>
                <p className="text-xs text-gray-500">Delivery</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-lg font-semibold text-gray-900">{vendor.complianceScore}</p>
                <p className="text-xs text-gray-500">Compliance</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Radar Chart */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Comparison</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <Radar
                name={vendors[0].vendorName.split(' ')[0]}
                dataKey={vendors[0].vendorName.split(' ')[0]}
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
              />
              <Radar
                name={vendors[1].vendorName.split(' ')[0]}
                dataKey={vendors[1].vendorName.split(' ')[0]}
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
              <Radar
                name={vendors[2].vendorName.split(' ')[0]}
                dataKey={vendors[2].vendorName.split(' ')[0]}
                stroke="#22c55e"
                fill="#22c55e"
                fillOpacity={0.3}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* CTQ Comparison Matrix */}
      <Card padding="none">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">CTQ Comparison Matrix</h3>
          <p className="text-sm text-gray-500 mt-1">
            Critical to Quality parameters evaluation across all vendors
          </p>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader>Parameter</TableCell>
              <TableCell isHeader className="text-center">Weight</TableCell>
              <TableCell isHeader>Requirement</TableCell>
              {vendors.map((vendor) => (
                <TableCell key={vendor.vendorId} isHeader className="text-center">
                  {vendor.vendorName.split(' ')[0]}
                </TableCell>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {ctqMatrix.map((item) => (
              <TableRow key={item.id}>
                <TableCell>
                  <span className="font-medium text-gray-900">{item.parameter}</span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-sm font-medium">
                    {item.weight}%
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-sm text-gray-600">{item.requirement}</span>
                </TableCell>
                {vendors.map((vendor) => {
                  const vendorData = item.vendors.find((v) => v.vendorId === vendor.vendorId);
                  return (
                    <TableCell key={vendor.vendorId} className="text-center">
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-sm font-medium">{vendorData?.value}</span>
                        <div className="flex items-center gap-1">
                          {vendorData?.compliant ? (
                            <CheckCircle size={14} className="text-green-500" />
                          ) : (
                            <XCircle size={14} className="text-red-500" />
                          )}
                          <span
                            className={`text-xs font-medium ${
                              vendorData?.compliant ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {vendorData?.score}
                          </span>
                        </div>
                      </div>
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Legend */}
      <div className="flex items-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <CheckCircle size={16} className="text-green-500" />
          <span>Compliant</span>
        </div>
        <div className="flex items-center gap-2">
          <XCircle size={16} className="text-red-500" />
          <span>Non-Compliant</span>
        </div>
        <div className="flex items-center gap-2">
          <TrendingUp size={16} className="text-blue-500" />
          <span>Higher score is better</span>
        </div>
      </div>
    </div>
  );
}
