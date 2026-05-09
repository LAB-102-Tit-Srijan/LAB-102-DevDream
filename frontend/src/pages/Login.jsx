import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import authService from '../services/authService';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const data = await authService.login(formData.email, formData.password);
      login(data.session.user, data.session.access_token);
      navigate('/');
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-serif text-[#D1D1D1]">Welcome Back</h2>
        <p className="text-slate-500 text-sm">Please enter your details to sign in.</p>
      </div>

      {error && (
        <div className="bg-red-500/5 border border-red-500/10 text-red-400/80 p-3 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-1.5">
          <div className="relative group">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600 group-focus-within:text-primary-500 transition-colors" />
            <input
              required
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Email address"
              className="w-full bg-[#212121] border border-white/5 rounded-2xl py-3.5 pl-11 pr-4 text-[15px] text-slate-200 outline-none focus:border-white/10 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="relative group">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600 group-focus-within:text-primary-500 transition-colors" />
            <input
              required
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Password"
              className="w-full bg-[#212121] border border-white/5 rounded-2xl py-3.5 pl-11 pr-4 text-[15px] text-slate-200 outline-none focus:border-white/10 transition-all placeholder:text-slate-600"
            />
          </div>
          <div className="flex justify-end px-1">
            <a href="#" className="text-[12px] text-slate-500 hover:text-slate-300 transition-colors">Forgot password?</a>
          </div>
        </div>

        <button 
          type="submit"
          disabled={isLoading}
          className="w-full bg-[#D1D1D1] hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-semibold py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2 group mt-2"
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
          {!isLoading && <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />}
        </button>
      </form>

      <div className="text-center">
        <p className="text-slate-500 text-sm">
          Don't have an account?{' '}
          <Link to="/signup" className="text-slate-300 font-medium hover:text-white transition-colors">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
