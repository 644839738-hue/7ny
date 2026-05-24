import { useCallback, useEffect, useState } from 'react';
import type { ArtStyle, AssetType, EngineType, GenerationProvider, PixelSize, ProjectSettings } from '../types';
import { getProjectSettings, resetProjectSettings, saveProjectSettings } from '../utils/projectSettings';

const ASSET_TYPE_OPTIONS: { key: AssetType; label: string }[] = [
  { key: 'character', label: '角色 (Character)' },
  { key: 'item', label: '道具 (Item)' },
  { key: 'tile', label: 'Tile' },
  { key: 'ui', label: 'UI' },
];

const STYLE_OPTIONS: { key: ArtStyle; label: string }[] = [
  { key: 'pixel_art', label: '像素风 (Pixel Art)' },
  { key: 'cartoon', label: '卡通 (Cartoon)' },
  { key: 'dark_fantasy', label: '暗黑幻想 (Dark Fantasy)' },
];

const SIZE_OPTIONS: PixelSize[] = [32, 64, 128];

const COUNT_OPTIONS: (1 | 4 | 8)[] = [1, 4, 8];

const ENGINE_OPTIONS: { key: EngineType; label: string }[] = [
  { key: 'unity', label: 'Unity' },
  { key: 'godot', label: 'Godot' },
  { key: 'generic', label: '通用 (Generic)' },
];

const PROVIDER_OPTIONS: { key: GenerationProvider; label: string; desc: string }[] = [
  { key: 'auto', label: 'Auto', desc: '跟随后端配置' },
  { key: 'demo', label: 'Demo', desc: '内置素材' },
  { key: 'wanxiang', label: '通义万相', desc: 'AI 生成' },
];

export default function ProjectSettingsPage() {
  const [settings, setSettings] = useState<ProjectSettings>(getProjectSettings);
  const [saved, setSaved] = useState(false);
  const [reset, setReset] = useState(false);

  useEffect(() => {
    if (saved) {
      const t = setTimeout(() => setSaved(false), 3000);
      return () => clearTimeout(t);
    }
  }, [saved]);

  useEffect(() => {
    if (reset) {
      const t = setTimeout(() => setReset(false), 3000);
      return () => clearTimeout(t);
    }
  }, [reset]);

  const handleSave = useCallback(() => {
    saveProjectSettings(settings);
    setSaved(true);
  }, [settings]);

  const handleReset = useCallback(() => {
    const defaults = resetProjectSettings();
    setSettings(defaults);
    setReset(true);
  }, []);

  const update = <K extends keyof ProjectSettings>(key: K, value: ProjectSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">项目配置</h2>

      {/* ---- default params ---- */}
      <section className="card space-y-5">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          默认生成参数
        </h3>

        {/* projectName */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            项目名称
          </label>
          <input
            type="text"
            className="input-field"
            value={settings.projectName}
            onChange={(e) => update('projectName', e.target.value)}
          />
        </div>

        {/* defaultAssetType */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认素材类型
          </label>
          <div className="grid grid-cols-4 gap-2">
            {ASSET_TYPE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => update('defaultAssetType', key)}
                className={`p-3 rounded-lg border text-center transition-all duration-150 text-xs font-medium ${
                  settings.defaultAssetType === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* defaultStyle */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认美术风格
          </label>
          <div className="flex gap-2">
            {STYLE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => update('defaultStyle', key)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all duration-150 ${
                  settings.defaultStyle === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* defaultSize + defaultCount */}
        <div className="grid grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              默认尺寸
            </label>
            <div className="flex gap-2">
              {SIZE_OPTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => update('defaultSize', s)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-mono transition-all duration-150 ${
                    settings.defaultSize === s
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
              默认生成数量
            </label>
            <div className="flex gap-2">
              {COUNT_OPTIONS.map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => update('defaultCount', n)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-mono transition-all duration-150 ${
                    settings.defaultCount === n
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

        {/* defaultTargetEngine */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认目标引擎
          </label>
          <div className="flex gap-2">
            {ENGINE_OPTIONS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => update('defaultTargetEngine', key)}
                className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-all duration-150 ${
                  settings.defaultTargetEngine === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* generationProvider */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            默认生成模式
          </label>
          <div className="flex gap-2">
            {PROVIDER_OPTIONS.map(({ key, label, desc }) => (
              <button
                key={key}
                type="button"
                onClick={() => update('generationProvider', key)}
                className={`flex-1 py-2 rounded-lg border text-center transition-all duration-150 ${
                  settings.generationProvider === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                <div className="text-sm font-medium">{label}</div>
                <div className="text-[10px] opacity-60">{desc}</div>
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
            <div className="text-xs text-gray-500">输出 RGBA PNG，移除生成背景</div>
          </div>
        </label>

        {/* ---- actions ---- */}
        <div className="flex gap-3 pt-2">
          <button className="btn-primary flex-1 py-2.5" onClick={handleSave}>
            保存配置
          </button>
          <button
            className="flex-1 py-2.5 rounded-lg border border-gray-700 bg-gray-800/40 text-gray-400
                       hover:border-gray-600 hover:bg-gray-800/60 hover:text-gray-300
                       transition-all duration-150 text-sm font-medium"
            onClick={handleReset}
          >
            重置默认配置
          </button>
        </div>
      </section>

      {/* ---- feedback ---- */}
      {saved && (
        <div className="bg-emerald-900/30 border border-emerald-800 rounded-lg p-4 text-sm text-emerald-300">
          项目配置已保存，将在素材生成页作为默认参数使用。
        </div>
      )}
      {reset && (
        <div className="bg-blue-900/30 border border-blue-800 rounded-lg p-4 text-sm text-blue-300">
          已恢复默认项目配置。
        </div>
      )}

      {/* ---- footnotes ---- */}
      <section className="card space-y-3 text-xs text-gray-500">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">说明</h3>
        <ul className="space-y-1.5 list-disc list-inside">
          <li>项目配置只保存默认生成参数，保存在浏览器 localStorage。</li>
          <li>素材生成页会自动读取这些默认值，但你在生成页仍可临时修改参数。</li>
          <li>通义万相 API Key 仍然只在 <code className="bg-gray-800 px-1 py-0.5 rounded">backend/.env</code> 中配置，不会保存到前端。</li>
          <li>
            生成模式选择 <strong>wanxiang</strong> 时，如果后端未配置 API Key，后端可能回退 Demo 模式或返回错误，
            取决于后端 <code className="bg-gray-800 px-1 py-0.5 rounded">ALLOW_DEMO_FALLBACK</code> 配置。
          </li>
        </ul>
      </section>
    </div>
  );
}
