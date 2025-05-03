import React, { useState } from 'react';
import { Report } from '../../types';
import Card from '../common/Card';
import SentimentChart from './SentimentChart';
import MetricsPanel from './MetricsPanel';
import ThemesList from './ThemesList';
import { FileDown, Copy, Share2 } from 'lucide-react';
import Button from '../common/Button';
import ReactMarkdown from 'react-markdown';
interface ReportDisplayProps {
  report: Report | null;
}

const ReportDisplay: React.FC<ReportDisplayProps> = ({ report }) => {
  const [isCopied, setIsCopied] = useState(false);

  if (!report) {
    return null;
  }

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(report.report);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleExportPDF = () => {
    alert('PDF export functionality would be implemented here');
  };

  const formatReportText = (text: string) => {
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      if (paragraph.startsWith('# ')) {
        return <h2 key={index} className="text-xl font-bold mt-6 mb-4">{paragraph.substring(2)}</h2>;
      } else if (paragraph.startsWith('## ')) {
        return <h3 key={index} className="text-lg font-bold mt-5 mb-3">{paragraph.substring(3)}</h3>;
      } else if (paragraph.startsWith('- ')) {
        const listItems = paragraph.split('\n- ');
        return (
          <ul key={index} className="list-disc pl-5 my-3 space-y-1">
            {listItems.map((item, i) => (
              <li key={i}>{item.replace('- ', '')}</li>
            ))}
          </ul>
        );
      } else if (paragraph.trim() !== '') {
        return <p key={index} className="my-3 leading-relaxed">{paragraph}</p>;
      }
      return null;
    });
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
          >
            Export
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