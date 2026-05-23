import { NavLink } from 'react-router-dom';
import type { NavTab } from '../../types';

const NAV_ITEMS: { tab: NavTab; label: string; icon: string; path: string }[] = [
  { tab: 'dashboard',   label: 'Dashboard',         icon: '📊', path: '/' },
  { tab: 'settings',    label: '项目配置',            icon: '⚙️', path: '/settings' },
  { tab: 'generator',   label: '素材生成',            icon: '✨', path: '/generator' },
  { tab: 'spritesheet', label: 'Sprite Sheet',       icon: '🎞️', path: '/spritesheet' },
  { tab: 'tile',        label: 'Tile 预览',           icon: '🧱', path: '/tile' },
  { tab: 'export',      label: '导出',                icon: '📦', path: '/export' },
];

export default function Sidebar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
      isActive
        ? 'bg-brand-600/20 text-brand-300 border border-brand-700/50'
        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
    }`;

  return (
    <nav className="w-56 border-r border-gray-800 bg-gray-950/80 flex flex-col gap-1 p-3 shrink-0">
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-2">
        导航
      </div>
      {NAV_ITEMS.map((item) => (
        <NavLink key={item.tab} to={item.path} end={item.path === '/'} className={linkClass}>
          <span className="text-base w-5 text-center">{item.icon}</span>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
