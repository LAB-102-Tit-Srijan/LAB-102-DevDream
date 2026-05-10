import { useState, useEffect, useRef } from 'react';
import AIChatInterface from '../components/AIChatInterface';
import TranscriptViewer from '../components/TranscriptViewer';
import { useAuth } from '../context/AuthContext';
import videoService from '../services/videoService';
import Loader from '../components/Loader';
import { UploadCloud, FileText, Zap, Clock, BrainCircuit, PlayCircle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setIsUploading(true);
    setError(null);
    try {
      const response = await videoService.uploadVideo(file, file.name, 'General');
      const newVideoId = response.data.video_id;
      setVideoId(newVideoId);

      const url = URL.createObjectURL(file);
      setVideoFile({
        ...file,
        id: newVideoId,
        serverPath: response.data.file_path,
        name: file.name
      });
      setVideoUrl(url);
    } catch (err) {
      console.error('Upload failed:', err);
      setError(typeof err === 'string' ? err : 'Failed to upload video.');
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl);
    };
  }, [videoUrl]);

  const userName = user?.email?.split('@')[0] || 'Student';

  return (
    <div className="flex-1 flex flex-col px-4 pb-20 pt-8 max-w-[1600px] mx-auto w-full min-h-screen">
      {isUploading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <Loader />
          <p className="text-slate-300 animate-pulse">Uploading and preparing AI features...</p>
        </div>
      ) : !videoFile ? (
        <div className="flex-1 flex flex-col items-center justify-center animate-in fade-in duration-1000 min-h-[70vh]">
          <div className="mb-10 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
              Welcome, <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">{userName}</span>
            </h1>
            <p className="text-slate-400 mt-4 text-lg">Upload a lecture to activate your AI Learning Companion.</p>
            {error && (
              <p className="text-red-400 mt-4 text-sm bg-red-400/10 py-2 px-4 rounded-full border border-red-400/20">
                {error}
              </p>
            )}
          </div>
          
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="w-full max-w-xl aspect-video bg-black/40 hover:bg-black/60 border-2 border-dashed border-white/10 hover:border-primary-500/50 rounded-[32px] flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group shadow-2xl backdrop-blur-xl"
          >
            <div className="w-20 h-20 bg-primary-500/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mb-6 group-hover:bg-primary-500/20">
              <UploadCloud className="w-10 h-10 text-primary-400" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-2">Upload Video Lecture</h3>
            <p className="text-slate-500 text-sm">MP4, WebM, or OGG up to 500MB</p>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept="video/*" 
              className="hidden" 
            />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
          {/* LEFT COLUMN: Video -> AI Chat */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            
            {/* Video Player Card */}
            <div className="bg-black/40 rounded-[24px] border border-white/5 p-4 shadow-2xl backdrop-blur-xl flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white truncate max-w-2xl">{videoFile.name}</h2>
                  <p className="text-primary-400/80 text-sm mt-1 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></span>
                    {videoId ? 'AI Sync Active' : 'Processing...'}
                  </p>
                </div>
                <button 
                  onClick={() => { setVideoFile(null); setVideoUrl(null); setVideoId(null); }}
                  className="text-xs text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full transition-all border border-white/5"
                >
                  Change Video
                </button>
              </div>
              <div className="w-full aspect-video bg-black rounded-[16px] overflow-hidden border border-white/5 shadow-inner relative">
                <video 
                  ref={videoRef}
                  src={videoUrl} 
                  controls 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>

            {/* AI Chat Card */}
            <div className="bg-black/40 rounded-[24px] border border-white/5 p-1 shadow-2xl backdrop-blur-xl flex flex-col h-[600px]">
              <div className="p-3 border-b border-white/5 bg-white/5 flex items-center gap-2 rounded-t-[23px]">
                <BrainCircuit className="w-5 h-5 text-primary-400" />
                <span className="text-base font-semibold text-white">AI Companion</span>
              </div>
              <div className="flex-1 overflow-hidden">
                <AIChatInterface videoData={videoFile} />
              </div>
            </div>
            
          </div>

          {/* RIGHT COLUMN: Interactive Transcript (YouTube Playlist Style) */}
          <div className="lg:col-span-4 h-full">
            <div className="sticky top-24 w-full bg-black/40 rounded-[24px] border border-white/5 shadow-2xl backdrop-blur-xl overflow-hidden flex flex-col h-[calc(100vh-8rem)]">
              <div className="flex-1 overflow-hidden relative">
                <TranscriptViewer 
                  videoId={videoId} 
                  onTimestampClick={(time) => {
                    if (videoRef.current) {
                      videoRef.current.currentTime = time;
                      videoRef.current.play();
                    }
                  }} 
                />
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default Dashboard;
