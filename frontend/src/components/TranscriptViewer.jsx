import { Clock, Search, ChevronRight } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const TranscriptViewer = ({ onTimestampClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const scrollRef = useRef(null);

  const transcriptData = [
    { time: '00:00', text: "Welcome to this deep dive into React performance optimization and advanced patterns." },
    { time: '00:45', text: "Overfitting occurs when a model learns the detail and noise in the training data to an extent that it negatively impacts the performance of the model on new data." },
    { time: '01:20', text: "Underfitting means that the model cannot provide a good fit to the training data nor generalize to new data." },
    { time: '02:15', text: "Now let's look at how we can use useMemo and useCallback to prevent unnecessary re-renders in our components." },
    { time: '03:40', text: "Context API is great, but overusing it can lead to performance bottlenecks if not handled with care." },
    { time: '05:10', text: "The reconciliation process is at the heart of React's efficiency. Let's break down how the virtual DOM works." },
    { time: '07:30', text: "In conclusion, mastering these patterns will make you a much more effective frontend engineer." },
  ];

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
        {filteredTranscript.length > 0 ? (
          filteredTranscript.map((item, index) => (
            <button
              key={index}
              onClick={() => {
                setActiveIndex(index);
                onTimestampClick(item.time);
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
                [{item.time}]
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
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 bg-black/20 border-t border-white/5 text-center">
        <p className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">
          AI Generated Transcription
        </p>
      </div>
    </div>
  );
};

export default TranscriptViewer;
