import React, { useState } from 'react';
import Configuration from './components/Configuration';
import VoiceInterface from './components/VoiceInterface';
import ReportView from './components/ReportView';

type AppState = 'CONFIG' | 'VOICE' | 'REPORT';

function App() {
  const [state, setState] = useState<AppState>('CONFIG');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const handleSessionCreated = (id: number, tkn: string) => {
    setSessionId(id);
    setToken(tkn);
    setState('VOICE');
  };

  const handleSessionEnded = () => {
    setState('REPORT');
  };

  const handleReset = () => {
    setSessionId(null);
    setToken(null);
    setState('CONFIG');
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {state === 'CONFIG' && (
          <Configuration onSessionCreated={handleSessionCreated} />
        )}

        {state === 'VOICE' && sessionId && token && (
          <VoiceInterface
            sessionId={sessionId}
            token={token}
            onSessionEnded={handleSessionEnded}
          />
        )}

        {state === 'REPORT' && sessionId && (
          <ReportView
            sessionId={sessionId}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
}

export default App;
