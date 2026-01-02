import { format, parseISO, differenceInDays, addDays } from 'date-fns';
import { EquipmentType, RFQStatus } from '../types';

// Format currency
export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

// Format date
export function formatDate(dateString: string | undefined, formatStr = 'MMM dd, yyyy'): string {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), formatStr);
  } catch {
    return dateString;
  }
}

// Format relative time
export function formatRelativeTime(dateString: string): string {
  const date = parseISO(dateString);
  const now = new Date();
  const diffDays = differenceInDays(now, date);

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return formatDate(dateString);
}

// Get status color class
export function getStatusColor(status: RFQStatus | string): string {
  const statusColors: Record<string, string> = {
    draft: 'badge-neutral',
    open: 'badge-info',
    closed: 'badge-warning',
    awarded: 'badge-success',
    cancelled: 'badge-danger',
    pending: 'badge-warning',
    in_progress: 'badge-info',
    completed: 'badge-success',
    approved: 'badge-success',
    rejected: 'badge-danger',
    submitted: 'badge-info',
    under_review: 'badge-warning',
    sent: 'badge-info',
    acknowledged: 'badge-success',
    delayed: 'badge-danger',
  };
  return statusColors[status] || 'badge-neutral';
}

// Get equipment type color
export function getEquipmentTypeColor(type: EquipmentType): string {
  const colors: Record<EquipmentType, string> = {
    DSC: 'bg-blue-500',
    TGA: 'bg-purple-500',
    Chamber: 'bg-green-500',
    Spectrometer: 'bg-orange-500',
    Chromatograph: 'bg-pink-500',
    Microscope: 'bg-teal-500',
    Analyzer: 'bg-indigo-500',
    Other: 'bg-gray-500',
  };
  return colors[type] || 'bg-gray-500';
}

// Get equipment type icon name (for lucide-react)
export function getEquipmentTypeIcon(type: EquipmentType): string {
  const icons: Record<EquipmentType, string> = {
    DSC: 'Thermometer',
    TGA: 'Scale',
    Chamber: 'Box',
    Spectrometer: 'Waves',
    Chromatograph: 'BarChart3',
    Microscope: 'Microscope',
    Analyzer: 'Activity',
    Other: 'Package',
  };
  return icons[type] || 'Package';
}

// Calculate TBE score color
export function getTBEScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

// Calculate progress percentage
export function calculateProgress(current: number, total: number): number {
  if (total === 0) return 0;
  return Math.min(Math.round((current / total) * 100), 100);
}

// Generate Gantt chart date range
export function generateDateRange(startDate: string, endDate: string): Date[] {
  const start = parseISO(startDate);
  const end = parseISO(endDate);
  const dates: Date[] = [];
  let current = start;

  while (current <= end) {
    dates.push(current);
    current = addDays(current, 1);
  }

  return dates;
}

// Calculate position for Gantt chart bar
export function calculateGanttPosition(
  taskStart: string,
  taskEnd: string,
  chartStart: string,
  chartEnd: string
): { left: number; width: number } {
  const chartStartDate = parseISO(chartStart);
  const chartEndDate = parseISO(chartEnd);
  const taskStartDate = parseISO(taskStart);
  const taskEndDate = parseISO(taskEnd);

  const totalDays = differenceInDays(chartEndDate, chartStartDate) + 1;
  const startOffset = differenceInDays(taskStartDate, chartStartDate);
  const taskDuration = differenceInDays(taskEndDate, taskStartDate) + 1;

  return {
    left: (startOffset / totalDays) * 100,
    width: (taskDuration / totalDays) * 100,
  };
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Truncate text
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
}

// Class name merger (similar to clsx but simpler)
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

// Sort function for data tables
export function sortByKey<T>(array: T[], key: keyof T, direction: 'asc' | 'desc'): T[] {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];

    if (aVal === bVal) return 0;
    if (aVal === null || aVal === undefined) return 1;
    if (bVal === null || bVal === undefined) return -1;

    const comparison = aVal < bVal ? -1 : 1;
    return direction === 'asc' ? comparison : -comparison;
  });
}

// Filter array by search term
export function filterBySearch<T extends Record<string, unknown>>(
  array: T[],
  searchTerm: string,
  keys: (keyof T)[]
): T[] {
  if (!searchTerm) return array;
  const lowerSearch = searchTerm.toLowerCase();
  return array.filter((item) =>
    keys.some((key) => {
      const value = item[key];
      return value && String(value).toLowerCase().includes(lowerSearch);
    })
  );
}
