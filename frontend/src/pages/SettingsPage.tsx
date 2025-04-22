import React from 'react';
import {
  User,
  Bell,
  Lock,
  Globe,
  Database,
  Sliders,
  CreditCard
} from 'lucide-react';

const settingsSections = [
  {
    id: 'profile',
    icon: User,
    title: 'Profile Settings',
    description: 'Manage your account information and preferences'
  },
  {
    id: 'notifications',
    icon: Bell,
    title: 'Notifications',
    description: 'Configure how and when you receive alerts'
  },
  {
    id: 'security',
    icon: Lock,
    title: 'Security',
    description: 'Protect your account and data'
  },
  {
    id: 'integrations',
    icon: Globe,
    title: 'Integrations',
    description: 'Connect with external tools and services'
  },
  {
    id: 'data',
    icon: Database,
    title: 'Data Management',
    description: 'Control your data sources and storage'
  },
  {
    id: 'preferences',
    icon: Sliders,
    title: 'Analysis Preferences',
    description: 'Customize your analysis settings'
  },
  {
    id: 'billing',
    icon: CreditCard,
    title: 'Billing & Subscription',
    description: 'Manage your subscription and payment methods'
  }
];

function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Settings Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
            <User className="h-8 w-8 text-slate-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">John Doe</h2>
            <p className="text-slate-600">john.doe@company.com</p>
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="bg-white rounded-xl shadow-sm divide-y divide-slate-100">
        {settingsSections.map(section => (
          <div
            key={section.id}
            className="p-6 hover:bg-slate-50 transition cursor-pointer"
          >
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-slate-100 rounded-lg">
                <section.icon className="h-6 w-6 text-slate-600" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-slate-900">{section.title}</h3>
                  <button className="text-sm text-teal-600 hover:text-teal-700">
                    Edit
                  </button>
                </div>
                <p className="text-slate-600 mt-1">{section.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Danger Zone */}
      <div className="bg-red-50 rounded-xl p-6">
        <h3 className="text-lg font-medium text-red-800 mb-2">Danger Zone</h3>
        <p className="text-red-600 mb-4">
          Actions here can't be undone. Please proceed with caution.
        </p>
        <div className="space-y-3">
          <button className="w-full px-4 py-2 bg-white text-red-600 rounded-lg border border-red-200 hover:bg-red-50 transition">
            Delete All Data
          </button>
          <button className="w-full px-4 py-2 bg-white text-red-600 rounded-lg border border-red-200 hover:bg-red-50 transition">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;