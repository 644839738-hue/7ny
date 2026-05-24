import { useCallback, useState } from 'react';
import type { ArtStyle, AssetType, EngineType, GenerationProvider, PixelSize, ProjectSettings } from '../types';
import { getProjectSettings, resetProjectSettings, saveProjectSettings } from '../utils/projectSettings';

// --- option defs ----------------------------------------------------------

const ASSET_TYPE_OPTIONS: { key: AssetType; label: string }[] = [
  { key: 'character', label: '角色 (Character)' },
  { key: 'item',      label: '道具 (Item)' },
  { key: 'tile',      label: 'Tile' },
  { key: 'ui',        label: 'UI' },
];

const STYLE_OPTIONS: { key: ArtStyle; label: string }[] = [
  { key: 'pixel_art',    label: '像素风' },
  { key: 'cartoon',      label: '卡通' },
  { key: 'dark_fantasy', label: '暗黑幻想' },
];

const SIZE_OPTIONS: PixelSize[] = [32, 64, 128];

const ENGINE_OPTIONS: { key: EngineType; label: string }[] = [
  { key: 'unity',   label: 'Unity' },
  { key: 'godot',   label: 'Godot' },
  { key: 'generic', label: '通用' },
];

const PROVIDER_OPTIONS: { key: GenerationProvider; label: string; desc: string }[] = [
  { key: 'auto',     label: 'Auto',      desc: '跟随后端配置' },
  { key: 'demo',     label: 'Demo',      desc: '内置素材' },
  { key: 'wanxiang', label: '通义万相',   desc: 'AI 生成' },
];

// --- component ------------------------------------------------------------

export default function ProjectSettings() {
  const [settings, setSettings] = useState<ProjectSettings>(getProjectSettings);
  const [saved, setSaved] = useState(false);

  const handleSave = useCallback(() => {
    saveProjectSettings(settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }, [settings]);

  const handleReset = useCallback(() => {
    const defaults = resetProjectSettings();
    setSettings(defaults);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }, []);

  const update = <K extends keyof ProjectSettings>(key: K, value: ProjectSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">项目配置</h2>

      {/* ---- Generation defaults ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          生成默认参数
        </h3>

        {/* projectName */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            默认项目名称
          </label>
          <input
            type="text"
            className="input-field"
            value={settings.projectName}
            onChange={(e) => update('projectName', e.target.value)}
          />
        </div>

        {/* assetType */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认素材类型
          </label>
          <select
            className="input-field"
            value={settings.defaultAssetType}
            onChange={(e) => update('defaultAssetType', e.target.value as AssetType)}
          >
            {ASSET_TYPE_OPTIONS.map(({ key, label }) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* style */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认美术风格
          </label>
          <select
            className="input-field"
            value={settings.defaultStyle}
            onChange={(e) => update('defaultStyle', e.target.value as ArtStyle)}
          >
            {STYLE_OPTIONS.map(({ key, label }) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* size */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认像素尺寸
          </label>
          <select
            className="input-field"
            value={settings.defaultSize}
            onChange={(e) => update('defaultSize', Number(e.target.value) as PixelSize)}
          >
            {SIZE_OPTIONS.map((s) => (
              <option key={s} value={s}>{s} x {s}</option>
            ))}
          </select>
        </div>

        {/* count */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认生成数量
          </label>
          <select
            className="input-field"
            value={settings.defaultCount}
            onChange={(e) => update('defaultCount', Number(e.target.value))}
          >
            <option value={1}>1</option>
            <option value={4}>4</option>
            <option value={8}>8</option>
          </select>
        </div>

        {/* targetEngine */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认目标引擎
          </label>
          <select
            className="input-field"
            value={settings.defaultTargetEngine}
            onChange={(e) => update('defaultTargetEngine', e.target.value as EngineType)}
          >
            {ENGINE_OPTIONS.map(({ key, label }) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* generationProvider */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            生成后端
          </label>
          <div className="flex gap-2">
            {PROVIDER_OPTIONS.map(({ key, label, desc }) => (
              <button
                key={key}
                type="button"
                onClick={() => update('generationProvider', key)}
                className={`flex-1 py-2 rounded-lg border text-sm transition-all duration-150 ${
                  settings.generationProvider === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                <div className="font-medium">{label}</div>
                <div className="text-[10px] opacity-70">{desc}</div>
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
              checked={settings.transparentBackground}
              onChange={(e) => update('transparentBackground', e.target.checked)}
            />
            <div className={`w-10 h-5 rounded-full transition-colors duration-200 ${
              settings.transparentBackground ? 'bg-brand-600' : 'bg-gray-700'
            }`}>
              <div className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-0.5 transition-transform duration-200 ${
                settings.transparentBackground ? 'left-[22px]' : 'left-[2px]'
              }`} />
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-300 group-hover:text-gray-200">
              默认透明背景
            </div>
            <div className="text-xs text-gray-500">新生成的素材默认启用透明背景</div>
          </div>
        </label>
      </section>

      {/* ---- Actions ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          操作
        </h3>

        <div className="flex gap-3">
          <button className="btn-primary" onClick={handleSave}>
            保存配置
          </button>
          <button
            className="px-4 py-2 rounded-lg border border-gray-700 text-sm text-gray-400 hover:border-gray-600 hover:text-gray-300 transition-colors"
            onClick={handleReset}
          >
            恢复默认
          </button>
        </div>

        {saved && (
          <p className="text-sm text-green-400">配置已保存</p>
        )}

        <div className="text-xs text-gray-600 space-y-1 mt-3">
          <p>配置保存在浏览器的 localStorage 中，不会上传到服务器。</p>
          <p>AI 生成需要 API Key，请将 API Key 配置在 <code className="bg-gray-800 px-1 rounded">backend/.env</code> 文件中。</p>
          <p>通义万相模式在 AI 生成失败时会自动回退到 Demo 模式（需开启 ALLOW_DEMO_FALLBACK=true）。</p>
        </div>
      </section>
    </div>
  );
}
