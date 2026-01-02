import React, { useState, useMemo } from 'react';
import { format, parseISO, eachDayOfInterval, startOfMonth, endOfMonth, addMonths, differenceInDays, isSameMonth } from 'date-fns';
import {
  ChevronLeft,
  ChevronRight,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { FilterBar } from '../components';
import { GanttTask, EquipmentType } from '../types';
import { mockGanttTasks, mockVendors } from '../utils/mockData';
import { getEquipmentTypeColor, cn } from '../utils';

type ZoomLevel = 'day' | 'week' | 'month';

export const TimelineView: React.FC = () => {
  const [tasks] = useState<GanttTask[]>(mockGanttTasks);
  const [currentDate, setCurrentDate] = useState(new Date(2024, 1, 1)); // Feb 2024
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>('week');
  const [equipmentType, setEquipmentType] = useState<EquipmentType | undefined>();
  const [vendorId, setVendorId] = useState<string | undefined>();
  const [search, setSearch] = useState('');
  const [selectedTask, setSelectedTask] = useState<GanttTask | null>(null);

  // Generate date range for the view
  const dateRange = useMemo(() => {
    const start = startOfMonth(currentDate);
    const end = endOfMonth(addMonths(currentDate, 2)); // Show 3 months
    return eachDayOfInterval({ start, end });
  }, [currentDate]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    let result = [...tasks];

    if (search) {
      const lowerSearch = search.toLowerCase();
      result = result.filter(
        (task) =>
          task.name.toLowerCase().includes(lowerSearch) ||
          task.vendor.toLowerCase().includes(lowerSearch)
      );
    }

    if (equipmentType) {
      result = result.filter((task) => task.equipment_type === equipmentType);
    }

    if (vendorId) {
      const vendor = mockVendors.find((v) => v.id === vendorId);
      if (vendor) {
        result = result.filter((task) => task.vendor === vendor.company_name);
      }
    }

    return result;
  }, [tasks, search, equipmentType, vendorId]);

  // Calculate bar position and width
  const getBarStyle = (task: GanttTask) => {
    const taskStart = parseISO(task.start_date);
    const taskEnd = parseISO(task.end_date);
    const viewStart = dateRange[0];
    const viewEnd = dateRange[dateRange.length - 1];

    const totalDays = differenceInDays(viewEnd, viewStart) + 1;
    const startOffset = Math.max(0, differenceInDays(taskStart, viewStart));
    const endOffset = Math.min(totalDays, differenceInDays(taskEnd, viewStart) + 1);
    const duration = endOffset - startOffset;

    if (duration <= 0 || startOffset >= totalDays) {
      return { display: 'none' };
    }

    const left = (startOffset / totalDays) * 100;
    const width = (duration / totalDays) * 100;

    return {
      left: `${left}%`,
      width: `${Math.max(width, 1)}%`,
    };
  };

  const getStatusColor = (status: GanttTask['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-blue-500';
      case 'delayed':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const vendors = mockVendors.map((v) => ({ id: v.id, name: v.company_name }));

  // Group dates by month for header
  const monthGroups = useMemo(() => {
    const groups: { month: Date; days: Date[] }[] = [];
    let currentMonth: Date | null = null;
    let currentDays: Date[] = [];

    dateRange.forEach((date) => {
      if (!currentMonth || !isSameMonth(currentMonth, date)) {
        if (currentDays.length > 0) {
          groups.push({ month: currentMonth!, days: currentDays });
        }
        currentMonth = date;
        currentDays = [date];
      } else {
        currentDays.push(date);
      }
    });

    if (currentDays.length > 0 && currentMonth) {
      groups.push({ month: currentMonth, days: currentDays });
    }

    return groups;
  }, [dateRange]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate((prev) => addMonths(prev, direction === 'next' ? 1 : -1));
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Delivery Timeline</h1>
          <p className="text-gray-500 mt-1">
            Gantt-style view of equipment delivery schedules
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
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

      {/* Timeline controls */}
      <div className="card p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Navigation */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="font-medium">
                {format(currentDate, 'MMMM yyyy')} - {format(addMonths(currentDate, 2), 'MMMM yyyy')}
              </span>
            </div>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Zoom controls */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Zoom:</span>
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              {(['day', 'week', 'month'] as ZoomLevel[]).map((level) => (
                <button
                  key={level}
                  onClick={() => setZoomLevel(level)}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium rounded-md transition-all capitalize',
                    zoomLevel === level
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700'
                  )}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400" />
              <span className="text-xs text-gray-500">Pending</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-xs text-gray-500">In Progress</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-xs text-gray-500">Completed</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-xs text-gray-500">Delayed</span>
            </div>
          </div>
        </div>
      </div>

      {/* Gantt Chart */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <div className="min-w-[1200px]">
            {/* Header - Month labels */}
            <div className="flex border-b border-gray-200">
              <div className="w-72 shrink-0 px-4 py-2 bg-gray-50 font-medium text-gray-700 border-r border-gray-200">
                Task
              </div>
              <div className="flex-1 flex">
                {monthGroups.map((group, i) => (
                  <div
                    key={i}
                    className="border-r border-gray-200 text-center py-2 bg-gray-50"
                    style={{ width: `${(group.days.length / dateRange.length) * 100}%` }}
                  >
                    <span className="font-medium text-gray-700">
                      {format(group.month, 'MMMM yyyy')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Header - Day/Week labels */}
            <div className="flex border-b border-gray-200">
              <div className="w-72 shrink-0 px-4 py-1 bg-gray-50 border-r border-gray-200" />
              <div className="flex-1 flex">
                {zoomLevel === 'day' && dateRange.map((date, i) => (
                  <div
                    key={i}
                    className="flex-1 text-center py-1 text-xs text-gray-500 border-r border-gray-100"
                    style={{ minWidth: '30px' }}
                  >
                    {format(date, 'd')}
                  </div>
                ))}
                {zoomLevel === 'week' && monthGroups.map((group, gi) =>
                  group.days
                    .filter((_, i) => i % 7 === 0)
                    .map((date, i) => (
                      <div
                        key={`${gi}-${i}`}
                        className="text-center py-1 text-xs text-gray-500 border-r border-gray-100"
                        style={{ width: `${(7 / dateRange.length) * 100}%` }}
                      >
                        W{Math.ceil((i * 7 + 1) / 7)}
                      </div>
                    ))
                )}
              </div>
            </div>

            {/* Task rows */}
            {filteredTasks.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No tasks match your filters
              </div>
            ) : (
              filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  onClick={() => setSelectedTask(task)}
                >
                  {/* Task info */}
                  <div className="w-72 shrink-0 px-4 py-3 border-r border-gray-200">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'w-3 h-3 rounded-full',
                          getEquipmentTypeColor(task.equipment_type)
                        )}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {task.name}
                        </p>
                        <p className="text-xs text-gray-500">{task.vendor}</p>
                      </div>
                    </div>
                  </div>

                  {/* Gantt bar area */}
                  <div className="flex-1 relative py-2">
                    {/* Grid lines */}
                    <div className="absolute inset-0 flex">
                      {monthGroups.map((group, gi) => (
                        <div
                          key={gi}
                          className="border-r border-gray-100"
                          style={{ width: `${(group.days.length / dateRange.length) * 100}%` }}
                        />
                      ))}
                    </div>

                    {/* Task bar */}
                    <div
                      className={cn(
                        'gantt-bar cursor-pointer',
                        getStatusColor(task.status)
                      )}
                      style={getBarStyle(task)}
                    >
                      {/* Progress indicator */}
                      <div
                        className="absolute inset-y-0 left-0 bg-white/20 rounded-l-md"
                        style={{ width: `${task.progress}%` }}
                      />
                      {/* Label */}
                      <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium truncate px-2">
                        {task.progress}%
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-sm text-gray-500">Total Tasks</p>
          <p className="text-2xl font-bold text-gray-900">{filteredTasks.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">In Progress</p>
          <p className="text-2xl font-bold text-blue-600">
            {filteredTasks.filter((t) => t.status === 'in_progress').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-2xl font-bold text-green-600">
            {filteredTasks.filter((t) => t.status === 'completed').length}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Delayed</p>
          <p className="text-2xl font-bold text-red-600">
            {filteredTasks.filter((t) => t.status === 'delayed').length}
          </p>
        </div>
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-gray-900 bg-opacity-50"
            onClick={() => setSelectedTask(null)}
          />
          <div className="relative bg-white rounded-xl shadow-2xl max-w-lg w-full">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    'w-4 h-4 rounded-full',
                    getEquipmentTypeColor(selectedTask.equipment_type)
                  )}
                />
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {selectedTask.name}
                  </h2>
                  <p className="text-gray-500">{selectedTask.vendor}</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Start Date</p>
                  <p className="font-medium">
                    {format(parseISO(selectedTask.start_date), 'MMM dd, yyyy')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">End Date</p>
                  <p className="font-medium">
                    {format(parseISO(selectedTask.end_date), 'MMM dd, yyyy')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <span
                    className={cn(
                      'badge',
                      selectedTask.status === 'completed'
                        ? 'badge-success'
                        : selectedTask.status === 'in_progress'
                        ? 'badge-info'
                        : selectedTask.status === 'delayed'
                        ? 'badge-danger'
                        : 'badge-neutral'
                    )}
                  >
                    {selectedTask.status.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Progress</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={cn(
                          'h-2 rounded-full',
                          getStatusColor(selectedTask.status)
                        )}
                        style={{ width: `${selectedTask.progress}%` }}
                      />
                    </div>
                    <span className="font-medium">{selectedTask.progress}%</span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Duration</p>
                <p className="font-medium">
                  {differenceInDays(
                    parseISO(selectedTask.end_date),
                    parseISO(selectedTask.start_date)
                  )}{' '}
                  days
                </p>
              </div>
            </div>
            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setSelectedTask(null)}
                className="btn btn-secondary"
              >
                Close
              </button>
              <button className="btn btn-primary">Update Progress</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineView;
