import axios from 'axios';
import { Report } from '../types';

const baseUrl = "http://localhost:5000"; // Or however you handle envs

interface ResearchRequest {
  query: string;
  retrieval_method: 'similarity' ;
}

export async function fetchResearchReport(payload: ResearchRequest): Promise<Report> {
  try {
    const response = await axios.post<Report>(`${baseUrl}/api/research`, payload);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error; // rethrow so the caller knows
  }
}

// Optional: Centralized error handler
function handleApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    console.error('API Error:', error.response?.data || error.message);
  } else {
    console.error('Unexpected Error:', error);
  }
}
