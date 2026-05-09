import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user } = useAuth();

  return (
    <nav className="h-12 flex items-center justify-center px-6 sticky top-0 z-40 bg-transparent">
      <div className="flex items-center gap-1.5 bg-[#212121] px-3 py-1 rounded-full border border-white/5">
        <span className="text-[11px] text-slate-400">Free plan</span>
        <span className="text-[11px] text-slate-500">·</span>
        <button className="text-[11px] text-slate-200 hover:text-white transition-colors underline underline-offset-2">
          Upgrade
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
