import { Send, User, Bot, Sparkles, Loader2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const AIChatInterface = ({ videoData }) => {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      type: 'ai', 
      content: "Hello! I'm your StudyAI assistant. I've analyzed the video. How can I help you master this topic today?",
      suggestions: ["Summarize the video", "Explain the key concepts", "Create a quiz"]
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

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

      // Build conversation history from last 6 messages (3 turns)
      // Filter out the initial greeting (which has 'suggestions') and map to Groq format
      const history = messages
        .filter(m => !m.suggestions)  // exclude the initial AI greeting message
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
    <div className="flex flex-col h-[calc(100vh-12rem)] bg-slate-900/50 border border-white/5 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-sm">
      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent"
      >
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
              msg.type === 'user' ? 'bg-primary-600' : 'bg-slate-800 border border-white/10'
            }`}>
              {msg.type === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-primary-400" />}
            </div>
            
            <div className={`space-y-3 max-w-[85%] ${msg.type === 'user' ? 'items-end' : ''}`}>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.type === 'user' 
                  ? 'bg-primary-600 text-white rounded-tr-none' 
                  : 'bg-slate-800/50 text-slate-200 border border-white/5 rounded-tl-none'
              }`}>
                {msg.content}
              </div>

              {msg.suggestions && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.suggestions.map((s) => (
                    <button 
                      key={s}
                      onClick={() => handleSend(s)}
                      className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-white/5 rounded-full transition-all"
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
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-white/10 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-primary-400" />
            </div>
            <div className="bg-slate-800/50 border border-white/5 p-4 rounded-2xl rounded-tl-none">
              <Loader2 className="w-4 h-4 animate-spin text-slate-500" />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-slate-950/50 border-t border-white/5">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
          className="relative flex items-center"
        >
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            placeholder={isTyping ? "Waiting for response..." : "Ask anything about the video..."}
            className="w-full bg-slate-900 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:ring-2 focus:ring-primary-500 outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isTyping}
            className="absolute right-2 p-1.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:bg-slate-800 text-white rounded-lg transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-600 mt-2">
          StudyAI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
};

export default AIChatInterface;
