import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { AssetType, ArtStyle, PixelSize, EngineType, GenerationProvider, GenerateParams, RuntimeConfig } from '../types';
import { getProjectSettings } from '../utils/projectSettings';
import type { AssetType, ArtStyle, EngineType, GenerateParams, GenerationProvider, PixelSize, RuntimeConfig } from '../types';
import { generateAssets, getRuntimeConfig, getTask } from '../services/api';
import { getProjectSettings } from '../utils/projectSettings';

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

const COUNT_OPTIONS: (1 | 4 | 8)[] = [1, 4, 8];

const ENGINE_OPTIONS: { key: EngineType; label: string }[] = [
  { key: 'unity',    label: 'Unity' },
  { key: 'godot',    label: 'Godot' },
  { key: 'generic',  label: '通用' },
];

const PROVIDER_OPTIONS: { key: GenerationProvider; label: string; desc: string }[] = [
  { key: 'auto',    label: 'Auto',   desc: '跟随后端配置' },
  { key: 'demo',    label: 'Demo',   desc: '内置素材' },
  { key: 'wanxiang', label: '通义万相', desc: 'AI 生成' },
];

// --- component ------------------------------------------------------------

function loadDefaults() {
  const s = getProjectSettings();
  return {
    projectName: s.projectName,
    assetType: s.defaultAssetType,
    style: s.defaultStyle,
    size: s.defaultSize,
    count: s.defaultCount,
    targetEngine: s.defaultTargetEngine,
    generationProvider: s.generationProvider,
    transparentBg: s.transparentBackground,
  };
}

export default function AssetGenerator() {
  const defs = loadDefaults();

  const [projectName, setProjectName] = useState(defs.projectName);
  const [assetType, setAssetType] = useState<AssetType>(defs.assetType);
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState<ArtStyle>(defs.style);
  const [size, setSize] = useState<PixelSize>(defs.size);
  const [count, setCount] = useState(defs.count);
  const [targetEngine, setTargetEngine] = useState<EngineType>(defs.targetEngine);
  const [generationProvider, setGenerationProvider] = useState<GenerationProvider>(defs.generationProvider);
  const [transparentBg, setTransparentBg] = useState(defs.transparentBg);

  // runtime config from backend
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig | null>(null);

  // result state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [warning, setWarning] = useState('');
  const [taskId, setTaskId] = useState('');
  const [generatedAssets, setGeneratedAssets] = useState<{
    id: string; name: string; type: string; width: number; height: number; image_url: string;
    metadata?: Record<string, unknown>;
  }[]>([]);

  useEffect(() => {
    getRuntimeConfig()
      .then(setRuntimeConfig)
      .catch(() => setRuntimeConfig(null));
  }, []);

  const handleReloadDefaults = () => {
    const d = loadDefaults();
    setProjectName(d.projectName);
    setAssetType(d.assetType);
    setStyle(d.style);
    setSize(d.size);
    setCount(d.count);
    setTargetEngine(d.targetEngine);
    setGenerationProvider(d.generationProvider);
    setTransparentBg(d.transparentBg);
  };

  const handleGenerate = useCallback(async () => {
    setError('');
    setWarning('');
    setLoading(true);
    setTaskId('');
    setGeneratedAssets([]);

    const params: GenerateParams = {
      projectName: projectName.trim(),
      assetType,
      prompt: prompt.trim(),
      style,
      size,
      count,
      targetEngine,
      transparentBackground: transparentBg,
      generationProvider,
    };

    try {
      const resp = await generateAssets(params);
      setTaskId(resp.task_id);

      if (resp.status === 'ready') {
        const task = await getTask(resp.task_id);
        setGeneratedAssets(task.assets || []);
        if (task.warning) {
          setWarning(task.warning);
        }
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '生成失败，请检查后端是否启动');
    }
    setLoading(false);
  }, [projectName, assetType, prompt, style, size, count, targetEngine, transparentBg, generationProvider]);

  const handleCopyTaskId = () => {
    navigator.clipboard.writeText(taskId);
  };

  const isFormValid = projectName.trim().length > 0 && prompt.trim().length > 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">素材生成</h2>
          <p className="text-xs text-gray-600 mt-0.5">
            默认参数来自项目配置，可在本页临时修改。
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors underline"
            onClick={handleReloadDefaults}
          >
            重新载入项目配置
          </button>
          {runtimeConfig && (
            <span className={`text-xs px-2.5 py-1 rounded-full border ${
              runtimeConfig.demo_mode
                ? 'bg-amber-900/60 text-amber-300 border-amber-700'
                : 'bg-emerald-900/60 text-emerald-300 border-emerald-700'
            }`}>
              {runtimeConfig.provider_label}{runtimeConfig.wanxiang_configured ? ' (已配置)' : ''}
            </span>
          )}
        </div>
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
                  {s}x{s}
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

        {/* generationProvider */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            生成模式
          </label>
          <div className="flex gap-2">
            {([
              { key: 'auto' as const, label: 'Auto', desc: '跟随后端配置' },
              { key: 'demo' as const, label: 'Demo', desc: '内置素材' },
              { key: 'wanxiang' as const, label: '通义万相', desc: 'AI 生成' },
            ]).map(({ key, label, desc }) => (
              <button
                key={key}
                type="button"
                onClick={() => setGenerationProvider(key)}
                className={`flex-1 py-2 rounded-lg border text-center transition-all duration-150 ${
                  generationProvider === key
                    ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                    : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
                }`}
              >
                <div className="text-sm font-medium">{label}</div>
                <div className="text-[10px] opacity-60">{desc}</div>
              </button>
            ))}
          </div>
          <p className="text-[10px] text-gray-600 mt-1">
            选择生成后端。API Key 仅保存在后端，不会泄露到前端。
          </p>
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
          disabled={!isFormValid || loading}
          onClick={handleGenerate}
        >
          {loading ? '生成中...' : '生成素材'}
        </button>
      </section>

      {/* ---- error ---- */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ---- warning (fallback, etc.) ---- */}
      {warning && (
        <div className="bg-amber-900/30 border border-amber-800 rounded-lg p-4 text-sm text-amber-300">
          <span className="font-semibold">Warning: </span>
          {warning}
        </div>
      )}

      {/* ---- result ---- */}
      {taskId && (
        <section className="card space-y-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            生成结果
          </h3>

          {/* task ID */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Task ID:</span>
            <code className="text-xs text-brand-300 bg-gray-900 px-2 py-1 rounded font-mono select-all">
              {taskId}
            </code>
            <button
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              onClick={handleCopyTaskId}
            >
              复制
            </button>
          </div>
          <p className="text-xs text-gray-600">
            将此 Task ID 粘贴至 Sprite Sheet 工具、Tile 预览或导出页面，以加载已生成的素材。
          </p>
          {generatedAssets.length > 0 && (
            <Link
              to="/assets"
              className="inline-flex items-center gap-1.5 text-sm text-brand-400 hover:text-brand-300 transition-colors"
            >
              查看素材库 &rarr;
            </Link>
          )}

          {/* asset thumbnails */}
          {generatedAssets.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">{generatedAssets.length} 个素材：</p>
              <div className="flex gap-3 flex-wrap">
                {generatedAssets.map((a) => (
                  <div key={a.id} className="flex flex-col items-center gap-1">
                    <div className="w-16 h-16 border border-gray-700 rounded bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')] overflow-hidden flex items-center justify-center">
                      <img
                        src={a.image_url}
                        alt={a.name}
                        className="max-w-full max-h-full pixelated"
                        style={{ imageRendering: 'pixelated' }}
                      />
                    </div>
                    <span className="text-[10px] text-gray-500 font-mono">{a.type}</span>
                    {a.metadata?.warning != null && (
                      <span className="text-[9px] text-amber-400 max-w-[120px] text-center leading-tight"
                        title={String(a.metadata.warning)}>
                        {(a.metadata.warning as string).slice(0, 60)}...
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* empty state */}
      {!taskId && !loading && !error && (
        <section className="card text-center py-12">
          <p className="text-gray-600">填写表单并点击「生成素材」，即可调用后端 API 生成素材</p>
          <p className="text-xs text-gray-700 mt-1">
            {runtimeConfig
              ? `当前后端模式：${runtimeConfig.provider_label}`
              : '加载后端配置中...'}
          </p>
        </section>
      )}
    </div>
  );
}
