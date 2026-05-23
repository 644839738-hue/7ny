import { Link } from 'react-router-dom';
import { DEMO_MODE } from '../config/demo';

const QUICK_LINKS = [
  { to: '/generator',   label: '素材生成',  desc: '通过文本或参数生成 2D 游戏素材',       icon: '✨' },
  { to: '/spritesheet', label: 'Sprite Sheet', desc: '拼接多帧素材并生成 JSON 元数据',    icon: '🎞️' },
  { to: '/tile',        label: 'Tile 预览',   desc: '3×3 平铺预览与边缘一致性评分',      icon: '🧱' },
  { to: '/export',      label: '导出素材包',   desc: '导出 Unity / Godot 可用 ZIP 包',     icon: '📦' },
];

const PIPELINE_STEPS = [
  { step: 1, label: '输入 Prompt',   desc: '描述你想要的素材' },
  { step: 2, label: 'AI 生成',       desc: '或 DEMO 模式返回样例' },
  { step: 3, label: '自动后处理',     desc: '透明背景、裁剪、标准化' },
  { step: 4, label: '预览 & 检测',   desc: 'Tile 评分、Sheet 预览' },
  { step: 5, label: '引擎导出',      desc: 'Unity / Godot ZIP 包' },
];

export default function Dashboard() {
  return (
    <div className="max-w-4xl mx-auto space-y-10">
      {/* Hero */}
      <section>
        <h2 className="text-2xl font-bold mb-2">欢迎使用 SpriteForge AI</h2>
        <p className="text-gray-400 max-w-xl">
          面向 2D 游戏开发工作流的 AI 素材生成与资产化管线。
          {DEMO_MODE && ' 当前运行在 DEMO 模式，无需外部 API 即可体验完整流程。'}
        </p>
      </section>

      {/* Pipeline overview */}
      <section>
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          处理管线
        </h3>
        <div className="flex items-center gap-2 flex-wrap">
          {PIPELINE_STEPS.map((s, i) => (
            <div key={s.step} className="flex items-center gap-2">
              <div className="card flex items-center gap-3 py-3 px-4">
                <span className="w-7 h-7 rounded-full bg-brand-600/30 text-brand-300
                                 flex items-center justify-center text-xs font-bold">
                  {s.step}
                </span>
                <div>
                  <div className="text-sm font-medium">{s.label}</div>
                  <div className="text-xs text-gray-500">{s.desc}</div>
                </div>
              </div>
              {i < PIPELINE_STEPS.length - 1 && (
                <span className="text-gray-700 text-lg">→</span>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Quick links */}
      <section>
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          快速开始
        </h3>
        <div className="grid grid-cols-2 gap-4">
          {QUICK_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="card hover:border-brand-700/50 hover:bg-gray-900/80
                         transition-colors duration-150 group"
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">{link.icon}</span>
                <div>
                  <div className="font-medium group-hover:text-brand-300 transition-colors">
                    {link.label}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">{link.desc}</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Status */}
      <section className="card">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
          系统状态
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <StatusItem label="运行模式" value={DEMO_MODE ? 'DEMO' : 'AI'} color="amber" />
          <StatusItem label="前端版本" value="v0.0.1" color="gray" />
          <StatusItem label="后端状态" value="待连接" color="gray" />
        </div>
      </section>
    </div>
  );
}

function StatusItem({ label, value, color }: { label: string; value: string; color: string }) {
  const dotColors: Record<string, string> = {
    amber: 'bg-amber-400',
    green: 'bg-green-400',
    gray: 'bg-gray-500',
  };
  return (
    <div className="flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${dotColors[color] || 'bg-gray-500'}`} />
      <span className="text-gray-500">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
