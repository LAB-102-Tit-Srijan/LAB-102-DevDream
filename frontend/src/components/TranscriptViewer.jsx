import { Clock, Search, Loader2, PlayCircle } from 'lucide-react';
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
    <div className="flex flex-col h-full overflow-hidden">
      {/* Search Bar */}
      {transcriptData.length > 0 && (
        <div className="shrink-0 px-3 py-2 border-b border-white/5">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search in transcript..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-black/40 border border-white/5 rounded-xl py-3 pl-9 pr-4 text-sm text-slate-300 outline-none focus:border-primary-500/50 transition-all shadow-inner"
            />
          </div>
        </div>
      )}

      {/* Transcript Grid */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
      >
        {!videoId ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 opacity-50">
            <Clock className="w-8 h-8" />
            <p className="text-sm">Upload a video to see timestamps</p>
          </div>
        ) : transcriptData.length > 0 ? (
          filteredTranscript.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredTranscript.map((item, index) => (
                <button
                  key={index}
                  title="Jump to this moment"
                  onClick={() => {
                    setActiveIndex(index);
                    onTimestampClick(item.start);
                  }}
                  className={`w-full text-left p-4 rounded-xl border transition-all flex flex-col gap-2 ${
                    activeIndex === index
                      ? 'bg-primary-500/10 border-primary-500/30 shadow-[inset_0_2px_10px_rgba(249,115,22,0.1)]'
                      : 'bg-white/[0.02] border-white/5 hover:border-white/20 hover:bg-white/[0.04]'
                  }`}
                >
                  <div className={`flex items-center gap-2 text-xs font-mono font-medium ${
                    activeIndex === index ? 'text-primary-400' : 'text-slate-400'
                  }`}>
                    <Clock className="w-3.5 h-3.5" />
                    {item.time || item.start}
                  </div>
                  <p className={`text-sm line-clamp-3 leading-relaxed ${
                    activeIndex === index ? 'text-white' : 'text-slate-300'
                  }`}>
                    {item.text}
                  </p>
                </button>
              ))}
            </div>
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

      {/* Status Footer */}
      <div className="shrink-0 px-3 py-2 bg-black/40 border-t border-white/5 flex items-center justify-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'transcribed' ? 'bg-emerald-500' :
          status === 'failed' ? 'bg-red-500' :
          'bg-amber-500 animate-pulse'
        }`} />
        <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">
          {status === 'transcribed' ? 'Click to jump' : 'Processing...'}
        </p>
      </div>
    </div>
  );
};

export default TranscriptViewer;
