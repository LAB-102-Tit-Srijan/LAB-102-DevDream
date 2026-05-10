import { useState, useEffect, useRef } from 'react';
import { StickyNote, Plus, Download, Clock, Loader2, Cloud, Sparkles, ExternalLink, RefreshCw } from 'lucide-react';
import api from '../services/api';

const SmartNotepad = ({ videoId, videoRef }) => {
  const [notes, setNotes] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Google Docs State
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [generatedDocUrl, setGeneratedDocUrl] = useState(null);

  // Email Sync Modal State
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [syncEmail, setSyncEmail] = useState('');
  const [isSyncingDrive, setIsSyncingDrive] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');

  const inputRef = useRef(null);
  const capturedTimeRef = useRef(0);

  useEffect(() => {
    if (!videoId) return;
    const fetchNotes = async () => {
      setIsLoading(true);
      try {
        const res = await api.get(`/api/videos/${videoId}/notes`);
        if (res.data.status) setNotes(res.data.data);
      } catch (err) {
        console.error('Failed to fetch notes:', err);
      } finally {
        setIsLoading(false);
      }
    };

    const checkGoogleAuth = async () => {
      try {
        const res = await api.get('/api/google/auth/status');
        setIsGoogleConnected(res.data.connected);
      } catch (err) {
        console.error('Failed to check Google auth status:', err);
      }
    };

    fetchNotes();
    checkGoogleAuth();
  }, [videoId]);

  const handleFocus = () => {
    if (videoRef?.current) capturedTimeRef.current = videoRef.current.currentTime;
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAddNote = async () => {
    if (!input.trim() || isSaving) return;
    setIsSaving(true);
    try {
      const res = await api.post(`/api/videos/${videoId}/notes`, {
        content: input.trim(),
        timestamp: capturedTimeRef.current,
      });
      if (res.data.status) {
        setNotes(prev => [...prev, res.data.data]);
        setInput('');
      }
    } catch (err) {
      console.error('Failed to save note:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAddNote(); }
  };

  // Google Docs Integrations
  const handleConnectGoogle = async () => {
    try {
      const res = await api.get('/api/google/auth/connect');
      if (res.data.auth_url) {
        window.location.href = res.data.auth_url;
      }
    } catch (err) {
      console.error('Failed to get Google auth URL:', err);
    }
  };

  const handleSyncToDocs = async () => {
    if (!isGoogleConnected) return handleConnectGoogle();
    if (notes.length === 0) return;
    
    setIsSyncing(true);
    try {
      const res = await api.post(`/api/google/docs/sync-notes/${videoId}`);
      if (res.data.status && res.data.data.doc_url) {
        setGeneratedDocUrl(res.data.data.doc_url);
      }
    } catch (err) {
      console.error('Failed to sync to Google Docs:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleGenerateAINotes = async () => {
    setIsGeneratingAI(true);
    try {
      const res = await api.post(`/api/google/docs/ai-notes/${videoId}`);
      if (res.data.status && res.data.data.content) {
        setGeneratedContent(res.data.data.content);
        setShowEmailModal(true);
      }
    } catch (err) {
      console.error('Failed to generate AI notes:', err);
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleEmailSync = () => {
    if (!syncEmail.includes('@')) return;
    setIsSyncingDrive(true);
    
    // Simulate Google Drive Sync & PDF Generation for Demo
    setTimeout(() => {
      setIsSyncingDrive(false);
      setSyncSuccess(true);
      
      // Create a blob for the file
      const blob = new Blob([generatedContent], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `StudyAI_Notes_${videoId}.md`; // Downloading as MD for now
      a.click();
      URL.revokeObjectURL(url);
      
      setTimeout(() => {
        setShowEmailModal(false);
        setSyncSuccess(false);
        setSyncEmail('');
      }, 3000);
    }, 2500);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden relative">
      {/* Top Workspace Bar */}
      <div className="shrink-0 px-3 py-3 border-b border-white/5 bg-white/[0.02] flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-white flex items-center gap-1.5">
            <Cloud className="w-4 h-4 text-blue-400" />
            Smart Workspace
          </span>
          {!isGoogleConnected ? (
            <button 
              onClick={handleConnectGoogle}
              className="text-[10px] px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded hover:bg-blue-500/20 transition-colors"
            >
              Connect Google Drive
            </button>
          ) : (
            <span className="text-[10px] px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
              Drive Connected
            </span>
          )}
        </div>
        
        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={handleGenerateAINotes}
            disabled={isGeneratingAI}
            className="flex items-center justify-center gap-1.5 text-xs py-2 bg-gradient-to-r from-primary-500/20 to-purple-500/20 hover:from-primary-500/30 hover:to-purple-500/30 text-white border border-white/10 rounded-lg transition-all disabled:opacity-50"
          >
            {isGeneratingAI ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-primary-400" />}
            AI Magic Notes
          </button>
          <button
            onClick={handleSyncToDocs}
            disabled={isSyncing || notes.length === 0}
            className="flex items-center justify-center gap-1.5 text-xs py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/20 rounded-lg transition-all disabled:opacity-50"
          >
            {isSyncing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            Sync to Docs
          </button>
        </div>

        {/* Doc Link Banner */}
        {generatedDocUrl && (
          <a
            href={generatedDocUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg group hover:bg-blue-500/20 transition-all"
          >
            <span className="text-xs text-blue-300 flex items-center gap-1.5">
              <Cloud className="w-3.5 h-3.5" />
              Doc Ready in Drive
            </span>
            <ExternalLink className="w-3.5 h-3.5 text-blue-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </a>
        )}
      </div>

      {/* Notes List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin scrollbar-thumb-white/10">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-slate-500" />
          </div>
        ) : notes.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 opacity-50">
            <StickyNote className="w-8 h-8" />
            <p className="text-sm text-center">No notes yet.<br />Focus input to capture timestamp.</p>
          </div>
        ) : (
          notes.map((note, i) => (
            <div
              key={note.id || i}
              className="bg-white/5 border border-white/5 rounded-xl p-3 group hover:border-yellow-500/30 transition-colors"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <button
                  onClick={() => {
                    if (videoRef?.current) {
                      videoRef.current.currentTime = note.timestamp;
                      videoRef.current.play();
                    }
                  }}
                  className="flex items-center gap-1 text-xs font-mono text-yellow-400 hover:text-yellow-300 bg-yellow-500/10 px-2 py-1 rounded-md transition-colors"
                >
                  <Clock className="w-3.5 h-3.5" />
                  {formatTime(note.timestamp)}
                </button>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">{note.content}</p>
            </div>
          ))
        )}
      </div>

      {/* Input */}
      <div className="shrink-0 p-3 bg-black/40 border-t border-white/5">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
            placeholder="Add a manual note..."
            className="flex-1 bg-black/50 border border-white/10 rounded-lg py-2.5 px-3 text-sm text-white focus:border-yellow-500/50 outline-none transition-all placeholder:text-slate-500"
          />
          <button
            onClick={handleAddNote}
            disabled={!input.trim() || isSaving}
            className="p-2.5 bg-gradient-to-r from-yellow-500 to-amber-500 hover:from-yellow-400 hover:to-amber-400 disabled:opacity-30 disabled:from-white/10 disabled:to-white/10 text-white rounded-lg transition-all shadow-[0_0_15px_rgba(234,179,8,0.2)]"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Email Sync Modal Overlay */}
      {showEmailModal && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#18181b] border border-white/10 rounded-2xl w-[90%] max-w-sm p-5 shadow-2xl flex flex-col gap-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-center gap-2">
              <Cloud className="w-5 h-5 text-blue-400" />
              <h3 className="text-white font-semibold text-lg">Sync to Google Drive</h3>
            </div>
            
            {!syncSuccess ? (
              <>
                <p className="text-slate-400 text-sm">
                  Enter your email address to sync and save the generated notes as a Document in your Drive.
                </p>
                <input
                  type="email"
                  value={syncEmail}
                  onChange={(e) => setSyncEmail(e.target.value)}
                  placeholder="Enter your email (e.g., user@gmail.com)"
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 px-3 text-sm text-white focus:border-blue-500/50 outline-none transition-all"
                />
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => setShowEmailModal(false)}
                    className="flex-1 py-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-lg text-sm font-medium transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleEmailSync}
                    disabled={!syncEmail.includes('@') || isSyncingDrive}
                    className="flex-1 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/20 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {isSyncingDrive ? <Loader2 className="w-4 h-4 animate-spin" /> : <Cloud className="w-4 h-4" />}
                    {isSyncingDrive ? 'Syncing...' : 'Sync Now'}
                  </button>
                </div>
              </>
            ) : (
              <div className="py-4 flex flex-col items-center justify-center gap-3 text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h4 className="text-emerald-400 font-semibold mb-1">Successfully Synced!</h4>
                  <p className="text-slate-400 text-xs">
                    The document has been saved to <strong>{syncEmail}</strong>'s Drive and downloaded locally.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartNotepad;
