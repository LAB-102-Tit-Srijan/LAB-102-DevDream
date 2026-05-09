import { Plus, Mic2 } from 'lucide-react';
import { useRef } from 'react';

const ChatInput = ({ onFileUpload, onSendMessage, isLoading }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('video/')) {
      onFileUpload(file);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-[#212121] border border-white/5 rounded-[24px] p-4 shadow-2xl transition-all focus-within:border-white/10">
        <textarea 
          placeholder="How can I help you today?"
          className="w-full bg-transparent border-none outline-none text-[16px] text-slate-200 placeholder:text-slate-500 resize-none min-h-[60px] px-2 pt-1"
          rows={1}
        />
        
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-2">
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="video/*"
              className="hidden"
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-slate-400 hover:text-slate-200 hover:bg-white/5 rounded-full transition-all"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-white/5 rounded-full transition-all">
              <Mic2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
