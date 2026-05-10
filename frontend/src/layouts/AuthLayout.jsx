import { Outlet, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-[#09090b] bg-grid-pattern bg-[length:40px_40px] flex flex-col text-[#fafafa] selection:bg-primary-500/30">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6 relative">
        {/* Background Gradients */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-3xl h-[400px] bg-primary-500/10 blur-[120px] rounded-full"></div>
        </div>

        <div className="w-full max-w-[420px] relative z-10">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
