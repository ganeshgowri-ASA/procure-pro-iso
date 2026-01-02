import React from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  Users,
  FileText,
  ArrowRight,
  Thermometer,
  Scale,
  Box,
  Waves,
  BarChart3,
  Microscope,
  Activity,
  Package,
} from 'lucide-react';
import { RFQ, EquipmentType } from '../types';
import { formatCurrency, formatDate, getStatusColor, cn } from '../utils';

interface RFQCardProps {
  rfq: RFQ;
}

const equipmentIcons: Record<EquipmentType, React.ElementType> = {
  DSC: Thermometer,
  TGA: Scale,
  Chamber: Box,
  Spectrometer: Waves,
  Chromatograph: BarChart3,
  Microscope: Microscope,
  Analyzer: Activity,
  Other: Package,
};

const equipmentColors: Record<EquipmentType, string> = {
  DSC: 'from-blue-500 to-blue-600',
  TGA: 'from-purple-500 to-purple-600',
  Chamber: 'from-green-500 to-green-600',
  Spectrometer: 'from-orange-500 to-orange-600',
  Chromatograph: 'from-pink-500 to-pink-600',
  Microscope: 'from-teal-500 to-teal-600',
  Analyzer: 'from-indigo-500 to-indigo-600',
  Other: 'from-gray-500 to-gray-600',
};

export const RFQCard: React.FC<RFQCardProps> = ({ rfq }) => {
  const equipmentType = rfq.equipment_type || 'Other';
  const Icon = equipmentIcons[equipmentType];
  const gradientColor = equipmentColors[equipmentType];

  return (
    <div className="card overflow-hidden hover:shadow-md transition-shadow duration-200">
      {/* Header with gradient */}
      <div className={cn('h-2 bg-gradient-to-r', gradientColor)} />

      <div className="p-6">
        {/* Equipment type badge and status */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center',
                gradientColor
              )}
            >
              <Icon className="w-5 h-5 text-white" />
            </div>
            <span className="text-sm font-medium text-gray-600">{equipmentType}</span>
          </div>
          <span className={cn('badge', getStatusColor(rfq.status))}>{rfq.status}</span>
        </div>

        {/* Title and RFQ number */}
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{rfq.title}</h3>
        <p className="text-sm text-gray-500 mb-4">{rfq.rfq_number}</p>

        {/* Description */}
        {rfq.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">{rfq.description}</p>
        )}

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 py-4 border-t border-gray-100">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
              <FileText className="w-4 h-4" />
            </div>
            <p className="text-lg font-semibold text-gray-900">{rfq.item_count}</p>
            <p className="text-xs text-gray-500">Items</p>
          </div>
          <div className="text-center border-x border-gray-100">
            <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
              <Users className="w-4 h-4" />
            </div>
            <p className="text-lg font-semibold text-gray-900">{rfq.quotation_count}</p>
            <p className="text-xs text-gray-500">Quotes</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
              <Clock className="w-4 h-4" />
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {rfq.closing_date ? formatDate(rfq.closing_date, 'MMM dd') : 'N/A'}
            </p>
            <p className="text-xs text-gray-500">Closes</p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-500">Estimated Value</p>
            <p className="text-lg font-bold text-gray-900">
              {rfq.estimated_value
                ? formatCurrency(rfq.estimated_value, rfq.currency)
                : 'TBD'}
            </p>
          </div>
          <Link
            to={`/rfq/${rfq.id}`}
            className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm transition-colors"
          >
            View Details
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RFQCard;
