import { Play, Maximize, Settings, Volume2, SkipBack, SkipForward } from 'lucide-react';

const VideoSection = ({ url }) => {
  return (
    <div className="space-y-4 animate-in slide-in-from-left-4 duration-700">
      <div className="aspect-video bg-slate-900 rounded-3xl overflow-hidden relative group border border-white/5 shadow-2xl">
        {/* Placeholder for Video Player */}
        <div className="absolute inset-0 flex items-center justify-center">
          <img 
            src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&auto=format&fit=crop&q=80" 
            className="w-full h-full object-cover opacity-40" 
            alt="Video Thumbnail"
          />
          <button className="absolute w-20 h-20 bg-primary-600 rounded-full flex items-center justify-center shadow-2xl shadow-primary-500/40 hover:scale-110 transition-transform">
            <Play className="w-8 h-8 text-white fill-current ml-1" />
          </button>
        </div>

        {/* Video Controls Overlay (Mockup) */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-slate-950 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="space-y-4">
            <div className="h-1.5 w-full bg-white/20 rounded-full overflow-hidden cursor-pointer">
              <div className="h-full bg-primary-500 w-1/3 rounded-full"></div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <button className="text-white hover:text-primary-400 transition-colors"><SkipBack className="w-5 h-5" /></button>
                <button className="text-white hover:text-primary-400 transition-colors"><Play className="w-6 h-6 fill-current" /></button>
                <button className="text-white hover:text-primary-400 transition-colors"><SkipForward className="w-5 h-5" /></button>
                <div className="flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-white" />
                  <div className="w-20 h-1 bg-white/20 rounded-full"></div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button className="text-white hover:text-primary-400 transition-colors"><Settings className="w-5 h-5" /></button>
                <button className="text-white hover:text-primary-400 transition-colors"><Maximize className="w-5 h-5" /></button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-2">
        <h2 className="text-xl font-bold text-white tracking-tight">Advanced React Patterns & AI Integration</h2>
        <p className="text-slate-400 text-sm mt-1">Uploaded 2 hours ago • 18:24 duration</p>
      </div>
    </div>
  );
};

export default VideoSection;
