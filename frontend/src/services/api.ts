import { Report } from '../types';

// Mock API service for development
const API_ENDPOINT = '/api/generate_report/';

// Mock delay to simulate API call
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Example report data
const MOCK_REPORTS: Record<string, Report> = {
  'default': {
    report: "# Market Analysis: Arlo Essential Security Camera\n\n## Overview\nThis analysis examined 1,247 user reviews and social media posts about the Arlo Essential Security Camera, focusing on battery life aspects. The data spans Amazon reviews and Reddit discussions from the past 3 months.\n\n## Key Findings\nThe Arlo Essential Security Camera receives mixed feedback regarding battery performance, with a slight negative trend. While many users appreciate the advertised battery life, actual performance appears to fall short of expectations in certain usage scenarios.\n\n## Battery Performance Analysis\nBattery life varies significantly based on usage patterns:\n- Heavy usage (frequent motion detection): 1-2 months average battery life\n- Moderate usage: 3-4 months average battery life\n- Light usage: 5-6 months average battery life\n\nMany users report that extreme weather conditions (particularly cold temperatures) significantly reduce battery performance by 40-60%, which isn't clearly communicated in product marketing materials.\n\n## Common Complaints\n- Battery drains faster than the advertised 6-month lifespan\n- Cold weather performance issues\n- Inconsistent battery life between identical camera units\n- Battery level indicator inaccuracy",
    metrics: [
      {
        title: "Average Battery Life",
        value: "3.2 months",
        description: "Across all usage patterns reported"
      },
      {
        title: "Weather Impact",
        value: "-45%",
        description: "Average battery reduction in cold weather"
      },
      {
        title: "Reviews Analyzed",
        value: "1,247",
        description: "From Amazon reviews and Reddit posts"
      }
    ],
    sentiments: {
      description: "Overall sentiment regarding battery performance",
      positive: "35",
      neutral: "20",
      negative: "45"
    },
    key_themes: [
      "Battery life below expectations",
      "Weather impact significant",
      "Charging frequency frustration",
      "Motion detection settings battery impact",
      "Battery indicator accuracy",
      "Firmware updates"
    ]
  },
  'airpods': {
    report: "# Market Analysis: Apple AirPods Pro\n\n## Overview\nThis analysis examined 2,418 user reviews and social media discussions about the Apple AirPods Pro, focusing on noise cancellation effectiveness and sound quality. The data spans Amazon reviews, Reddit discussions, and Twitter mentions from the past 6 months.\n\n## Key Findings\nThe Apple AirPods Pro receives overwhelmingly positive feedback for both noise cancellation and sound quality. Users particularly praise the balance between features, comfort, and integration with the Apple ecosystem.\n\n## Noise Cancellation Analysis\nThe Active Noise Cancellation (ANC) feature is highlighted as industry-leading for earbuds in this category:\n- Excellent for commuting environments (public transport, busy streets)\n- Effective for office settings and eliminating background conversations\n- Mixed results for high-frequency sounds\n- Transparency mode highly praised for natural sound pass-through\n\nMost users report significant satisfaction with noise isolation capabilities, though some experienced users coming from over-ear headphones note limitations inherent to the earbud form factor.\n\n## Sound Quality Assessment\nSound profile is described as balanced with good detail:\n- Clear mid-range for vocals and spoken content\n- Adequate but not overwhelming bass response\n- Crisp high frequencies without harshness\n- Spatial audio feature receives extremely positive feedback",
    metrics: [
      {
        title: "ANC Effectiveness",
        value: "8.7/10",
        description: "User rating for noise cancellation"
      },
      {
        title: "Sound Quality",
        value: "8.3/10",
        description: "Average user rating across reviews"
      },
      {
        title: "Customer Satisfaction",
        value: "92%",
        description: "Users reporting positive experience"
      },
      {
        title: "Reviews Analyzed",
        value: "2,418",
        description: "From multiple platforms"
      }
    ],
    sentiments: {
      description: "Overall sentiment distribution",
      positive: "80",
      neutral: "12",
      negative: "8"
    },
    key_themes: [
      "Excellent noise cancellation",
      "Balanced sound profile",
      "Spatial audio experience",
      "Seamless Apple ecosystem integration",
      "Comfort during extended wear",
      "Battery concerns",
      "Price premium justified"
    ]
  }
};

export const generateReport = async (query: string): Promise<Report> => {
  try {
    // In a real implementation, this would make an API call to the Python backend
    // For now, we're simulating a delay and returning mock data
    await delay(2500); // Simulate API delay
    
    // Return different mock data based on query content
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
  // In a real implementation, this would fetch a specific report by ID
  await delay(1000);
  
  if (reportId === 'airpods') {
    return MOCK_REPORTS.airpods;
  }
  
  return MOCK_REPORTS.default;
};