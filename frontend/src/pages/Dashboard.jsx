import { useState, useEffect, useRef } from 'react';
import AIChatInterface from '../components/AIChatInterface';
import TranscriptViewer from '../components/TranscriptViewer';
import SmartNotepad from '../components/SmartNotepad';
import QuizModal from '../components/QuizModal';
import { Download, Clock, X } from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import videoService from '../services/videoService';
import Loader from '../components/Loader';
import { UploadCloud, FileText, BrainCircuit, StickyNote, BrainCog, Sparkles } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [activeRightTab, setActiveRightTab] = useState('transcript');
  const [showQuiz, setShowQuiz] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
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

  const handleVideoEnded = () => setShowQuiz(true);

  useEffect(() => {
    return () => { if (videoUrl) URL.revokeObjectURL(videoUrl); };
  }, [videoUrl]);

  const userName = user?.email?.split('@')[0] || 'Student';

  // ── Upload / Loading States ──────────────────────────────────────────
  if (isUploading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 h-[calc(100vh-5rem)]">
        <Loader />
        <p className="text-slate-300 animate-pulse">Uploading and preparing AI features...</p>
      </div>
    );
  }

  if (!videoFile) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center animate-in fade-in duration-1000 h-[calc(100vh-5rem)]">
        <div className="mb-10 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
            Welcome, <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">{userName}</span>
          </h1>
          <p className="text-slate-400 mt-4 text-lg">Upload a lecture to activate your AI Learning Companion.</p>
          {error && (
            <p className="text-red-400 mt-4 text-sm bg-red-400/10 py-2 px-4 rounded-full border border-red-400/20">{error}</p>
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
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="video/*" className="hidden" />
        </div>
      </div>
    );
  }

  // ── 3-Column Workspace ───────────────────────────────────────────────
  return (
    <>
      <div className="w-full h-[calc(100vh-5rem)] overflow-hidden grid grid-cols-1 lg:grid-cols-12 gap-0 animate-in fade-in slide-in-from-bottom-2 duration-500">

        {/* ═══ LEFT COLUMN: Video & Timestamps ═══ */}
        <div className="lg:col-span-8 h-full overflow-y-auto flex flex-col bg-[#09090b] border-r border-white/5 scrollbar-thin scrollbar-thumb-white/10">
          {/* Video Player */}
          <div className="p-4 flex flex-col gap-4">
            {/* Video Meta Bar */}
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <h2 className="text-xl font-semibold text-white truncate">{videoFile.name}</h2>
                <p className="text-primary-400/80 text-sm mt-0.5 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse"></span>
                  {videoId ? 'AI Sync Active' : 'Processing...'}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => setShowQuiz(true)}
                  className="flex items-center gap-1.5 text-sm text-purple-300 bg-purple-500/10 hover:bg-purple-500/20 px-4 py-2 rounded-full transition-all border border-purple-500/20 font-medium"
                >
                  <BrainCog className="w-4 h-4" />
                  Take Quiz
                </button>
                <button
                  onClick={() => { setVideoFile(null); setVideoUrl(null); setVideoId(null); }}
                  className="text-sm text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full transition-all border border-white/5"
                >
                  Change
                </button>
              </div>
            </div>

            {/* Video Frame */}
            <div className="w-full aspect-video bg-black rounded-2xl overflow-hidden border border-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.5)] relative">
              <video
                ref={videoRef}
                src={videoUrl}
                controls
                onEnded={handleVideoEnded}
                className="w-full h-full object-contain"
              />
            </div>
          </div>

          {/* Timestamps Section */}
          <div className="flex-1 px-4 pb-4 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary-400" />
                <h3 className="text-xl font-semibold text-white">Timestamps</h3>
              </div>
              <button className="flex items-center gap-2 text-sm bg-white/5 hover:bg-white/10 px-4 py-2 rounded-xl border border-white/10 text-slate-300 transition-colors font-medium">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
            <div className="flex-1 bg-black/20 rounded-2xl border border-white/5 overflow-hidden shadow-inner min-h-[400px]">
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

        {/* ═══ RIGHT COLUMN: AI Chat & Actions ═══ */}
        <div className="lg:col-span-4 h-full overflow-hidden flex flex-col bg-black/20">
          {/* AI Chat Header */}
          <div className="shrink-0 px-4 py-3 border-b border-white/5 bg-white/[0.03] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-[0_0_12px_rgba(249,115,22,0.3)]">
                <BrainCircuit className="w-4 h-4 text-white" />
              </div>
              <span className="text-base font-semibold text-white tracking-tight">AI Assistant</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-black/40 px-2.5 py-1 rounded-full border border-white/5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Active
            </div>
          </div>

          {/* Chat fills remaining height */}
          <div className="flex-1 overflow-hidden">
            <AIChatInterface videoData={videoFile} />
          </div>

          {/* Notes / Summary Actions Button */}
          <div className="shrink-0 p-4 border-t border-white/5 bg-black/40">
            <button
              onClick={() => setShowNotes(true)}
              className="w-full flex items-center justify-center gap-2 py-3 bg-[#18181b] hover:bg-[#27272a] border border-white/5 text-slate-300 rounded-xl transition-all font-medium shadow-sm"
            >
              <FileText className="w-4 h-4 text-primary-400" />
              Generate Lecture Summary
            </button>
          </div>
        </div>
      </div>

      {/* Notes Modal Overlay */}
      {showNotes && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-[#111318] border border-white/10 rounded-[28px] w-full max-w-3xl h-[80vh] mx-4 shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
            {/* Modal Header */}
            <div className="shrink-0 p-4 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-yellow-500/10 to-amber-500/10">
              <div className="flex items-center gap-2">
                <StickyNote className="w-5 h-5 text-yellow-400" />
                <span className="text-lg font-semibold text-white">Lecture Notes & Summary</span>
              </div>
              <button
                onClick={() => setShowNotes(false)}
                className="p-2 hover:bg-white/10 rounded-xl transition-colors text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            {/* Modal Body */}
            <div className="flex-1 overflow-hidden bg-black/20">
              <SmartNotepad videoId={videoId} videoRef={videoRef} />
            </div>
          </div>
        </div>
      )}

      {/* Quiz Modal (portal-level) */}
      <QuizModal
        videoId={videoId}
        isOpen={showQuiz}
        onClose={() => setShowQuiz(false)}
      />
    </>
  );
};

export default Dashboard;
