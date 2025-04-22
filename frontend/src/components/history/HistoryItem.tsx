import React from 'react';
import { SearchHistoryItem } from '../../types';
import { Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface HistoryItemProps {
  item: SearchHistoryItem;
  onSelect: (item: SearchHistoryItem) => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ item, onSelect }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const truncateQuery = (query: string, maxLength = 120) => {
    return query.length > maxLength ? `${query.substring(0, maxLength)}...` : query;
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow p-4 cursor-pointer"
      onClick={() => onSelect(item)}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1 flex-1">
          <h3 className="text-lg font-medium text-gray-900">{truncateQuery(item.query)}</h3>
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="h-4 w-4 mr-1" />
            <span>{formatDate(item.timestamp)}</span>
          </div>
        </div>
        <Link 
          to={`/dashboard?reportId=${item.reportId}`}
          className="text-blue-600 hover:text-blue-800 flex items-center"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="mr-1">View</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
};

export default HistoryItem;