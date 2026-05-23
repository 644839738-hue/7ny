import { useState } from 'react';
import type { AssetType, PixelSize } from '../types';

export default function AssetGenerator() {
  const [prompt, setPrompt] = useState('');
  const [assetType, setAssetType] = useState<AssetType>('character');
  const [size, setSize] = useState<PixelSize>(32);
  const [count, setCount] = useState(4);

  const handleGenerate = () => {
    // Placeholder — will be wired to API in a future PR
    console.log('Generate:', { prompt, assetType, size, count });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">素材生成</h2>

      <section className="card space-y-5">
        {/* Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            描述 (Prompt)
          </label>
          <textarea
            className="input-field h-24 resize-none"
            placeholder="描述你想要的 2D 游戏素材，例如：a brave knight with golden sword, pixel art style"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <p className="text-xs text-gray-500 mt-1">{prompt.length}/500</p>
        </div>

        {/* Type */}
        <div className="grid grid-cols-4 gap-3">
          {([
            ['character', '角色', '🧑'],
            ['prop', '道具', '⚔️'],
            ['tile', 'Tile', '🧱'],
            ['ui', 'UI', '🖼️'],
          ] as [AssetType, string, string][]).map(([key, label, icon]) => (
            <button
              key={key}
              onClick={() => setAssetType(key)}
              className={`p-3 rounded-lg border text-center transition-colors duration-150 ${
                assetType === key
                  ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                  : 'border-gray-700 bg-gray-800/50 text-gray-400 hover:border-gray-600'
              }`}
            >
              <div className="text-xl mb-1">{icon}</div>
              <div className="text-xs font-medium">{label}</div>
            </button>
          ))}
        </div>

        {/* Size + Count */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              像素尺寸
            </label>
            <div className="flex gap-2">
              {([32, 64] as PixelSize[]).map((s) => (
                <button
                  key={s}
                  onClick={() => setSize(s)}
                  className={`px-4 py-2 rounded-lg border text-sm font-mono transition-colors duration-150 ${
                    size === s
                      ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                      : 'border-gray-700 bg-gray-800/50 text-gray-400 hover:border-gray-600'
                  }`}
                >
                  {s}×{s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              生成数量
            </label>
            <select
              className="input-field"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            >
              {[1, 2, 4, 8, 16].map((n) => (
                <option key={n} value={n}>{n} 个</option>
              ))}
            </select>
          </div>
        </div>

        {/* Generate button */}
        <button
          className="btn-primary w-full py-3 text-base"
          disabled={!prompt.trim()}
          onClick={handleGenerate}
        >
          ✨ 生成素材
        </button>
      </section>

      {/* Result placeholder */}
      <section className="card">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          生成结果
        </h3>
        <div className="border-2 border-dashed border-gray-800 rounded-lg p-12 text-center">
          <p className="text-gray-600">输入 prompt 并点击「生成素材」开始</p>
          <p className="text-xs text-gray-700 mt-1">
            DEMO 模式下将使用内置样例素材
          </p>
        </div>
      </section>
    </div>
  );
}
