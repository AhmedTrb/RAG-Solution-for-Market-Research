import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Trash2 } from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import Button from '../components/common/Button';
import HistoryItem from '../components/history/HistoryItem';
import { SearchHistoryItem } from '../types';
import { getSearchHistory, clearSearchHistory, deleteSearchItem, saveSearch } from '../services/history';

const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await getSearchHistory();
      setHistory(data);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear all search history?')) {
      setIsLoading(true);
      try {
        await clearSearchHistory();
        setHistory([]);
      } catch (error) {
        console.error('Failed to clear history:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDeleteItem = async (id: string) => {
    try {
      await deleteSearchItem(id);
      setHistory(history.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const handleSelectItem = (item: SearchHistoryItem) => {
    navigate(`/dashboard?reportId=${item.reportId}`);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <div className="flex-grow bg-gray-50">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Search History</h1>
              <p className="mt-2 text-lg text-gray-600">
                View and access your previous research queries
              </p>
            </div>
            {history.length > 0 && (
              <Button
                variant="outline"
                leftIcon={<Trash2 className="h-4 w-4" />}
                onClick={handleClearHistory}
              >
                Clear History
              </Button>
            )}
          </div>
          
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : history.length > 0 ? (
            <div className="grid grid-cols-1 gap-4">
              {history.map((item) => (
                <HistoryItem 
                  key={item.id} 
                  item={item} 
                  onSelect={handleSelectItem} 
                />
              ))}
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg p-12 text-center">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No search history yet</h3>
              <p className="text-gray-500 mb-6">
                Your research queries will appear here once you start analyzing data.
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/dashboard')}
              >
                Start Researching
              </Button>
            </div>
          )}
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default HistoryPage;