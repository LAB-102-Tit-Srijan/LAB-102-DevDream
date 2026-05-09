import { Upload, Link as LinkIcon, Youtube, FileVideo } from 'lucide-react';

const UploadSection = ({ onSourceSelect }) => {
  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-in fade-in zoom-in duration-700">
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
          What do you want to <span className="text-primary-500">learn</span> today?
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          Import a video or document, and let StudyAI guide you through the learning process.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button 
          onClick={() => onSourceSelect({ type: 'youtube' })}
          className="group p-6 bg-slate-900/50 border border-white/5 rounded-2xl hover:border-primary-500/50 hover:bg-primary-500/5 transition-all text-left space-y-4"
        >
          <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
            <Youtube className="w-6 h-6 text-red-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">YouTube Link</h3>
            <p className="text-sm text-slate-400">Paste a URL to start learning from any video.</p>
          </div>
        </button>

        <button 
          onClick={() => onSourceSelect({ type: 'upload' })}
          className="group p-6 bg-slate-900/50 border border-white/5 rounded-2xl hover:border-primary-500/50 hover:bg-primary-500/5 transition-all text-left space-y-4"
        >
          <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
            <FileVideo className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Upload Video</h3>
            <p className="text-sm text-slate-400">Upload MP4 or MKV files from your device.</p>
          </div>
        </button>
      </div>

      <div className="relative group">
        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
          <LinkIcon className="w-5 h-5 text-slate-500 group-focus-within:text-primary-500 transition-colors" />
        </div>
        <input 
          type="text" 
          placeholder="Paste YouTube or Video URL here..."
          className="w-full bg-slate-900/80 border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all placeholder:text-slate-600 shadow-2xl"
          onKeyDown={(e) => {
            if (e.key === 'Enter') onSourceSelect({ type: 'youtube', url: e.target.value });
          }}
        />
      </div>
    </div>
  );
};

export default UploadSection;
