import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-[#171717] flex items-center justify-center p-6 selection:bg-primary-500/30">
      {/* Background Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-900/10 blur-[120px] rounded-full"></div>
      </div>

      <div className="w-full max-w-[400px] relative z-10">
        <Outlet />
      </div>
    </div>
  );
};

export default AuthLayout;
