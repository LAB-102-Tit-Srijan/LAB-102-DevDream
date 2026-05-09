import { Clock, Search, ChevronRight, Loader2 } from 'lucide-react';
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
    <div className="flex flex-col h-full bg-[#212121] border border-white/5 rounded-[24px] overflow-hidden shadow-2xl transition-all">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-slate-200">Transcript</span>
        </div>
        <div className="relative group">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
          <input 
            type="text" 
            placeholder="Search transcript..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-black/20 border border-white/5 rounded-full py-1.5 pl-8 pr-4 text-xs text-slate-300 outline-none focus:border-primary-500/50 transition-all w-40"
          />
        </div>
      </div>

      {/* Transcript List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
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
                onClick={() => {
                  setActiveIndex(index);
                  onTimestampClick(item.start);
                }}
                className={`w-full text-left p-3 rounded-xl transition-all group flex gap-4 ${
                  activeIndex === index 
                    ? 'bg-primary-500/10 border border-primary-500/20' 
                    : 'hover:bg-white/5 border border-transparent'
                }`}
              >
                <span className={`text-[11px] font-mono shrink-0 mt-0.5 ${
                  activeIndex === index ? 'text-primary-400' : 'text-slate-500 group-hover:text-slate-300'
                }`}>
                  [{item.time || item.start}]
                </span>
                <div className="flex-1">
                  <p className={`text-[13px] leading-relaxed ${
                    activeIndex === index ? 'text-slate-100 font-medium' : 'text-slate-400 group-hover:text-slate-300'
                  }`}>
                    {item.text}
                  </p>
                </div>
                <ChevronRight className={`w-4 h-4 shrink-0 self-center transition-transform ${
                  activeIndex === index ? 'text-primary-400 translate-x-1' : 'text-slate-600 opacity-0 group-hover:opacity-100'
                }`} />
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
      <div className="p-3 bg-black/20 border-t border-white/5 flex items-center justify-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'transcribed' ? 'bg-emerald-500' : 
          status === 'failed' ? 'bg-red-500' : 
          'bg-amber-500 animate-pulse'
        }`} />
        <p className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">
          {status === 'transcribed' ? 'AI Generated • Ready' : 'AI Processing...'}
        </p>
      </div>
    </div>
  );
};

export default TranscriptViewer;
