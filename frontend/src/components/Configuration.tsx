import React, { useState } from 'react';
import axios from 'axios';

interface ConfigurationProps {
  onSessionCreated: (sessionId: number, token: string) => void;
}

const Configuration: React.FC<ConfigurationProps> = ({ onSessionCreated }) => {
  const [contextText, setContextText] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/sessions`, {
        context_text: contextText,
        system_prompt: systemPrompt,
      });
      onSessionCreated(response.data.id, response.data.token);
    } catch (error) {
      console.error('Failed to create session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-md space-y-6">
      <h1 className="text-2xl font-bold text-gray-800 text-center">AI Reflective Voice Coach (Thai)</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Context (เกิดอะไรขึ้น?)</label>
          <textarea
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
            rows={4}
            placeholder="เล่ารายละเอียดเหตุการณ์ที่ต้องการทบทวน..."
            value={contextText}
            onChange={(e) => setContextText(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">System Prompt (คำแนะนำเพิ่มเติมสำหรับ AI)</label>
          <textarea
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
            rows={2}
            placeholder="เช่น เน้นเรื่องการจัดการอารมณ์..."
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isLoading ? 'Starting...' : 'เริ่มการสนทนา'}
        </button>
      </form>
    </div>
  );
};

export default Configuration;
