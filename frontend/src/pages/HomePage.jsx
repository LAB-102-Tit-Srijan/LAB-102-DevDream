import { useState, useEffect } from 'react';
import ChatInput from '../components/ChatInput';
import AIChatInterface from '../components/AIChatInterface';
import { useAuth } from '../context/AuthContext';
import videoService from '../services/videoService';
import Loader from '../components/Loader';

const HomePage = () => {
  const { user } = useAuth();
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    try {
      // 1. Upload to backend
      const response = await videoService.uploadVideo(
        file, 
        file.name, // Using filename as title for now
        'General', // Default subject
        user?.email || 'anonymous'
      );

      console.log('Upload success:', response);

      // 2. Set local preview after successful upload
      const url = URL.createObjectURL(file);
      setVideoFile({
        ...file,
        id: response.data.video_id,
        serverPath: response.data.file_path,
        name: file.name
      });
      setVideoUrl(url);
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err || 'Failed to upload video');
    } finally {
      setIsUploading(false);
    }
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
      {isUploading ? (
        <div className="flex flex-col items-center gap-4">
          <Loader />
          <p className="text-[#D1D1D1] animate-pulse">Uploading your video to StudyAI...</p>
        </div>
      ) : !videoFile ? (
        <div className="w-full max-w-4xl flex flex-col items-center animate-in fade-in duration-1000">
          <div className="mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-serif text-[#D1D1D1]">
              Good evening, {userName}
            </h1>
            {error && (
              <p className="text-red-400 mt-4 text-sm bg-red-400/10 py-2 px-4 rounded-full border border-red-400/20">
                {error}
              </p>
            )}
          </div>
          
          <ChatInput onFileUpload={handleFileUpload} isLoading={isUploading} />
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

          {/* AI Chat Area */}
          <div className="lg:col-span-5 xl:col-span-4 h-full">
            <AIChatInterface videoData={videoFile} />
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
