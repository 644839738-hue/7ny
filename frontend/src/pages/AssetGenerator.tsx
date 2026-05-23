import { useState } from 'react';
import type { AssetType, ArtStyle, PixelSize, EngineType, GenerateParams } from '../types';
import { DEMO_MODE } from '../config/demo';

// --- option definitions ---------------------------------------------------

const ASSET_TYPE_OPTIONS: { key: AssetType; label: string; icon: string }[] = [
  { key: 'character', label: '角色', icon: '🧑' },
  { key: 'item',      label: '道具', icon: '⚔️' },
  { key: 'tile',      label: 'Tile', icon: '🧱' },
  { key: 'ui',        label: 'UI',   icon: '🖼️' },
];

const STYLE_OPTIONS: { key: ArtStyle; label: string }[] = [
  { key: 'pixel_art',     label: '像素风' },
  { key: 'cartoon',       label: '卡通' },
  { key: 'dark_fantasy',  label: '暗黑幻想' },
];

const SIZE_OPTIONS: PixelSize[] = [32, 64, 128];

const COUNT_OPTIONS = [1, 4, 8];

const ENGINE_OPTIONS: { key: EngineType; label: string }[] = [
  { key: 'unity',    label: 'Unity' },
  { key: 'godot',    label: 'Godot' },
  { key: 'generic',  label: '通用' },
];

// --- component ------------------------------------------------------------

export default function AssetGenerator() {
  const [projectName, setProjectName] = useState('');
  const [assetType, setAssetType] = useState<AssetType>('character');
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState<ArtStyle>('pixel_art');
  const [size, setSize] = useState<PixelSize>(32);
  const [count, setCount] = useState(4);
  const [targetEngine, setTargetEngine] = useState<EngineType>('unity');
  const [transparentBg, setTransparentBg] = useState(true);

  const [submittedParams, setSubmittedParams] = useState<GenerateParams | null>(null);

  const handleGenerate = () => {
    const params: GenerateParams = {
      projectName: projectName.trim(),
      assetType,
      prompt: prompt.trim(),
      style,
      size,
      count,
      targetEngine,
      transparentBackground: transparentBg,
    };
    console.log('[SpriteForge] Generate params:', params);
    setSubmittedParams(params);
  };

  const isFormValid = projectName.trim().length > 0 && prompt.trim().length > 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">素材生成</h2>
        {DEMO_MODE && (
          <span className="text-xs bg-amber-900/60 text-amber-300 border border-amber-700
                           px-2.5 py-1 rounded-full">
            参数将打印到控制台
          </span>
        )}
      </div>

      {/* ---- form card ---- */}
      <section className="card space-y-5">
        {/* projectName */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            项目名称 <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="例如：dungeon-crawler"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
          />
        </div>

        {/* assetType */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            素材类型
          </label>
          <div className="grid grid-cols-4 gap-2">
            {ASSET_TYPE_OPTIONS.map(({ key, label, icon }) => (
              <button
                key={key}
                type="button"
                onClick={() => setAssetType(key)}
                className={`p-3 rounded-lg border text-center transition-all duration-150 ${
                  assetType === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300 shadow-sm shadow-brand-500/10'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                <div className="text-xl mb-0.5">{icon}</div>
                <div className="text-xs font-medium">{label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            描述 Prompt <span className="text-red-400">*</span>
          </label>
          <textarea
            className="input-field h-20 resize-none"
            placeholder="描述你想要的素材，例如：a brave knight with golden sword, pixel art"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            maxLength={500}
          />
          <p className="text-xs text-gray-500 mt-1">{prompt.length}/500</p>
        </div>

        {/* style */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            美术风格
          </label>
          <div className="flex gap-2">
            {STYLE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => setStyle(key)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all duration-150 ${
                  style === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* size + count */}
        <div className="grid grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              像素尺寸
            </label>
            <div className="flex gap-2">
              {SIZE_OPTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setSize(s)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-mono transition-all duration-150 ${
                    size === s
                      ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                      : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                  }`}
                >
                  {s}×{s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              生成数量
            </label>
            <div className="flex gap-2">
              {COUNT_OPTIONS.map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setCount(n)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-mono transition-all duration-150 ${
                    count === n
                      ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                      : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* targetEngine */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            目标引擎
          </label>
          <div className="flex gap-2">
            {ENGINE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => setTargetEngine(key)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all duration-150 ${
                  targetEngine === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* transparentBackground */}
        <label className="flex items-center gap-3 cursor-pointer group">
          <div className="relative">
            <input
              type="checkbox"
              className="sr-only"
              checked={transparentBg}
              onChange={(e) => setTransparentBg(e.target.checked)}
            />
            <div className={`w-10 h-5 rounded-full transition-colors duration-200 ${
              transparentBg ? 'bg-brand-600' : 'bg-gray-700'
            }`}>
              <div className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-0.5 transition-transform duration-200 ${
                transparentBg ? 'left-[22px]' : 'left-[2px]'
              }`} />
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-300 group-hover:text-gray-200">
              透明背景
            </div>
            <div className="text-xs text-gray-500">输出 RGBA PNG，移除生成背景</div>
          </div>
        </label>

        {/* submit */}
        <button
          className="btn-primary w-full py-3 text-base"
          disabled={!isFormValid}
          onClick={handleGenerate}
        >
          ✨ 生成素材
        </button>
      </section>

      {/* ---- JSON preview ---- */}
      {submittedParams && (
        <section className="card space-y-3 animate-in fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              提交参数预览
            </h3>
            <button
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(submittedParams, null, 2));
              }}
            >
              复制 JSON
            </button>
          </div>

          <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4
                          text-xs text-green-400/90 font-mono leading-relaxed
                          overflow-x-auto max-h-64 overflow-y-auto">
{JSON.stringify(submittedParams, null, 2)}
          </pre>

          <p className="text-xs text-gray-600">
            ↑ 以上参数将在后续 PR 中发送至后端 API。当前 DEMO 模式下仅打印到控制台。
          </p>
        </section>
      )}

      {/* ---- empty state ---- */}
      {!submittedParams && (
        <section className="card">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            提交参数预览
          </h3>
          <div className="border-2 border-dashed border-gray-800 rounded-lg p-10 text-center">
            <p className="text-gray-600">填写表单并点击「生成素材」后，</p>
            <p className="text-gray-600">此处将显示序列化的请求参数 JSON</p>
            <p className="text-xs text-gray-700 mt-2">
              {DEMO_MODE ? 'DEMO 模式：参数同时打印到浏览器控制台' : ''}
            </p>
          </div>
        </section>
      )}
    </div>
  );
}
