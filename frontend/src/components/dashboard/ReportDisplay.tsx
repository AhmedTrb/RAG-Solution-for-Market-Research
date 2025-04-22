import React, { useState } from 'react';
import { Report } from '../../types';
import Card from '../common/Card';
import SentimentChart from './SentimentChart';
import MetricsPanel from './MetricsPanel';
import ThemesList from './ThemesList';
import { FileDown, Copy, Share2 } from 'lucide-react';
import Button from '../common/Button';

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
    // Split text into paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      // Check if paragraph is a header (starts with # or ##)
      if (paragraph.startsWith('# ')) {
        return <h2 key={index} className="text-xl font-bold mt-6 mb-4">{paragraph.substring(2)}</h2>;
      } else if (paragraph.startsWith('## ')) {
        return <h3 key={index} className="text-lg font-bold mt-5 mb-3">{paragraph.substring(3)}</h3>;
      } else if (paragraph.startsWith('- ')) {
        // Handle bullet points
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
        <h2 className="text-2xl font-bold text-gray-900">Research Report</h2>
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
        <div>{formatReportText(report.report)}</div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <SentimentChart sentiment={report.sentiments} />
        </Card>
        <Card className="lg:col-span-2">
          <ThemesList themes={report.key_themes} />
        </Card>
      </div>

      <MetricsPanel metrics={report.metrics} />
    </div>
  );
};

export default ReportDisplay;