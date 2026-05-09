import { useState, useEffect } from 'react';
import ChatInput from '../components/ChatInput';
import AIChatInterface from '../components/AIChatInterface';
import TranscriptViewer from '../components/TranscriptViewer';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { user } = useAuth();
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'transcript'

  const handleFileUpload = (file) => {
    const url = URL.createObjectURL(file);
    setVideoFile(file);
    setVideoUrl(url);
  };

  // Cleanup URL object when component unmounts or file changes
  useEffect(() => {
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl);
    };
  }, [videoUrl]);

  const userName = user?.email?.split('@')[0] || 'Aadarsh';

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 pb-12">
      {!videoFile ? (
        <div className="w-full max-w-4xl flex flex-col items-center animate-in fade-in duration-1000">
          <div className="mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-serif text-[#D1D1D1]">
              Good evening, {userName}
            </h1>
          </div>
          
          <ChatInput onFileUpload={handleFileUpload} />
        </div>
      ) : (
        <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          {/* Video Preview Section */}
          <div className="lg:col-span-7 xl:col-span-8 flex flex-col gap-4">
            <div className="aspect-video bg-black rounded-[24px] overflow-hidden border border-white/5 shadow-2xl relative group">
              <video 
                src={videoUrl} 
                controls 
                className="w-full h-full object-contain"
              />
              <button 
                onClick={() => { setVideoFile(null); setVideoUrl(null); }}
                className="absolute top-4 right-4 bg-black/50 hover:bg-black/80 text-white px-3 py-1 rounded-full text-xs transition-all opacity-0 group-hover:opacity-100"
              >
                Change Video
              </button>
            </div>
            <div className="px-2">
              <h2 className="text-xl font-bold text-white tracking-tight">{videoFile.name}</h2>
              <p className="text-slate-400 text-sm mt-1">Ready for AI analysis</p>
            </div>
          </div>

          {/* AI and Data Sidebar Area */}
          <div className="lg:col-span-5 xl:col-span-4 flex flex-col h-full min-h-[600px]">
            {/* Tab Switcher */}
            <div className="flex bg-[#212121] p-1 rounded-2xl mb-4 border border-white/5 self-start">
              <button 
                onClick={() => setActiveTab('chat')}
                className={`px-6 py-2 rounded-xl text-xs font-bold transition-all ${
                  activeTab === 'chat' 
                    ? 'bg-primary-600 text-white shadow-lg' 
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                AI CHAT
              </button>
              <button 
                onClick={() => setActiveTab('transcript')}
                className={`px-6 py-2 rounded-xl text-xs font-bold transition-all ${
                  activeTab === 'transcript' 
                    ? 'bg-primary-600 text-white shadow-lg' 
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                TRANSCRIPT
              </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 min-h-0">
              {activeTab === 'chat' ? (
                <AIChatInterface videoData={videoFile} />
              ) : (
                <TranscriptViewer onTimestampClick={(time) => console.log('Seeking to:', time)} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
