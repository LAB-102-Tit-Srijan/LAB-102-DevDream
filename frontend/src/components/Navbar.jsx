import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles } from 'lucide-react';

const Navbar = () => {
  const { user } = useAuth();

  return (
    <nav className="h-20 flex items-center justify-between px-8 sticky top-0 z-50 bg-[#09090b]/80 backdrop-blur-md border-b border-white/5">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-[0_0_15px_rgba(249,115,22,0.5)] group-hover:shadow-[0_0_25px_rgba(249,115,22,0.6)] transition-all duration-300">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <span className="text-xl font-semibold tracking-tight text-foreground">
          AILearn
        </span>
      </Link>

      {/* Center Links */}
      {!user && (
        <div className="hidden md:flex items-center gap-8">
          {['Home', 'Features', 'AI Assistant', 'Dashboard', 'Pricing', 'Contact'].map((item) => (
            <Link
              key={item}
              to={`/${item.toLowerCase().replace(' ', '-')}`}
              className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
            >
              {item}
            </Link>
          ))}
        </div>
      )}

      {/* Right Actions */}
      <div className="flex items-center gap-6">
        {user ? (
          <>
            <Link to="/dashboard" className="text-sm font-medium text-white bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full border border-white/10 transition-colors">
              Dashboard
            </Link>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-sm shadow-[0_0_10px_rgba(249,115,22,0.3)]">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
          </>
        ) : (
          <>
            <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Login
            </Link>
            <Link
              to="/signup"
              className="px-6 py-2.5 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 text-white text-sm font-medium hover:from-primary-400 hover:to-primary-500 shadow-[0_0_15px_rgba(249,115,22,0.4)] hover:shadow-[0_0_25px_rgba(249,115,22,0.6)] transition-all duration-300"
            >
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
