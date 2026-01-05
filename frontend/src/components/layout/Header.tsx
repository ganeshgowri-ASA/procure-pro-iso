import { Menu, Bell, Search, ChevronDown } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
  title: string;
  subtitle?: string;
}

export default function Header({ onMenuClick, title, subtitle }: HeaderProps) {
  return (
    <header className="bg-gradient-header h-16 px-4 flex items-center justify-between shadow-md">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden text-white/90 hover:text-white p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          <Menu size={24} />
        </button>
        <div>
          <h1 className="text-white font-semibold text-lg">{title}</h1>
          {subtitle && (
            <p className="text-white/70 text-sm">{subtitle}</p>
          )}
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="hidden md:flex items-center bg-white/10 rounded-lg px-3 py-2 w-64">
          <Search size={18} className="text-white/60" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent border-none outline-none text-white placeholder-white/60 ml-2 w-full text-sm"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-white/90 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User dropdown */}
        <button className="hidden md:flex items-center gap-2 px-3 py-2 text-white/90 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">JD</span>
          </div>
          <span className="text-sm font-medium">John Doe</span>
          <ChevronDown size={16} />
        </button>
      </div>
    </header>
  );
}
