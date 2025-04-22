import React from 'react';
import {
  TrendingUp,
  Users,
  Building2,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const marketData = [
  { name: 'Product A', value: 400 },
  { name: 'Product B', value: 300 },
  { name: 'Product C', value: 200 },
  { name: 'Product D', value: 100 },
];

const sentimentData = [
  { name: 'Positive', value: 60, color: '#059669' },
  { name: 'Neutral', value: 30, color: '#6B7280' },
  { name: 'Negative', value: 10, color: '#DC2626' },
];

function InsightCard({ title, description, impact, trend }: {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  trend: 'up' | 'down';
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          impact === 'high' ? 'bg-red-100 text-red-600' :
          impact === 'medium' ? 'bg-yellow-100 text-yellow-600' :
          'bg-green-100 text-green-600'
        }`}>
          {impact.charAt(0).toUpperCase() + impact.slice(1)} Impact
        </span>
        {trend === 'up' ? (
          <ArrowUpRight className="h-5 w-5 text-emerald-500" />
        ) : (
          <ArrowDownRight className="h-5 w-5 text-red-500" />
        )}
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}

function InsightsPage() {
  return (
    <div className="space-y-6">
      {/* Key Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <InsightCard
          title="Market Share Shift"
          description="Competitor X has gained 5% market share in the APAC region through aggressive pricing strategy."
          impact="high"
          trend="down"
        />
        <InsightCard
          title="Consumer Sentiment"
          description="Positive sentiment around sustainable products has increased by 25% in Q1."
          impact="medium"
          trend="up"
        />
        <InsightCard
          title="Emerging Trend"
          description="New product category showing 200% growth in early adopter segments."
          impact="high"
          trend="up"
        />
      </div>

      {/* Market Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Market Share Distribution</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#0D9488" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Sentiment Analysis</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-xl shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">AI Recommendations</h3>
        <div className="space-y-4">
          {[
            {
              icon: TrendingUp,
              title: 'Expand Market Presence',
              description: 'Consider entering the APAC market with a focused product line to capture emerging demand.',
              priority: 'High'
            },
            {
              icon: Users,
              title: 'Customer Engagement',
              description: 'Implement a customer feedback program to address declining satisfaction scores.',
              priority: 'Medium'
            },
            {
              icon: Building2,
              title: 'Competitive Strategy',
              description: 'Develop premium product offerings to differentiate from competitors\' price-based approach.',
              priority: 'High'
            },
            {
              icon: AlertTriangle,
              title: 'Risk Mitigation',
              description: 'Review supply chain resilience in response to emerging market uncertainties.',
              priority: 'Medium'
            }
          ].map((recommendation, index) => (
            <div key={index} className="flex items-start p-4 rounded-lg bg-slate-50">
              <div className="p-2 bg-teal-50 rounded-lg mr-4">
                <recommendation.icon className="h-6 w-6 text-teal-600" />
              </div>
              <div>
                <div className="flex items-center mb-1">
                  <h4 className="font-medium text-slate-900 mr-2">{recommendation.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    recommendation.priority === 'High'
                      ? 'bg-red-100 text-red-600'
                      : 'bg-yellow-100 text-yellow-600'
                  }`}>
                    {recommendation.priority} Priority
                  </span>
                </div>
                <p className="text-sm text-slate-600">{recommendation.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default InsightsPage;