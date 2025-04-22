import { SearchHistoryItem } from '../types';

// Mock delay to simulate API call
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock storage key
const STORAGE_KEY = 'search_history';

export const saveSearch = async (query: string, reportId: string): Promise<SearchHistoryItem> => {
  await delay(300); // Simulate storage delay
  
  const newItem: SearchHistoryItem = {
    id: Math.random().toString(36).substr(2, 9),
    query,
    timestamp: new Date().toISOString(),
    reportId
  };
  
  // Get existing history
  const historyJson = localStorage.getItem(STORAGE_KEY);
  const history: SearchHistoryItem[] = historyJson ? JSON.parse(historyJson) : [];
  
  // Add new item to history
  const updatedHistory = [newItem, ...history].slice(0, 50); // Limit to 50 items
  
  // Save updated history
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedHistory));
  
  return newItem;
};

export const getSearchHistory = async (): Promise<SearchHistoryItem[]> => {
  await delay(500); // Simulate API delay
  
  const historyJson = localStorage.getItem(STORAGE_KEY);
  return historyJson ? JSON.parse(historyJson) : [];
};

export const clearSearchHistory = async (): Promise<void> => {
  await delay(500); // Simulate API delay
  localStorage.removeItem(STORAGE_KEY);
};

export const deleteSearchItem = async (id: string): Promise<void> => {
  await delay(300); // Simulate API delay
  
  const historyJson = localStorage.getItem(STORAGE_KEY);
  if (!historyJson) return;
  
  const history: SearchHistoryItem[] = JSON.parse(historyJson);
  const updatedHistory = history.filter(item => item.id !== id);
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedHistory));
};