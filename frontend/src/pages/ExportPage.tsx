import { useState } from 'react';
import type { EngineType } from '../types';

export default function ExportPage() {
  const [engine, setEngine] = useState<EngineType>('unity');
  const [includeSpritesheet, setIncludeSpritesheet] = useState(true);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeTilePreview, setIncludeTilePreview] = useState(true);

  const handleExport = () => {
    console.log('Export:', { engine, includeSpritesheet, includeMetadata, includeTilePreview });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">导出素材包</h2>

      <section className="card space-y-5">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          导出设置
        </h3>

        {/* Engine selector */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            目标引擎
          </label>
          <div className="flex gap-3">
            {([
              ['unity', 'Unity', 'Assets/Sprites/'],
              ['godot', 'Godot', 'assets/sprites/'],
            ] as [EngineType, string, string][]).map(([key, label, path]) => (
              <button
                key={key}
                onClick={() => setEngine(key)}
                className={`flex-1 p-4 rounded-lg border text-left transition-colors duration-150 ${
                  engine === key
                    ? 'border-brand-500 bg-brand-600/20'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                }`}
              >
                <div className="font-medium text-sm">{label}</div>
                <div className="text-xs text-gray-500 mt-1 font-mono">{path}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Options */}
        <div className="space-y-3">
          <ToggleOption
            label="包含 Sprite Sheet"
            desc="拼接后的 Spritesheet 图 + JSON 帧元数据"
            checked={includeSpritesheet}
            onChange={setIncludeSpritesheet}
          />
          <ToggleOption
            label="包含 JSON 元数据"
            desc="每张素材的生成参数、尺寸、处理记录"
            checked={includeMetadata}
            onChange={setIncludeMetadata}
          />
          <ToggleOption
            label="包含 Tile 平铺预览"
            desc="Tile 素材的 3×3 平铺预览图"
            checked={includeTilePreview}
            onChange={setIncludeTilePreview}
          />
        </div>
      </section>

      {/* Package structure preview */}
      <section className="card">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          导出结构预览
        </h3>
        <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4 text-xs text-gray-400 font-mono leading-relaxed">
{engine === 'unity' ? (
`Assets/
└── Sprites/
    ├── character_001.png
    ├── character_001.png.meta
    ├── spritesheet.png
    └── spritesheet.json`
) : (
`assets/
└── sprites/
    ├── character_001.png
    ├── character_001.png.import
    ├── spritesheet.png
    └── spritesheet.json`
)}
        </pre>
      </section>

      {/* Export button */}
      <button
        className="btn-primary w-full py-3 text-base"
        onClick={handleExport}
      >
        📦 导出 {engine === 'unity' ? 'Unity' : 'Godot'} ZIP 包
      </button>
    </div>
  );
}

function ToggleOption({
  label,
  desc,
  checked,
  onChange,
}: {
  label: string;
  desc: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-3 cursor-pointer group">
      <input
        type="checkbox"
        className="mt-0.5 accent-brand-500"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <div>
        <div className="text-sm font-medium text-gray-300 group-hover:text-gray-200">
          {label}
        </div>
        <div className="text-xs text-gray-500">{desc}</div>
      </div>
    </label>
  );
}
