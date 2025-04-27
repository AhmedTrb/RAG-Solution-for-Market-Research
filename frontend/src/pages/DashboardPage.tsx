import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import QueryForm, { QueryFilters } from '../components/dashboard/QueryForm';
import ReportDisplay from '../components/dashboard/ReportDisplay';
import { Report } from '../types';
import { generateReport, getReportById } from '../services/api';
import { saveSearch } from '../services/history';
import { fetchResearchReport } from '../services/ResearchService';

const DashboardPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);
  //const [loading, setLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const reportId = searchParams.get('reportId');

  useEffect(() => {
    // Check if a specific report ID was requested (from history)
    if (reportId) {
      setIsLoading(true);
      getReportById(reportId)
        .then(data => {
          setReport(data);
        })
        .catch(error => {
          console.error('Error fetching report:', error);
          // Handle error
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [reportId]);

  const handleFetchReport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchResearchReport({
        query: "What are the main complaints about battery life for Arlo cameras?",
        retrieval_method: "similarity",
      });
      setReport(data);
    } catch (err) {
      setError('Failed to fetch research report.');
    } finally {
      setIsLoading(false);
    }
  };
  // const handleQuerySubmit = async (query: string, filters: QueryFilters) => {
  //   setIsLoading(true);
  //   try {
  //     // Generate report
  //     const reportData = await generateReport(query);
  //     setReport(reportData);
      
  //     // Save to search history with a generated report ID
  //     const reportIdForHistory = query.toLowerCase().includes('airpod') 
  //       ? 'airpods' 
  //       : 'default';
      
  //     await saveSearch(query, reportIdForHistory);
  //   } catch (error) {
  //     console.error('Error:', error);
  //     // Handle error
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <div className="flex-grow bg-gray-50">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Market Research Dashboard</h1>
            <p className="mt-2 text-lg text-gray-600">
              Get deep insights from customer reviews and social media data
            </p>
          </div>
          
          <div className="grid grid-cols-1 gap-8">
            <div className="bg-white shadow rounded-lg p-6">
              <QueryForm onSubmit={handleFetchReport} isLoading={isLoading} />
            </div>
            
            {isLoading && (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            )}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error!</strong>
                <span className="block sm:inline">{error}</span>
              </div>
            )}
            {!isLoading && report && (
              <div className="bg-white shadow rounded-lg p-6">
                <ReportDisplay report={report} />
              </div>
            )}
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default DashboardPage;