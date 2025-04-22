export interface Metric {
  title: string;
  value: string;
  description: string;
}

export interface Sentiment {
  description: string;
  positive: string | number;
  neutral: string | number;
  negative: string | number;
}

export interface Report {
  report: string;
  metrics: Metric[];
  sentiments: Sentiment;
  key_themes: string[];
}

export interface User {
  id: string;
  name: string;
  email: string;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  reportId: string;
}