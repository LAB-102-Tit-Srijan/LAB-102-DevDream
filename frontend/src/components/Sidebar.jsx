import { Plus, Search, MessageSquare, Box, LayoutGrid, Code, ShoppingBag, Download, User } from 'lucide-react';

const Sidebar = () => {
  const topIcons = [
    { icon: Plus, label: 'New' },
    { icon: Search, label: 'Search' },
    { icon: MessageSquare, label: 'Chat' },
    { icon: Box, label: 'Vault' },
    { icon: LayoutGrid, label: 'Apps' },
    { icon: Code, label: 'Code' },
    { icon: ShoppingBag, label: 'Shop' },
  ];

  return (
    <aside className="w-[60px] h-screen bg-[#171717] border-r border-white/5 flex flex-col items-center py-4 fixed left-0 top-0 z-50">
      <div className="flex-1 flex flex-col gap-4">
        {topIcons.map((item, i) => (
          <button 
            key={i} 
            className="p-2 text-slate-500 hover:text-slate-200 hover:bg-white/5 rounded-lg transition-all"
            title={item.label}
          >
            <item.icon className="w-5 h-5" />
          </button>
        ))}
      </div>
      
      <div className="flex flex-col gap-4 mt-auto">
        <button className="p-2 text-slate-500 hover:text-slate-200 hover:bg-white/5 rounded-lg transition-all">
          <Download className="w-5 h-5" />
        </button>
        <div className="w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center text-[10px] font-bold text-slate-400 border border-white/10 cursor-pointer hover:border-slate-500 transition-all">
          AD
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
