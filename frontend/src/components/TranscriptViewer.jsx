import { Clock, Search, ChevronRight, Loader2, PlayCircle } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import api from '../services/api';

const TranscriptViewer = ({ videoId, onTimestampClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const [transcriptData, setTranscriptData] = useState([]);
  const [status, setStatus] = useState('');
  const [elapsed, setElapsed] = useState(0);
  const scrollRef = useRef(null);
  const intervalRef = useRef(null);
  const timerRef = useRef(null);
  const statusRef = useRef(status);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    if (!videoId) return;

    setTranscriptData([]);
    setStatus('uploaded');
    setElapsed(0);

    // Timer for user feedback
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);

    const fetchTranscript = async () => {
      try {
        const response = await api.get(`/api/videos/${videoId}/transcript`);
        const newStatus = response.data.status;

        if (newStatus === 'transcribed') {
          setTranscriptData(response.data.transcript_data || []);
          if (intervalRef.current) clearInterval(intervalRef.current);
          if (timerRef.current) clearInterval(timerRef.current);
        } else if (newStatus === 'failed' || newStatus === 'error') {
          if (intervalRef.current) clearInterval(intervalRef.current);
          if (timerRef.current) clearInterval(timerRef.current);
        }
        setStatus(newStatus);
      } catch (err) {
        console.error('Failed to fetch transcript:', err);
      }
    };

    fetchTranscript();

    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      const currentStatus = statusRef.current;
      if (currentStatus !== 'transcribed' && currentStatus !== 'failed' && currentStatus !== 'error') {
        fetchTranscript();
      }
    }, 3000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [videoId]);

  const formatElapsed = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  const filteredTranscript = transcriptData.filter(item => 
    item.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full overflow-hidden transition-all">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-slate-200">Interactive Transcript</span>
        </div>
        <div className="relative group">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
          <input 
            type="text" 
            placeholder="Search transcript..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-black/40 border border-white/5 rounded-full py-1.5 pl-8 pr-4 text-xs text-slate-300 outline-none focus:border-primary-500/50 transition-all w-40"
          />
        </div>
      </div>

      {/* Transcript List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent relative"
      >
        {!videoId ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 opacity-50">
            <Clock className="w-8 h-8" />
            <p className="text-sm">Upload a video to see transcript</p>
          </div>
        ) : transcriptData.length > 0 ? (
          filteredTranscript.length > 0 ? (
            filteredTranscript.map((item, index) => (
              <button
                key={index}
                title="Jump to this moment"
                onClick={() => {
                  setActiveIndex(index);
                  onTimestampClick(item.start);
                }}
                className={`w-full text-left p-3 rounded-xl transition-all group flex gap-3 ${
                  activeIndex === index 
                    ? 'bg-gradient-to-r from-primary-500/10 to-transparent border border-primary-500/20 shadow-[inset_2px_0_0_0_rgba(249,115,22,1)]' 
                    : 'hover:bg-white/5 border border-transparent hover:shadow-[inset_2px_0_0_0_rgba(255,255,255,0.1)]'
                }`}
              >
                <div className={`flex flex-col items-center justify-center w-14 shrink-0 ${
                  activeIndex === index ? 'text-primary-400' : 'text-slate-500 group-hover:text-primary-300'
                }`}>
                  <span className="text-[13px] font-mono mt-0.5 group-hover:hidden">
                    {item.time || item.start}
                  </span>
                  <PlayCircle className="w-5 h-5 hidden group-hover:block" />
                </div>
                
                <div className="flex-1 border-l border-white/5 pl-3">
                  <p className={`text-[15px] leading-relaxed ${
                    activeIndex === index ? 'text-slate-100 font-medium' : 'text-slate-400 group-hover:text-slate-200'
                  }`}>
                    {item.text}
                  </p>
                </div>
              </button>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2 opacity-50">
              <Search className="w-8 h-8" />
              <p className="text-sm">No matches found</p>
            </div>
          )
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
            <Loader2 className="w-8 h-8 animate-spin text-primary-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-slate-400">AI is transcribing...</p>
              <p className="text-[11px] text-slate-500 mt-1 font-mono">Elapsed: {formatElapsed(elapsed)}</p>
            </div>
            <p className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">
              Status: {status}
            </p>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 bg-black/40 border-t border-white/5 flex items-center justify-center gap-2 backdrop-blur-md">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'transcribed' ? 'bg-emerald-500' : 
          status === 'failed' ? 'bg-red-500' : 
          'bg-amber-500 animate-pulse'
        }`} />
        <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
          {status === 'transcribed' ? 'AI Generated • Click to Navigate' : 'AI Processing...'}
        </p>
      </div>
    </div>
  );
};

export default TranscriptViewer;
