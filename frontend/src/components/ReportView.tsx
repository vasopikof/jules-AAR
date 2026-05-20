import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Loader2, RefreshCw } from 'lucide-react';

interface ReportViewProps {
  sessionId: number;
  onReset: () => void;
}

const ReportView: React.FC<ReportViewProps> = ({ sessionId, onReset }) => {
  const [report, setReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchReport = async () => {
    setIsLoading(true);
    try {
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/sessions/${sessionId}`);
      if (response.data.report) {
        setReport(response.data.report);
        setIsLoading(false);
      } else {
        // Poll if report not ready yet
        setTimeout(fetchReport, 3000);
      }
    } catch (error) {
      console.error('Failed to fetch report:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [sessionId]);

  return (
    <div className="max-w-3xl mx-auto p-8 bg-white rounded-2xl shadow-xl space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 border-b pb-4">รายงานการสะท้อนคิด (Gibbs' Report)</h2>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
          <p className="text-gray-600 italic">กำลังวิเคราะห์และสรุปผลการสนทนา...</p>
        </div>
      ) : (
        <div className="prose prose-indigo max-w-none">
          <ReactMarkdown>{report || 'ไม่พบข้อมูลรายงาน'}</ReactMarkdown>
        </div>
      )}

      <div className="pt-6 border-t flex justify-center">
        <button
          onClick={onReset}
          className="flex items-center space-x-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>เริ่มเซสชันใหม่</span>
        </button>
      </div>
    </div>
  );
};

export default ReportView;
