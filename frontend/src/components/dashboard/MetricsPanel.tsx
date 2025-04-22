import React from 'react';
import { Metric } from '../../types';
import Card from '../common/Card';

interface MetricsPanelProps {
  metrics: Metric[];
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics }) => {
  if (!metrics || metrics.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Key Metrics</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric, index) => (
          <Card key={index} className="transition-all duration-300 transform hover:scale-105 hover:shadow-lg">
            <div className="text-center">
              <h4 className="text-sm font-medium text-gray-500">{metric.title}</h4>
              <div className="mt-2 text-3xl font-bold text-gray-900">{metric.value}</div>
              {metric.description && (
                <p className="mt-2 text-sm text-gray-500">{metric.description}</p>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default MetricsPanel;