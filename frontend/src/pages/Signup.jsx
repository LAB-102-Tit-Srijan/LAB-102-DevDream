import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Sparkles, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { useState } from 'react';
import authService from '../services/authService';

const Signup = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      await authService.signup(formData.email, formData.password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#0f1115]/90 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl shadow-black animate-in fade-in slide-in-from-bottom-4 duration-700 relative">
      <Link to="/" className="absolute top-6 right-6 p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
        <X className="w-5 h-5" />
      </Link>

      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-[0_0_15px_rgba(249,115,22,0.5)]">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Create Account</h2>
      </div>

      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3 rounded-xl flex items-center gap-3 text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <p>Account created! Redirecting...</p>
        </div>
      )}

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300 ml-1">Full Name</label>
          <div className="relative group">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary-500 transition-colors" />
            <input
              required
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              placeholder="Enter your full name"
              className="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-[15px] text-white outline-none focus:border-primary-500/50 focus:bg-black/60 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300 ml-1">Email</label>
          <div className="relative group">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary-500 transition-colors" />
            <input
              required
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Enter your email"
              className="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-[15px] text-white outline-none focus:border-primary-500/50 focus:bg-black/60 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300 ml-1">Password</label>
          <div className="relative group">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary-500 transition-colors" />
            <input
              required
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Create a password"
              className="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-[15px] text-white outline-none focus:border-primary-500/50 focus:bg-black/60 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        <button 
          type="submit"
          disabled={isLoading || success}
          className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-400 hover:to-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-2xl transition-all shadow-[0_0_15px_rgba(249,115,22,0.3)] hover:shadow-[0_0_25px_rgba(249,115,22,0.5)] mt-2"
        >
          {isLoading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>

      <div className="text-center mt-6">
        <p className="text-slate-400 text-sm">
          Already have an account?{' '}
          <Link to="/login" className="text-white font-medium hover:text-primary-400 transition-colors">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
