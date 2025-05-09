import React, { useState } from 'react';
import { Report } from '../../types';
import Card from '../common/Card';
import SentimentChart from './SentimentChart';
import MetricsPanel from './MetricsPanel';
import ThemesList from './ThemesList';
import { FileDown, Copy, Share2 } from 'lucide-react';
import Button from '../common/Button';
import { jsPDF } from 'jspdf';
import ReactMarkdown from 'react-markdown';
interface ReportDisplayProps {
  report: Report | null;
}

const ReportDisplay: React.FC<ReportDisplayProps> = ({ report }) => {
  const [isCopied, setIsCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  if (!report) {
    return null;
  }

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(report.report);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      const doc = new jsPDF();
      
      // Add title
      doc.setFontSize(20);
      doc.text('Market Research Report', 20, 20);
      
      // Add timestamp
      doc.setFontSize(10);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
      
      // Add retrieval info
      doc.text(`Based on ${report.retrieved_document_count} documents using ${report.retrieval_method_used} search`, 20, 40);
      
      // Add main report content
      doc.setFontSize(12);
      const splitReport = doc.splitTextToSize(report.report, 170);
      doc.text(splitReport, 20, 60);
      
      let yPos = 60 + (splitReport.length * 7);
      
      // Add Key Themes
      doc.setFontSize(14);
      doc.text('Key Themes:', 20, yPos);
      doc.setFontSize(12);
      report.key_themes.forEach((theme) => {
        yPos += 7;
        doc.text(`• ${theme}`, 25, yPos);
      });
      
      yPos += 15;
      
      // Add Sentiment Analysis
      doc.setFontSize(14);
      doc.text('Sentiment Analysis:', 20, yPos);
      doc.setFontSize(12);
      yPos += 10;
      doc.text(`Positive: ${report.sentiments.positive}`, 25, yPos);
      yPos += 7;
      doc.text(`Neutral: ${report.sentiments.neutral}`, 25, yPos);
      yPos += 7;
      doc.text(`Negative: ${report.sentiments.negative}`, 25, yPos);
      
      // Add Aspect Sentiments
      if (yPos > 250) {
        doc.addPage();
        yPos = 20;
      }
      
      yPos += 15;
      doc.setFontSize(14);
      doc.text('Aspect Analysis:', 20, yPos);
      doc.setFontSize(12);
      
      report.aspect_sentiments_aggregated.forEach((aspect) => {
        if (yPos > 250) {
          doc.addPage();
          yPos = 20;
        }
        yPos += 10;
        doc.text(`${aspect.aspect}:`, 25, yPos);
        yPos += 7;
        doc.text(`Summary: ${aspect.summary}`, 30, yPos);
        yPos += 7;
        doc.text(`Total mentions: ${aspect.total_mentions}`, 30, yPos);
      });
      
      // Save the PDF
      doc.save('market-research-report.pdf');
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Research Report</h2>
          <p className="text-sm text-gray-500 mt-1">
            Based on {report.retrieved_document_count} documents using {report.retrieval_method_used} search
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            leftIcon={<Copy className="h-4 w-4" />}
            onClick={handleCopyToClipboard}
          >
            {isCopied ? 'Copied!' : 'Copy'}
          </Button>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<FileDown className="h-4 w-4" />}
            onClick={handleExportPDF}
            isLoading={isExporting}
          >
            {isExporting ? 'Exporting...' : 'Export PDF'}
          </Button>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<Share2 className="h-4 w-4" />}
          >
            Share
          </Button>
        </div>
      </div>

      <Card className="prose max-w-none">
        <ReactMarkdown>{report.report}</ReactMarkdown>
      </Card>


      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 ">
        <Card className="lg:col-span-1">
          <SentimentChart sentiment={report.sentiments} />
        </Card>
        <Card className="lg:col-span-2">
          <div className="space-y-6">
            <ThemesList themes={report.key_themes} />
            {Array.isArray(report?.aspect_sentiments_aggregated) && report.aspect_sentiments_aggregated.length > 0 && (
              <div className="mt-6 max-h-64 overflow-y-scroll">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Aspect-Based Sentiment Analysis</h3>
                <div className="space-y-4">
                  {report.aspect_sentiments_aggregated.map((aspect, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="text-sm font-medium text-gray-900 capitalize">{aspect.aspect}</h4>
                        <span className="text-sm text-gray-500">{aspect.total_mentions} mentions</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{aspect.summary}</p>
                      <div className="flex justify-between text-sm">
                        <span className="text-green-600">Positive: {aspect.positive_count}</span>
                        <span className="text-gray-600">Neutral: {aspect.neutral_count}</span>
                        <span className="text-red-600">Negative: {aspect.negative_count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>

      <MetricsPanel metrics={report.metrics} />
    </div>
  );
};

export default ReportDisplay;