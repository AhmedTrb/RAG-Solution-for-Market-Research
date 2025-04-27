export interface AspectSentiment {
  aspect: string;
  negative_count: string;
  neutral_count: string;
  positive_count: string;
  summary: string;
  total_mentions: string;
}

export interface Metric {
  title: string;
  value: string | number;
  description: string;
}

export interface Sentiment {
  description: string;
  positive: string | number;
  neutral: string | number;
  negative: string | number;
}

export interface Report {
  aspect_sentiments_aggregated: AspectSentiment[];
  key_themes: string[];
  metrics: Metric[];
  report: string;
  retrieval_method_used: string;
  retrieved_document_count: number;
  sentiments: Sentiment;
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