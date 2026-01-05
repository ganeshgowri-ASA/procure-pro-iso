import { Settings as SettingsIcon, User, Bell, Shield, Database, Globe } from 'lucide-react';
import { Card, Button } from '../components/ui';

export default function Settings() {
  const settingSections = [
    {
      icon: User,
      title: 'Profile Settings',
      description: 'Manage your account information and preferences',
      color: 'text-blue-500',
      bg: 'bg-blue-50',
    },
    {
      icon: Bell,
      title: 'Notifications',
      description: 'Configure email and in-app notification preferences',
      color: 'text-orange-500',
      bg: 'bg-orange-50',
    },
    {
      icon: Shield,
      title: 'Security',
      description: 'Password, two-factor authentication, and access logs',
      color: 'text-green-500',
      bg: 'bg-green-50',
    },
    {
      icon: Database,
      title: 'Data Management',
      description: 'Export data, backup settings, and data retention',
      color: 'text-purple-500',
      bg: 'bg-purple-50',
    },
    {
      icon: Globe,
      title: 'System Preferences',
      description: 'Language, timezone, and regional settings',
      color: 'text-indigo-500',
      bg: 'bg-indigo-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-50 rounded-lg">
          <SettingsIcon className="text-purple-brand" size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">System Settings</h2>
          <p className="text-sm text-gray-500">Manage your application preferences</p>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {settingSections.map((section, index) => (
          <Card
            key={index}
            className="cursor-pointer hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-lg ${section.bg}`}>
                <section.icon className={section.color} size={24} />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{section.title}</h3>
                <p className="text-sm text-gray-500 mt-1">{section.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Settings */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div>
              <p className="font-medium text-gray-900">Dark Mode</p>
              <p className="text-sm text-gray-500">Enable dark theme for the interface</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-brand rounded-full peer peer-checked:bg-purple-brand after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div>
              <p className="font-medium text-gray-900">Email Notifications</p>
              <p className="text-sm text-gray-500">Receive updates via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-brand rounded-full peer peer-checked:bg-purple-brand after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">Auto-save Drafts</p>
              <p className="text-sm text-gray-500">Automatically save form drafts</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-brand rounded-full peer peer-checked:bg-purple-brand after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button variant="outline">Reset to Defaults</Button>
        <Button>Save Changes</Button>
      </div>
    </div>
  );
}
