import { useState } from 'react';
import UploadSection from '../components/UploadSection';
import VideoSection from '../components/VideoSection';
import AIChatInterface from '../components/AIChatInterface';
import { Sparkles, ArrowLeft } from 'lucide-react';

const HomePage = () => {
  const [selectedSource, setSelectedSource] = useState(null);

  const handleSourceSelect = (source) => {
    setSelectedSource(source);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center p-4 md:p-8">
      {!selectedSource ? (
        <UploadSection onSourceSelect={handleSourceSelect} />
      ) : (
        <div className="w-full max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
          <div className="flex items-center justify-between mb-2">
            <button 
              onClick={() => setSelectedSource(null)}
              className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              Change Source
            </button>
            <div className="flex items-center gap-2 px-3 py-1 bg-primary-500/10 border border-primary-500/20 rounded-full">
              <Sparkles className="w-3 h-3 text-primary-400" />
              <span className="text-[10px] font-bold text-primary-400 uppercase tracking-wider">AI Analysis Active</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Video Area */}
            <div className="lg:col-span-7 xl:col-span-8">
              <VideoSection url={selectedSource.url} />
            </div>

            {/* AI Chat Area */}
            <div className="lg:col-span-5 xl:col-span-4">
              <AIChatInterface videoData={selectedSource} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
