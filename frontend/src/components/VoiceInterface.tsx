import React, { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
} from '@livekit/components-react';
import { Mic, Square } from 'lucide-react';
import axios from 'axios';

interface VoiceInterfaceProps {
  sessionId: number;
  token: string;
  onSessionEnded: () => void;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({ sessionId, token, onSessionEnded }) => {
  const [isEnding, setIsEnding] = useState(false);
  const livekitUrl = (import.meta as any).env.VITE_LIVEKIT_URL || 'ws://localhost:7880';

  const handleEndSession = async () => {
    setIsEnding(true);
    try {
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
      await axios.post(`${apiUrl}/sessions/${sessionId}/complete`);
      onSessionEnded();
    } catch (error) {
      console.error('Failed to end session:', error);
      alert('Failed to end session properly.');
      onSessionEnded();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-8 p-12 bg-gray-50 rounded-3xl shadow-inner min-h-[400px]">
      <LiveKitRoom
        video={false}
        audio={true}
        token={token}
        serverUrl={livekitUrl}
        connectOptions={{ autoSubscribe: true }}
        onDisconnected={onSessionEnded}
        className="flex flex-col items-center w-full"
      >
        <div className="relative">
          <div className="pulse w-32 h-32 rounded-full bg-red-500 flex items-center justify-center z-10">
            <Mic className="text-white w-12 h-12" />
          </div>
        </div>

        <h2 className="text-xl font-medium text-gray-700 animate-pulse">กำลังคุยกับโค้ช...</h2>

        <RoomAudioRenderer />

        <button
          onClick={handleEndSession}
          disabled={isEnding}
          className="flex items-center space-x-2 px-8 py-3 bg-gray-800 text-white rounded-full hover:bg-gray-900 transition-colors disabled:opacity-50"
        >
          <Square className="w-4 h-4 fill-current" />
          <span>{isEnding ? 'กำลังประมวลผล...' : 'จบการสนทนา'}</span>
        </button>
      </LiveKitRoom>
    </div>
  );
};

export default VoiceInterface;
