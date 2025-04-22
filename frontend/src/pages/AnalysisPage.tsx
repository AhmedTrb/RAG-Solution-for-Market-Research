import React, { useState } from 'react';
import { Search, Filter, Download } from 'lucide-react';

const sources = [
  { id: 'social', label: 'Social Media' },
  { id: 'news', label: 'News & PR' },
  { id: 'ecommerce', label: 'E-commerce' },
  { id: 'patents', label: 'Patents' },
  { id: 'reports', label: 'Industry Reports' }
];

const metrics = [
  { id: 'sentiment', label: 'Sentiment Analysis' },
  { id: 'engagement', label: 'Engagement Rate' },
  { id: 'share', label: 'Market Share' },
  { id: 'growth', label: 'Growth Rate' },
  { id: 'pricing', label: 'Pricing Analysis' }
];

function AnalysisPage() {
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);

  const toggleSource = (id: string) => {
    setSelectedSources(prev =>
      prev.includes(id)
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
  };

  const toggleMetric = (id: string) => {
    setSelectedMetrics(prev =>
      prev.includes(id)
        ? prev.filter(m => m !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      {/* Analysis Configuration */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-6">Analysis Configuration</h2>
        
        {/* Search Input */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Enter competitors, markets, or keywords to analyze..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>

        {/* Data Sources */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-slate-700 mb-3">Data Sources</h3>
          <div className="flex flex-wrap gap-2">
            {sources.map(source => (
              <button
                key={source.id}
                onClick={() => toggleSource(source.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  selectedSources.includes(source.id)
                    ? 'bg-teal-50 text-teal-600 border-2 border-teal-200'
                    : 'bg-slate-50 text-slate-600 border-2 border-transparent hover:bg-slate-100'
                }`}
              >
                {source.label}
              </button>
            ))}
          </div>
        </div>

        {/* Metrics */}
        <div>
          <h3 className="text-sm font-medium text-slate-700 mb-3">Analysis Metrics</h3>
          <div className="flex flex-wrap gap-2">
            {metrics.map(metric => (
              <button
                key={metric.id}
                onClick={() => toggleMetric(metric.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  selectedMetrics.includes(metric.id)
                    ? 'bg-teal-50 text-teal-600 border-2 border-teal-200'
                    : 'bg-slate-50 text-slate-600 border-2 border-transparent hover:bg-slate-100'
                }`}
              >
                {metric.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Analysis Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="flex items-center px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
            <Filter className="h-4 w-4 mr-2" />
            Advanced Filters
          </button>
          <button className="flex items-center px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </button>
        </div>
        <button className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition">
          Run Analysis
        </button>
      </div>

      {/* Analysis Preview */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="text-center py-12">
          <div className="mb-4">
            <Search className="h-12 w-12 text-slate-300 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-slate-900 mb-2">Configure Your Analysis</h3>
          <p className="text-slate-600 max-w-md mx-auto">
            Select your data sources and metrics above to begin analyzing market trends and competitor insights.
          </p>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPage;