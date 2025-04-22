import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart2, Search, TrendingUp, FileText, PieChart, MessageSquare } from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import Button from '../components/common/Button';

const LandingPage: React.FC = () => {
  const features = [
    {
      name: 'Sentiment Analysis',
      description: 'Analyze user sentiments across thousands of reviews and social media posts to understand how customers truly feel about products.',
      icon: <MessageSquare className="h-8 w-8 text-blue-500" />
    },
    {
      name: 'Theme Extraction',
      description: 'Automatically identify recurring themes and topics from user feedback to pinpoint what matters most to your customers.',
      icon: <FileText className="h-8 w-8 text-blue-500" />
    },
    {
      name: 'Data Visualization',
      description: 'Transform complex data into intuitive visualizations that make it easy to grasp key insights at a glance.',
      icon: <PieChart className="h-8 w-8 text-blue-500" />
    },
    {
      name: 'Trend Identification',
      description: 'Spot emerging trends and patterns in the market before they become mainstream.',
      icon: <TrendingUp className="h-8 w-8 text-blue-500" />
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-700 to-indigo-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight">
                <span className="block">AI-Powered</span>
                <span className="block text-blue-200">Market Research</span>
              </h1>
              <p className="text-xl text-blue-100 max-w-3xl">
                Unlock actionable insights from product reviews and social media with our advanced AI analysis platform. Transform scattered feedback into strategic knowledge.
              </p>
              <div className="flex space-x-4 pt-4">
                <Link to="/dashboard">
                  <Button size="lg" variant="primary" className="bg-white text-blue-700 hover:bg-blue-50">
                    Get Started
                  </Button>
                </Link>
                <Link to="/auth">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-blue-800">
                    Sign In
                  </Button>
                </Link>
              </div>
            </div>
            <div className="lg:flex justify-end hidden">
              <div className="relative">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg blur opacity-30"></div>
                <div className="relative bg-white/10 backdrop-blur-sm rounded-lg p-8 shadow-xl border border-white/20">
                  <div className="flex justify-between items-center mb-6">
                    <div className="flex">
                      <div className="h-3 w-3 bg-red-500 rounded-full mr-2"></div>
                      <div className="h-3 w-3 bg-amber-500 rounded-full mr-2"></div>
                      <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                    </div>
                    <Search className="h-5 w-5 text-blue-200" />
                  </div>
                  <div className="space-y-4">
                    <div className="bg-white/5 rounded p-3">
                      <div className="text-sm text-blue-200 mb-2">Query:</div>
                      <div className="text-white">Analyze customer feedback for wireless headphones focusing on sound quality</div>
                    </div>
                    <div className="bg-white/5 rounded p-3">
                      <div className="text-sm text-blue-200 mb-2">Results:</div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-white">Positive sentiment:</span>
                          <span className="text-green-300">68%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white">Negative sentiment:</span>
                          <span className="text-red-300">14%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white">Key themes:</span>
                          <span className="text-blue-300">Bass quality, Comfort</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 sm:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base font-semibold text-blue-600 uppercase tracking-wide">Features</h2>
            <p className="mt-1 text-3xl font-extrabold text-gray-900 sm:text-4xl sm:tracking-tight">
              Everything you need for market analysis
            </p>
            <p className="max-w-xl mt-5 mx-auto text-xl text-gray-500">
              Our platform uses advanced AI to analyze product reviews and social media, giving you actionable insights.
            </p>
          </div>

          <div className="mt-16">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-16">
              {features.map((feature) => (
                <div key={feature.name} className="relative">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0 h-14 w-14 rounded-full bg-blue-50 flex items-center justify-center">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{feature.name}</h3>
                      <p className="mt-2 text-base text-gray-500">{feature.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-16 sm:py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base font-semibold text-blue-600 uppercase tracking-wide">Process</h2>
            <p className="mt-1 text-3xl font-extrabold text-gray-900 sm:text-4xl sm:tracking-tight">
              How It Works
            </p>
          </div>

          <div className="mt-16">
            <div className="relative">
              <div className="absolute inset-0 flex items-center" aria-hidden="true">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-around">
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-600 text-white font-bold text-xl">
                    1
                  </div>
                  <div className="mt-4 text-center max-w-xs">
                    <h3 className="text-lg font-medium text-gray-900">Ask a Question</h3>
                    <p className="mt-2 text-sm text-gray-500">
                      Enter your research query about specific products, industries, or market trends
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-600 text-white font-bold text-xl">
                    2
                  </div>
                  <div className="mt-4 text-center max-w-xs">
                    <h3 className="text-lg font-medium text-gray-900">AI Analysis</h3>
                    <p className="mt-2 text-sm text-gray-500">
                      Our AI processes thousands of reviews and social media posts in seconds
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-600 text-white font-bold text-xl">
                    3
                  </div>
                  <div className="mt-4 text-center max-w-xs">
                    <h3 className="text-lg font-medium text-gray-900">Get Insights</h3>
                    <p className="mt-2 text-sm text-gray-500">
                      Receive a comprehensive report with actionable insights and visual data
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-16 text-center">
            <Link to="/dashboard">
              <Button size="lg">
                Try It Now
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="py-16 sm:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base font-semibold text-blue-600 uppercase tracking-wide">Testimonials</h2>
            <p className="mt-1 text-3xl font-extrabold text-gray-900 sm:text-4xl sm:tracking-tight">
              What Our Users Say
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <img 
                  className="h-12 w-12 rounded-full object-cover"
                  src="https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?auto=compress&cs=tinysrgb&w=600" 
                  alt="User" 
                />
                <div className="ml-4">
                  <h4 className="text-lg font-bold">Sarah Johnson</h4>
                  <p className="text-gray-600">Marketing Director</p>
                </div>
              </div>
              <p className="text-gray-600 italic">
                "This platform transformed our approach to product development. We identified key pain points in customer feedback that we had been overlooking for months."
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <img 
                  className="h-12 w-12 rounded-full object-cover" 
                  src="https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=600" 
                  alt="User" 
                />
                <div className="ml-4">
                  <h4 className="text-lg font-bold">Michael Chen</h4>
                  <p className="text-gray-600">Product Manager</p>
                </div>
              </div>
              <p className="text-gray-600 italic">
                "The sentiment analysis saved us countless hours of manual review. We gained insights from thousands of reviews in minutes rather than weeks."
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <img 
                  className="h-12 w-12 rounded-full object-cover" 
                  src="https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&w=600" 
                  alt="User" 
                />
                <div className="ml-4">
                  <h4 className="text-lg font-bold">Emily Rodriguez</h4>
                  <p className="text-gray-600">Research Analyst</p>
                </div>
              </div>
              <p className="text-gray-600 italic">
                "The theme extraction feature helped us identify emerging trends in our industry months before our competitors caught on. Game-changing for our strategy."
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-700">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            <span className="block">Ready to dive deeper?</span>
            <span className="block text-blue-200">Start analyzing your market today.</span>
          </h2>
          <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md shadow">
              <Link to="/dashboard">
                <Button size="lg" className="bg-white text-blue-700 hover:bg-blue-50">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default LandingPage;