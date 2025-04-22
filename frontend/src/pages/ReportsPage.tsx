import React from 'react';
import {
  FileText,
  Download,
  Share2,
  Copy,
  Calendar,
  Filter,
  Plus
} from 'lucide-react';

const reportTemplates = [
  {
    id: 1,
    name: 'Market Overview',
    description: 'Comprehensive analysis of market trends and competitive landscape',
    type: 'template',
    lastUsed: '2 days ago'
  },
  {
    id: 2,
    name: 'Competitor Analysis',
    description: 'Detailed comparison of competitor strategies and market positioning',
    type: 'template',
    lastUsed: '1 week ago'
  },
  {
    id: 3,
    name: 'Consumer Insights',
    description: 'Deep dive into consumer behavior and sentiment analysis',
    type: 'template',
    lastUsed: '3 days ago'
  }
];

const recentReports = [
  {
    id: 1,
    name: 'Q1 2024 Market Analysis',
    description: 'Quarterly market performance and competitive analysis',
    date: 'Mar 15, 2024',
    status: 'completed'
  },
  {
    id: 2,
    name: 'Competitor Strategy Review',
    description: 'Analysis of key competitor movements and strategies',
    date: 'Mar 10, 2024',
    status: 'in-progress'
  },
  {
    id: 3,
    name: 'Consumer Trends Report',
    description: 'Monthly analysis of consumer behavior and preferences',
    date: 'Mar 5, 2024',
    status: 'completed'
  }
];

function ReportsPage() {
  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition">
            <Plus className="h-4 w-4 mr-2" />
            New Report
          </button>
          <button className="flex items-center px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </button>
        </div>
        <div className="flex items-center space-x-4">
          <button className="flex items-center px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
            <Calendar className="h-4 w-4 mr-2" />
            Schedule
          </button>
          <button className="flex items-center px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </button>
        </div>
      </div>

      {/* Report Templates */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Report Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reportTemplates.map(template => (
            <div
              key={template.id}
              className="p-4 rounded-lg border-2 border-dashed border-slate-200 hover:border-teal-500 transition cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-slate-50 rounded-lg group-hover:bg-teal-50">
                  <FileText className="h-6 w-6 text-slate-400 group-hover:text-teal-600" />
                </div>
                <button className="text-slate-400 hover:text-slate-600">
                  <Copy className="h-5 w-5" />
                </button>
              </div>
              <h3 className="font-medium text-slate-900 mb-1">{template.name}</h3>
              <p className="text-sm text-slate-600 mb-4">{template.description}</p>
              <div className="text-xs text-slate-500">
                Last used {template.lastUsed}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Reports</h2>
        <div className="space-y-4">
          {recentReports.map(report => (
            <div
              key={report.id}
              className="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 transition"
            >
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-white rounded-lg">
                  <FileText className="h-6 w-6 text-teal-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">{report.name}</h3>
                  <p className="text-sm text-slate-600">{report.description}</p>
                  <div className="text-xs text-slate-500 mt-1">{report.date}</div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  report.status === 'completed'
                    ? 'bg-emerald-100 text-emerald-600'
                    : 'bg-yellow-100 text-yellow-600'
                }`}>
                  {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                </span>
                <button className="p-2 text-slate-400 hover:text-slate-600">
                  <Download className="h-5 w-5" />
                </button>
                <button className="p-2 text-slate-400 hover:text-slate-600">
                  <Share2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;