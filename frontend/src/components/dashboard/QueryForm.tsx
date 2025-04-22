import React, { useState } from 'react';
import { Search, FileText, Calendar, Tag } from 'lucide-react';
import Button from '../common/Button';
import TextArea from '../common/TextArea';
import Select from '../common/Select';
import Input from '../common/Input';

interface QueryFormProps {
  onSubmit: (query: string, filters: QueryFilters) => void;
  isLoading: boolean;
}

export interface QueryFilters {
  product: string;
  industry: string;
  timeRange: string;
}

const industries = [
  { value: 'all', label: 'All Industries' },
  { value: 'tech', label: 'Technology' },
  { value: 'fashion', label: 'Fashion & Apparel' },
  { value: 'health', label: 'Health & Beauty' },
  { value: 'home', label: 'Home & Kitchen' },
  { value: 'electronics', label: 'Electronics' },
];

const timeRanges = [
  { value: 'week', label: 'Past Week' },
  { value: 'month', label: 'Past Month' },
  { value: 'quarter', label: 'Past Quarter' },
  { value: 'year', label: 'Past Year' },
  { value: 'all', label: 'All Time' },
];

const products = [
  { value: '', label: 'All Products' },
  { value: 'arlo-essential', label: 'Arlo Essential Security Camera' },
  { value: 'sony-wh1000xm4', label: 'Sony WH-1000XM4' },
  { value: 'dyson-v11', label: 'Dyson V11 Vacuum' },
  { value: 'airpods-pro', label: 'Apple AirPods Pro' },
  { value: 'kindle-paperwhite', label: 'Kindle Paperwhite' },
];

const QueryForm: React.FC<QueryFormProps> = ({ onSubmit, isLoading }) => {
  const [query, setQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [filters, setFilters] = useState<QueryFilters>({
    product: '',
    industry: 'all',
    timeRange: 'month',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query, filters);
    }
  };

  const handleFilterChange = (key: keyof QueryFilters, value: string) => {
    setFilters({ ...filters, [key]: value });
  };

  const exampleQueries = [
    "Analyze user feedback for Arlo Essential Security Camera focusing on battery life",
    "What are the most common complaints about Sony WH-1000XM4 headphones?",
    "Compare sentiment analysis between Apple AirPods Pro and Sony WH-1000XM4",
    "Identify key themes in Kindle Paperwhite reviews from the last 3 months"
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <TextArea
          label="Research Query"
          placeholder="Enter your market research question or topic..."
          rows={4}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          fullWidth
          helperText="Ask specific questions about products, user sentiment, or market trends."
        />
        <div className="text-sm text-gray-500">
          <p className="mb-2">Example queries:</p>
          <ul className="space-y-1.5">
            {exampleQueries.map((example, index) => (
              <li key={index}>
                <button
                  type="button"
                  className="text-blue-600 hover:text-blue-800 text-left"
                  onClick={() => setQuery(example)}
                >
                  "{example}"
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <button
          type="button"
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          <svg
            className={`ml-1 h-4 w-4 transform ${showAdvanced ? 'rotate-180' : ''} transition-transform duration-200`}
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 pb-3 animate-fade-in">
          <Select
            label="Product"
            options={products}
            value={filters.product}
            onChange={(value) => handleFilterChange('product', value)}
            fullWidth
            leftIcon={<Tag className="h-4 w-4 text-gray-400" />}
          />
          
          <Select
            label="Industry"
            options={industries}
            value={filters.industry}
            onChange={(value) => handleFilterChange('industry', value)}
            fullWidth
            leftIcon={<FileText className="h-4 w-4 text-gray-400" />}
          />
          
          <Select
            label="Time Range"
            options={timeRanges}
            value={filters.timeRange}
            onChange={(value) => handleFilterChange('timeRange', value)}
            fullWidth
            leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
          />
        </div>
      )}

      <div>
        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          leftIcon={<Search className="h-4 w-4" />}
          fullWidth
          className="mt-2"
          disabled={query.trim() === '' || isLoading}
        >
          Generate Analysis Report
        </Button>
      </div>
    </form>
  );
};

export default QueryForm;