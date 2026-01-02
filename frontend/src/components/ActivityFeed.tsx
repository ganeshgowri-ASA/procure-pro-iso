import React from 'react';
import {
  FileText,
  MessageSquare,
  ShoppingCart,
  UserCheck,
  CheckCircle,
} from 'lucide-react';
import { ActivityItem } from '../types';
import { formatRelativeTime, cn } from '../utils';

interface ActivityFeedProps {
  activities: ActivityItem[];
  className?: string;
}

const activityIcons = {
  rfq_created: FileText,
  quotation_received: MessageSquare,
  po_issued: ShoppingCart,
  vendor_approved: UserCheck,
  tbe_completed: CheckCircle,
};

const activityColors = {
  rfq_created: 'bg-blue-100 text-blue-600',
  quotation_received: 'bg-purple-100 text-purple-600',
  po_issued: 'bg-green-100 text-green-600',
  vendor_approved: 'bg-orange-100 text-orange-600',
  tbe_completed: 'bg-teal-100 text-teal-600',
};

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities, className }) => {
  return (
    <div className={cn('card', className)}>
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {activities.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No recent activity</div>
        ) : (
          activities.map((activity) => {
            const Icon = activityIcons[activity.type];
            const colorClass = activityColors[activity.type];

            return (
              <div
                key={activity.id}
                className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="flex gap-4">
                  <div className={cn('p-2 rounded-lg shrink-0', colorClass)}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <p className="text-sm text-gray-500 truncate">{activity.description}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-400">
                        {formatRelativeTime(activity.timestamp)}
                      </span>
                      {activity.user && (
                        <>
                          <span className="text-gray-300">•</span>
                          <span className="text-xs text-gray-400">{activity.user}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
      <div className="p-4 border-t border-gray-100">
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View all activity
        </button>
      </div>
    </div>
  );
};

export default ActivityFeed;
