import { useState } from 'react';
import { HelpCircle, X, Loader2, Lightbulb } from 'lucide-react';
import api from '../services/api';

const ConfusedButton = ({ videoId, videoRef }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [timeRange, setTimeRange] = useState('');
  const [error, setError] = useState('');

  const handleConfused = async () => {
    if (!videoRef?.current || !videoId) return;

    const currentTime = videoRef.current.currentTime;
    // Optionally pause video while explaining
    videoRef.current.pause();

    setIsOpen(true);
    setIsLoading(true);
    setError('');
    setExplanation('');

    try {
      const res = await api.post(`/api/videos/${videoId}/simplify`, {
        current_time: currentTime,
      });

      if (res.data.status) {
        setExplanation(res.data.data.explanation);
        setTimeRange(res.data.data.timestamp_range);
      } else {
        setError(res.data.message || 'Could not simplify. Try again.');
      }
    } catch (err) {
      console.error('Simplify failed:', err);
      setError('AI simplification failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    // Resume playback
    if (videoRef?.current) {
      videoRef.current.play();
    }
  };

  return (
    <>
      {/* Floating Confused Button */}
      <button
        onClick={handleConfused}
        className="absolute bottom-4 right-4 z-20 flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white text-sm font-medium rounded-full shadow-[0_0_20px_rgba(244,63,94,0.4)] hover:shadow-[0_0_30px_rgba(244,63,94,0.6)] transition-all duration-300 hover:scale-105 active:scale-95"
        title="Click if you're confused about this part"
      >
        <HelpCircle className="w-4 h-4" />
        Confused?
      </button>

      {/* Explanation Overlay/Toast */}
      {isOpen && (
        <div className="absolute inset-0 z-30 flex items-end justify-center p-4">
          <div className="w-full max-w-md bg-[#1a1d23]/95 backdrop-blur-xl border border-white/10 rounded-[20px] shadow-2xl animate-in slide-in-from-bottom-4 fade-in duration-300 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-rose-500/10 to-pink-500/10">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                <span className="text-sm font-semibold text-white">Simple Explanation</span>
                {timeRange && (
                  <span className="text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded-full">
                    {timeRange}
                  </span>
                )}
              </div>
              <button
                onClick={handleClose}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Body */}
            <div className="p-5">
              {isLoading ? (
                <div className="flex items-center justify-center gap-3 py-6">
                  <Loader2 className="w-5 h-5 animate-spin text-rose-400" />
                  <span className="text-sm text-slate-400 animate-pulse">Simplifying for you...</span>
                </div>
              ) : error ? (
                <p className="text-sm text-red-400 text-center py-4">{error}</p>
              ) : (
                <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-line">
                  {explanation}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ConfusedButton;
