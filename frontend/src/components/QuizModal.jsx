import { useState, useEffect } from 'react';
import { X, Trophy, CheckCircle2, XCircle, Loader2, BrainCircuit, RotateCcw } from 'lucide-react';
import api from '../services/api';

const QuizModal = ({ videoId, isOpen, onClose }) => {
  const [questions, setQuestions] = useState([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [selected, setSelected] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && videoId) {
      fetchQuiz();
    }
  }, [isOpen, videoId]);

  const fetchQuiz = async () => {
    setIsLoading(true);
    setError('');
    setScore(0);
    setCurrentQ(0);
    setSelected(null);
    setShowResult(false);
    setIsFinished(false);
    try {
      const res = await api.get(`/api/videos/${videoId}/quiz`);
      if (res.data.status && res.data.data.questions.length > 0) {
        setQuestions(res.data.data.questions);
      } else {
        setError('Could not generate quiz. Please try again.');
      }
    } catch (err) {
      console.error('Quiz fetch failed:', err);
      setError('Failed to generate quiz. The AI may be temporarily unavailable.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionClick = (index) => {
    if (showResult) return;
    setSelected(index);
    setShowResult(true);
    if (index === questions[currentQ]?.correct_index) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentQ + 1 >= questions.length) {
      setIsFinished(true);
    } else {
      setCurrentQ(prev => prev + 1);
      setSelected(null);
      setShowResult(false);
    }
  };

  if (!isOpen) return null;

  const q = questions[currentQ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-[#111318] border border-white/10 rounded-[28px] w-full max-w-lg mx-4 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        {/* Header */}
        <div className="p-5 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-purple-500/10 to-blue-500/10">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-purple-400" />
            <span className="text-lg font-semibold text-white">AI Quiz</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-xl transition-colors text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 min-h-[300px] flex flex-col justify-center">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center gap-4">
              <Loader2 className="w-10 h-10 animate-spin text-purple-400" />
              <p className="text-slate-400 text-sm animate-pulse">AI is generating your quiz...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center gap-4">
              <XCircle className="w-10 h-10 text-red-400" />
              <p className="text-slate-400 text-sm text-center">{error}</p>
              <button
                onClick={fetchQuiz}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-300 rounded-xl hover:bg-purple-500/30 transition-colors text-sm"
              >
                <RotateCcw className="w-4 h-4" /> Retry
              </button>
            </div>
          ) : isFinished ? (
            <div className="flex flex-col items-center justify-center gap-5 py-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center shadow-[0_0_30px_rgba(234,179,8,0.4)]">
                <Trophy className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white">Quiz Complete!</h3>
              <div className="text-center">
                <p className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                  {score} / {questions.length}
                </p>
                <p className="text-slate-400 text-sm mt-2">
                  {score === questions.length ? '🎉 Perfect Score!' : score >= 2 ? '👏 Great job!' : '📚 Keep studying!'}
                </p>
              </div>
              <div className="flex gap-3 mt-2">
                <button
                  onClick={fetchQuiz}
                  className="flex items-center gap-2 px-5 py-2.5 bg-purple-500/20 text-purple-300 rounded-xl hover:bg-purple-500/30 transition-colors text-sm font-medium"
                >
                  <RotateCcw className="w-4 h-4" /> Try Again
                </button>
                <button
                  onClick={onClose}
                  className="px-5 py-2.5 bg-white/5 text-slate-300 rounded-xl hover:bg-white/10 transition-colors text-sm font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          ) : q ? (
            <div className="space-y-5">
              {/* Progress */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">
                  Question <span className="text-white font-semibold">{currentQ + 1}</span> of {questions.length}
                </span>
                <span className="text-purple-400 font-medium">Score: {score}</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                  style={{ width: `${((currentQ + 1) / questions.length) * 100}%` }}
                />
              </div>

              {/* Question */}
              <h3 className="text-lg font-semibold text-white leading-relaxed">{q.question}</h3>

              {/* Options */}
              <div className="space-y-3">
                {q.options.map((opt, i) => {
                  let optClass = 'bg-white/5 border-white/5 hover:border-purple-500/50 hover:bg-white/10 text-slate-300';
                  if (showResult) {
                    if (i === q.correct_index) {
                      optClass = 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300';
                    } else if (i === selected && i !== q.correct_index) {
                      optClass = 'bg-red-500/15 border-red-500/40 text-red-300';
                    } else {
                      optClass = 'bg-white/5 border-white/5 text-slate-500 opacity-50';
                    }
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => handleOptionClick(i)}
                      disabled={showResult}
                      className={`w-full text-left p-4 rounded-xl border transition-all text-sm font-medium flex items-center gap-3 ${optClass}`}
                    >
                      <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold shrink-0">
                        {String.fromCharCode(65 + i)}
                      </span>
                      {opt}
                      {showResult && i === q.correct_index && <CheckCircle2 className="w-5 h-5 ml-auto text-emerald-400" />}
                      {showResult && i === selected && i !== q.correct_index && <XCircle className="w-5 h-5 ml-auto text-red-400" />}
                    </button>
                  );
                })}
              </div>

              {/* Next Button */}
              {showResult && (
                <button
                  onClick={handleNext}
                  className="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-400 hover:to-blue-400 text-white rounded-xl font-medium transition-all shadow-[0_0_15px_rgba(147,51,234,0.3)] mt-2"
                >
                  {currentQ + 1 >= questions.length ? 'See Results' : 'Next Question →'}
                </button>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default QuizModal;
