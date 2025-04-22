import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  LineChart,
  FileText,
  Settings,
  TrendingUp,
  LogOut
} from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/analysis', icon: Search, label: 'Analysis' },
  { to: '/insights', icon: LineChart, label: 'Insights' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' }
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <TrendingUp className="h-6 w-6 text-teal-600" />
          <span className="ml-2 text-lg font-semibold text-slate-900">TrendInsights</span>
        </div>
        <nav className="p-4">
          <ul className="space-y-2">
            {navItems.map(({ to, icon: Icon, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-2 rounded-lg transition ${
                      isActive
                        ? 'bg-teal-50 text-teal-600'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`
                  }
                >
                  <Icon className="h-5 w-5" />
                  <span className="ml-3">{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="absolute bottom-0 w-64 p-4 border-t border-slate-200">
          <button className="flex items-center w-full px-4 py-2 text-slate-600 hover:bg-slate-50 rounded-lg transition">
            <LogOut className="h-5 w-5" />
            <span className="ml-3">Log Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
          <h1 className="text-xl font-semibold text-slate-900">
            {navItems.find(item => location.pathname.startsWith(item.to))?.label || 'Dashboard'}
          </h1>
          <div className="flex items-center space-x-4">
            <button className="text-slate-600 hover:text-slate-900">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}