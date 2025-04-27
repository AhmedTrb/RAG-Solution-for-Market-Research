import { Report } from '../types';

// Mock API service for development
const API_ENDPOINT = '/api/generate_report/';

// Mock delay to simulate API call
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Example report data
const MOCK_REPORTS: Record<string, Report> = {
  'default': {
    aspect_sentiments_aggregated: [
      {
        aspect: "battery",
        negative_count: "0",
        neutral_count: "0",
        positive_count: "1",
        summary: "Positive sentiment expressed towards battery life.",
        total_mentions: "1"
      },
      {
        aspect: "life",
        negative_count: "0",
        neutral_count: "0",
        positive_count: "1",
        summary: "Positive sentiment expressed towards battery life.",
        total_mentions: "1"
      }
    ],
    key_themes: [
      "Battery Life",
      "Cold Weather",
      "Camera"
    ],
    metrics: [
      {
        description: "Number of documents that explicitly mention battery life.",
        title: "Documents mentioning battery life",
        value: 2
      }
    ],
    report: "The main complaint about battery life for cameras, specifically mentioned in the context of cold weather, is that it drains rapidly. One review mentions excellent battery life but notes that it drains quickly in cold weather environments. Another review mentions excellent battery life and decent battery life, but also notes that arctic temperatures have a major impact.",
    retrieval_method_used: "similarity",
    retrieved_document_count: 1,
    sentiments: {
      description: "Overall sentiment distribution across the documents: positive, neutral, and negative.",
      negative: 1,
      neutral: 5,
      positive: 2
    }
  },
  'airpods': {
    aspect_sentiments_aggregated: [
      {
        aspect: "sound quality",
        negative_count: "1",
        neutral_count: "2",
        positive_count: "5",
        summary: "Generally positive feedback on sound quality with some concerns.",
        total_mentions: "8"
      },
      {
        aspect: "noise cancellation",
        negative_count: "0",
        neutral_count: "1",
        positive_count: "4",
        summary: "Very positive feedback on noise cancellation effectiveness.",
        total_mentions: "5"
      }
    ],
    key_themes: [
      "Sound Quality",
      "Noise Cancellation",
      "Comfort",
      "Battery Life",
      "Price"
    ],
    metrics: [
      {
        title: "Total Reviews Analyzed",
        value: 2418,
        description: "Number of reviews processed for this analysis"
      },
      {
        title: "Average Rating",
        value: "4.5",
        description: "Average star rating across all reviews"
      }
    ],
    report: "Analysis of AirPods Pro reviews shows overwhelmingly positive feedback for both sound quality and noise cancellation features. Users particularly praise the balance between features, comfort, and integration with the Apple ecosystem. The Active Noise Cancellation (ANC) is highlighted as industry-leading for earbuds in this category, especially effective in commuting environments and office settings.",
    retrieval_method_used: "hybrid",
    retrieved_document_count: 2418,
    sentiments: {
      description: "Overall sentiment distribution across all analyzed reviews",
      positive: 80,
      neutral: 12,
      negative: 8
    }
  }
};

export const generateReport = async (query: string): Promise<Report> => {
  try {
    await delay(2500);
    
    if (query.toLowerCase().includes('airpods')) {
      return MOCK_REPORTS.airpods;
    }
    
    return MOCK_REPORTS.default;
  } catch (error) {
    console.error('Error generating report:', error);
    throw new Error('Failed to generate report. Please try again.');
  }
};

export const getReportById = async (reportId: string): Promise<Report> => {
  await delay(1000);
  
  if (reportId === 'airpods') {
    return MOCK_REPORTS.airpods;
  }
  
  return MOCK_REPORTS.default;
};