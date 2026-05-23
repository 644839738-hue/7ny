import { DEMO_MODE } from '../../config/demo';

export default function Header() {
  return (
    <header className="h-14 border-b border-gray-800 bg-gray-950 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-xl">🎮</span>
        <h1 className="text-lg font-bold tracking-tight">
          SpriteForge <span className="text-brand-400">AI</span>
        </h1>
      </div>

      <div className="flex items-center gap-4 text-sm">
        {DEMO_MODE && (
          <span className="bg-amber-900/60 text-amber-300 border border-amber-700
                           px-3 py-0.5 rounded-full text-xs font-medium">
            DEMO 模式
          </span>
        )}
        <span className="text-gray-500">v0.0.1</span>
      </div>
    </header>
  );
}
