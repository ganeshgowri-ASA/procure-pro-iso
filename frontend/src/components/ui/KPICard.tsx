import {
  Package,
  DollarSign,
  FileText,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import clsx from 'clsx';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  color: 'blue' | 'green' | 'orange' | 'purple';
  icon: string;
}

const iconMap = {
  Package,
  DollarSign,
  FileText,
  Clock,
};

const colorClasses = {
  blue: {
    border: 'border-l-kpi-blue',
    bg: 'bg-blue-50',
    icon: 'text-kpi-blue',
    trend: 'text-kpi-blue',
  },
  green: {
    border: 'border-l-kpi-green',
    bg: 'bg-green-50',
    icon: 'text-kpi-green',
    trend: 'text-kpi-green',
  },
  orange: {
    border: 'border-l-kpi-orange',
    bg: 'bg-orange-50',
    icon: 'text-kpi-orange',
    trend: 'text-kpi-orange',
  },
  purple: {
    border: 'border-l-kpi-purple',
    bg: 'bg-purple-50',
    icon: 'text-kpi-purple',
    trend: 'text-kpi-purple',
  },
};

export default function KPICard({ title, value, change, trend, color, icon }: KPICardProps) {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || Package;
  const colors = colorClasses[color];

  return (
    <div
      className={clsx(
        'bg-white rounded-lg shadow-card p-5 border-l-4 transition-all duration-200 hover:shadow-card-hover',
        colors.border
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <div className="flex items-center mt-2 gap-1">
              {trend === 'up' ? (
                <TrendingUp size={14} className="text-green-500" />
              ) : trend === 'down' ? (
                <TrendingDown size={14} className="text-red-500" />
              ) : null}
              <span
                className={clsx(
                  'text-xs font-medium',
                  trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500'
                )}
              >
                {trend === 'up' ? '+' : trend === 'down' ? '' : ''}{change}% from last month
              </span>
            </div>
          )}
        </div>
        <div className={clsx('p-3 rounded-lg', colors.bg)}>
          <IconComponent size={24} className={colors.icon} />
        </div>
      </div>
    </div>
  );
}
