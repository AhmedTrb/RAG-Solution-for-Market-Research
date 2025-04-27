import React from 'react';
import { Sentiment } from '../../types';

interface SentimentChartProps {
  sentiment: Sentiment;
}

const SentimentChart: React.FC<SentimentChartProps> = ({ sentiment }) => {
  const positive = typeof sentiment.positive === 'string' 
    ? parseFloat(sentiment.positive) 
    : sentiment.positive;
  
  const neutral = typeof sentiment.neutral === 'string' 
    ? parseFloat(sentiment.neutral) 
    : sentiment.neutral;
  
  const negative = typeof sentiment.negative === 'string' 
    ? parseFloat(sentiment.negative) 
    : sentiment.negative;

  const total = positive + neutral + negative;
  const positivePercent = total > 0 ? (positive / total) * 100 : 0;
  const neutralPercent = total > 0 ? (neutral / total) * 100 : 0;
  const negativePercent = total > 0 ? (negative / total) * 100 : 0;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Sentiment Analysis</h3>
      <p className="text-sm text-gray-500">{sentiment.description}</p>
      
      <div className="flex items-center w-full h-6 rounded-full overflow-hidden">
        <div 
          className="h-full bg-green-500 transition-all duration-500 ease-in-out"
          style={{ width: `${positivePercent}%` }}
        ></div>
        <div 
          className="h-full bg-gray-300 transition-all duration-500 ease-in-out"
          style={{ width: `${neutralPercent}%` }}
        ></div>
        <div 
          className="h-full bg-red-500 transition-all duration-500 ease-in-out"
          style={{ width: `${negativePercent}%` }}
        ></div>
      </div>
      
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="space-y-1">
          <div className="flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span className="text-sm font-medium text-gray-900">Positive</span>
          </div>
          <p className="text-lg font-bold text-gray-900">{positivePercent.toFixed(1)}%</p>
          <p className="text-sm text-gray-500">({positive})</p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-gray-300 mr-2"></div>
            <span className="text-sm font-medium text-gray-900">Neutral</span>
          </div>
          <p className="text-lg font-bold text-gray-900">{neutralPercent.toFixed(1)}%</p>
          <p className="text-sm text-gray-500">({neutral})</p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <span className="text-sm font-medium text-gray-900">Negative</span>
          </div>
          <p className="text-lg font-bold text-gray-900">{negativePercent.toFixed(1)}%</p>
          <p className="text-sm text-gray-500">({negative})</p>
        </div>
      </div>
    </div>
  );
};

export default SentimentChart;