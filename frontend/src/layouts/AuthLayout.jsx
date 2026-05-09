import { Outlet } from 'react-router-dom'
import { BrainCircuit } from 'lucide-react'

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col md:flex-row">
      {/* Left Side - Hero Section */}
      <div className="hidden md:flex flex-1 bg-primary-600 relative overflow-hidden items-center justify-center p-12">
        <div className="absolute inset-0 bg-slate-950/20"></div>
        <div className="relative z-10 text-center max-w-lg">
          <div className="w-20 h-20 bg-white/10 backdrop-blur-xl rounded-3xl flex items-center justify-center mx-auto mb-8 border border-white/20">
            <BrainCircuit className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-6 leading-tight">
            Personalized AI-Powered Learning for Everyone
          </h1>
          <p className="text-primary-100 text-lg">
            Master new skills with our intelligent companion that adapts to your learning pace and style.
          </p>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-400/30 blur-[100px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-slate-950/40 blur-[100px] rounded-full"></div>
      </div>

      {/* Right Side - Form Section */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12">
        <div className="w-full max-w-md">
          <div className="md:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
              <BrainCircuit className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">AI LMS</span>
          </div>
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
