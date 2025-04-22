import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  TrendingUp,
  Users,
  BarChart2,
  ArrowRight,
  Building2,
  LineChart,
  Globe2,
  Zap
} from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-teal-600" />
              <span className="ml-2 text-xl font-bold text-slate-800">TrendInsights</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-slate-600 hover:text-slate-900">Features</a>
              <a href="#solutions" className="text-slate-600 hover:text-slate-900">Solutions</a>
              <a href="#pricing" className="text-slate-600 hover:text-slate-900">Pricing</a>
              <button 
                onClick={() => navigate('/dashboard')}
                className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6">
              AI-Powered Market Research & Analysis
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
              Uncover market trends, analyze competitors, and identify consumer insights with our comprehensive AI-driven platform.
            </p>
            <div className="max-w-2xl mx-auto mb-12">
              <div className="relative">
                <Search className="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search market trends, competitors, or industries..."
                  className="w-full pl-12 pr-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <button 
                onClick={() => navigate('/dashboard')}
                className="flex items-center bg-slate-800 text-white px-6 py-3 rounded-lg hover:bg-slate-700 transition"
              >
                Start Analysis
                <ArrowRight className="ml-2 h-4 w-4" />
              </button>
              <button className="flex items-center bg-white text-slate-800 px-6 py-3 rounded-lg border border-slate-200 hover:border-slate-300 transition">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white border-y border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 mb-2">10M+</div>
              <div className="text-slate-600">Analyzed Posts</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 mb-2">500+</div>
              <div className="text-slate-600">Brands Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900 mb-2">98%</div>
              <div className="text-slate-600">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Powerful Features for Market Leaders</h2>
            <p className="text-lg text-slate-600">Everything you need to stay ahead of the competition</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Globe2 className="h-6 w-6 text-teal-600" />}
              title="Market Pulse Monitor"
              description="Track real-time market trends and receive instant alerts on significant changes."
            />
            <FeatureCard
              icon={<Building2 className="h-6 w-6 text-teal-600" />}
              title="Competitor Observatory"
              description="Analyze competitor strategies, pricing, and market positioning."
            />
            <FeatureCard
              icon={<Users className="h-6 w-6 text-teal-600" />}
              title="Consumer Insights"
              description="Understand customer behavior and sentiment across demographics."
            />
            <FeatureCard
              icon={<LineChart className="h-6 w-6 text-teal-600" />}
              title="Trend Analysis"
              description="Identify emerging trends and predict market movements."
            />
            <FeatureCard
              icon={<BarChart2 className="h-6 w-6 text-teal-600" />}
              title="Visual Analytics"
              description="Generate beautiful, interactive visualizations of market data."
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6 text-teal-600" />}
              title="AI Recommendations"
              description="Get actionable insights powered by advanced AI algorithms."
            />
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm font-semibold text-slate-600 uppercase tracking-wide mb-8">
            Trusted by leading companies worldwide
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center opacity-60">
            {['Microsoft', 'Adobe', 'Salesforce', 'Oracle', 'IBM', 'SAP'].map((company) => (
              <div key={company} className="text-center text-slate-400 font-semibold">
                {company}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;