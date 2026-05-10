import { Link } from 'react-router-dom';
import { Play, Sparkles, MessageSquare, FileText, Clock, Users, Zap, TrendingUp } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="flex flex-col min-h-screen bg-[#09090b] bg-grid-pattern bg-[length:40px_40px] overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[400px] bg-primary-500/20 blur-[120px] rounded-full pointer-events-none" />
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 flex flex-col items-center justify-center text-center z-10">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-8">
          <Sparkles className="w-4 h-4" />
          Powered by Advanced AI Technology
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white max-w-4xl leading-tight mb-8">
          Transform Every Lecture <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
            Into An AI-Powered
          </span> <br className="hidden md:block" />
          Learning Experience
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-12">
          An intelligent LMS companion that helps students ask questions directly from
          lectures, generate contextual summaries, jump to concepts instantly, and learn
          smarter using AI.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <Link 
            to="/dashboard"
            className="group px-8 py-4 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 text-white text-lg font-medium hover:from-primary-400 hover:to-primary-500 shadow-[0_0_20px_rgba(249,115,22,0.4)] hover:shadow-[0_0_35px_rgba(249,115,22,0.6)] transition-all duration-300 flex items-center gap-2"
          >
            Start Learning
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </Link>
          <button className="px-8 py-4 rounded-full bg-white/5 hover:bg-white/10 text-white text-lg font-medium border border-white/10 transition-colors flex items-center gap-2">
            <Play className="w-5 h-5" />
            Watch Demo
          </button>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 px-6 border-t border-white/5 bg-black/20 backdrop-blur-sm relative z-10">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: Users, label: '1M+ Students' },
            { icon: Zap, label: 'AI-Powered' },
            { icon: MessageSquare, label: 'Instant Answers' },
            { icon: TrendingUp, label: '95% Faster' },
          ].map((stat, i) => (
            <div key={i} className="flex flex-col items-center justify-center p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-primary-500/30 transition-colors group">
              <stat.icon className="w-8 h-8 text-primary-500 mb-3 group-hover:scale-110 transition-transform" />
              <span className="text-sm md:text-base font-medium text-slate-300">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-primary-400 text-sm font-medium mb-6">
              AI Features
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
              Intelligent Learning Tools
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Leverage cutting-edge RAG-based contextual AI to transform your learning experience with 
              powerful features designed specifically for modern students.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: MessageSquare,
                title: 'Contextual Q&A',
                description: 'Ask questions directly from lecture transcripts and get instant, context-aware answers from the AI.'
              },
              {
                icon: FileText,
                title: 'Smart Summaries',
                description: 'Generate intelligent topic-wise summaries or catch up quickly with last 5-minute summaries.'
              },
              {
                icon: Clock,
                title: 'Jump-to-Moment',
                description: 'Clickable timestamps in the interactive transcript allow you to instantly navigate to exact video sections.'
              },
              {
                icon: Zap,
                title: 'Streaming Responses',
                description: 'Experience real-time AI-generated responses with zero latency for a fluid conversation.'
              },
              {
                icon: Sparkles,
                title: 'Session Memory',
                description: 'The AI intelligently retains conversation context within your current session for natural multi-turn discussions.'
              }
            ].map((feature, i) => (
              <div key={i} className="p-8 rounded-3xl bg-black/40 border border-white/5 hover:border-primary-500/50 hover:bg-black/60 transition-all duration-300 group hover:-translate-y-1">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-6 shadow-lg shadow-primary-500/20 group-hover:shadow-primary-500/40 transition-shadow">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="py-24 px-6 relative z-10 bg-gradient-to-b from-transparent to-black/50 border-t border-white/5">
        <div className="max-w-6xl mx-auto text-center">
           <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-primary-400 text-sm font-medium mb-6">
              Our Impact
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-16 tracking-tight">
              Transforming Education Globally
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
               {[
                 { value: '10,00,000+', label: 'Students' },
                 { value: '10,000+', label: 'Lectures Processed' },
                 { value: '50,000+', label: 'AI Questions Answered' },
                 { value: '95%', label: 'Faster Revision', highlight: true }
               ].map((stat, i) => (
                 <div key={i} className="p-8 rounded-2xl bg-black/40 border border-white/5 hover:border-white/10 transition-colors">
                   <div className={`text-4xl md:text-5xl font-bold mb-2 ${stat.highlight ? 'text-primary-500' : 'text-primary-500'}`}>
                     {stat.value}
                   </div>
                   <div className="text-slate-400 font-medium">
                     {stat.label}
                   </div>
                 </div>
               ))}
            </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
