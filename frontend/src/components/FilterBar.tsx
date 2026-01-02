import React from 'react';
import { Search, X, Filter } from 'lucide-react';
import { EquipmentType } from '../types';
import { equipmentTypes } from '../utils/mockData';
import { cn } from '../utils';

interface FilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  equipmentType?: EquipmentType;
  onEquipmentTypeChange: (value: EquipmentType | undefined) => void;
  vendorId?: string;
  vendors?: { id: string; name: string }[];
  onVendorChange?: (value: string | undefined) => void;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  search,
  onSearchChange,
  equipmentType,
  onEquipmentTypeChange,
  vendorId,
  vendors,
  onVendorChange,
  className,
}) => {
  const hasActiveFilters = search || equipmentType || vendorId;

  const clearFilters = () => {
    onSearchChange('');
    onEquipmentTypeChange(undefined);
    onVendorChange?.(undefined);
  };

  return (
    <div className={cn('flex flex-wrap gap-4 items-center', className)}>
      {/* Search input */}
      <div className="relative flex-1 min-w-[200px] max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search equipment, vendor..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Equipment type filter */}
      <div className="relative">
        <select
          value={equipmentType || ''}
          onChange={(e) =>
            onEquipmentTypeChange(e.target.value ? (e.target.value as EquipmentType) : undefined)
          }
          className="input pr-10 appearance-none cursor-pointer min-w-[160px]"
        >
          <option value="">All Equipment</option>
          {equipmentTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <Filter className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>

      {/* Vendor filter */}
      {vendors && vendors.length > 0 && onVendorChange && (
        <div className="relative">
          <select
            value={vendorId || ''}
            onChange={(e) => onVendorChange(e.target.value || undefined)}
            className="input pr-10 appearance-none cursor-pointer min-w-[180px]"
          >
            <option value="">All Vendors</option>
            {vendors.map((vendor) => (
              <option key={vendor.id} value={vendor.id}>
                {vendor.name}
              </option>
            ))}
          </select>
          <Filter className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      )}

      {/* Clear filters button */}
      {hasActiveFilters && (
        <button
          onClick={clearFilters}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-4 h-4" />
          Clear Filters
        </button>
      )}
    </div>
  );
};

export default FilterBar;
