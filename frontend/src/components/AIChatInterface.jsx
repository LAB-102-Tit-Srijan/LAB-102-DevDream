import { Send, User, Bot, Sparkles, Loader2, FileText, Clock, Zap } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const AIChatInterface = ({ videoData }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (videoData && messages.length === 0) {
      setMessages([
        { 
          id: 1, 
          type: 'ai', 
          content: `Hello! I've successfully analyzed your video "${videoData.name}". I am ready to answer any questions or generate summaries based on its content.`,
          suggestions: [
            "What are the main concepts discussed?", 
            "Generate a 5-point summary", 
            "Are there any definitions I should remember?"
          ]
        }
      ]);
    }
  }, [videoData]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (content) => {
    if (!content.trim() || isTyping) return;

    const userMsg = { id: Date.now(), type: 'user', content };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      if (!videoData?.id) throw new Error("Video ID not found. Please ensure video is uploaded.");

      const history = messages
        .filter(m => !m.suggestions)
        .slice(-6)
        .map(m => ({
          role: m.type === 'user' ? 'user' : 'assistant',
          content: m.content
        }));

      const { default: api } = await import('../services/api');
      const response = await api.post(`/api/videos/${videoData.id}/ask`, {
        question: content,
        history,
      });

      const aiMsg = { 
        id: Date.now() + 1, 
        type: 'ai', 
        content: response.data.data.answer
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      const errMsg = { 
        id: Date.now() + 1, 
        type: 'ai', 
        content: err.response?.data?.detail || "Sorry, I couldn't process your request right now."
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Context Header */}
      <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-slate-200">AI Companion</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-black/40 px-3 py-1 rounded-full border border-white/5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          Context Active
        </div>
      </div>

      {/* Quick Actions (Smart Summaries) */}
      <div className="p-3 border-b border-white/5 bg-black/20 flex flex-wrap gap-2">
        <button 
          onClick={() => handleSend("Generate a topic-wise summary of this lecture.")}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-primary-500/10 hover:bg-primary-500/20 text-primary-300 border border-primary-500/20 rounded-full transition-all"
        >
          <FileText className="w-3 h-3" />
          Topic-wise Summary
        </button>
        <button 
          onClick={() => handleSend("Summarize the last 5 minutes of the video.")}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-primary-500/10 hover:bg-primary-500/20 text-primary-300 border border-primary-500/20 rounded-full transition-all"
        >
          <Clock className="w-3 h-3" />
          Last 5-Min Summary
        </button>
      </div>

      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
      >
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
              msg.type === 'user' ? 'bg-gradient-to-br from-primary-400 to-primary-600 shadow-[0_0_10px_rgba(249,115,22,0.4)]' : 'bg-white/5 border border-white/10'
            }`}>
              {msg.type === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-primary-400" />}
            </div>
            
            <div className={`space-y-3 max-w-[85%] flex flex-col ${msg.type === 'user' ? 'items-end' : ''}`}>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.type === 'user' 
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-tr-none shadow-[0_0_15px_rgba(249,115,22,0.2)]' 
                  : 'bg-white/5 text-slate-200 border border-white/5 rounded-tl-none backdrop-blur-md'
              }`}>
                {msg.content}
              </div>

              {msg.suggestions && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.suggestions.map((s) => (
                    <button 
                      key={s}
                      onClick={() => handleSend(s)}
                      className="text-xs px-3 py-1.5 bg-black/40 hover:bg-white/10 text-slate-300 hover:text-white border border-white/5 hover:border-primary-500/30 rounded-full transition-all"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-4 animate-pulse">
            <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-primary-400" />
            </div>
            <div className="bg-white/5 border border-white/5 p-4 rounded-2xl rounded-tl-none">
              <Loader2 className="w-4 h-4 animate-spin text-slate-500" />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-black/40 border-t border-white/5 backdrop-blur-md">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
          className="relative flex items-center group"
        >
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            placeholder={isTyping ? "Waiting for response..." : "Ask anything about the video..."}
            className="w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:border-primary-500/50 focus:bg-black/60 outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-slate-500"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isTyping}
            className="absolute right-2 p-1.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-400 hover:to-primary-500 disabled:opacity-50 disabled:from-white/10 disabled:to-white/10 text-white rounded-lg transition-all shadow-[0_0_10px_rgba(249,115,22,0.3)] disabled:shadow-none"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-500 mt-3">
          Session context is retained. Answers are grounded in the lecture.
        </p>
      </div>
    </div>
  );
};

export default AIChatInterface;
