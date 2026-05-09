import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';

const MainLayout = () => {
  return (
    <div className="min-h-screen bg-[#171717] text-slate-50 selection:bg-primary-500/30 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-screen ml-[60px]">
        <Navbar />
        <main className="flex-1 flex flex-col">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
