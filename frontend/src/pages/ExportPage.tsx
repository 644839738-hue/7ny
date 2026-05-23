import { useCallback, useState } from 'react';
import type { EngineType, ExportResult } from '../types';
import { exportPackage, getTask } from '../services/api';
import { DEMO_MODE } from '../config/demo';

export default function ExportPage() {
  // ---- form state ----
  const [taskId, setTaskId] = useState('');
  const [assetIds, setAssetIds] = useState<string[]>([]);
  const [projectName, setProjectName] = useState('my-game');
  const [engine, setEngine] = useState<EngineType>('unity');
  const [includeSpritesheet, setIncludeSpritesheet] = useState(true);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeTilePreview, setIncludeTilePreview] = useState(true);

  // ---- result state ----
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ExportResult | null>(null);

  // ---- fetch assets from task ----
  const handleFetchTask = useCallback(async () => {
    if (!taskId.trim()) return;
    setError('');
    setLoading(true);
    try {
      const task = await getTask(taskId.trim());
      if (task.status !== 'ready') {
        setError(`Task is not ready (status: ${task.status})`);
        setLoading(false);
        return;
      }
      const ids = (task.assets || []).map((a) => a.id);
      if (ids.length === 0) {
        setError('Task has no assets');
      } else {
        setAssetIds(ids);
        setError('');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch task');
    }
    setLoading(false);
  }, [taskId]);

  // ---- export ----
  const handleExport = useCallback(async () => {
    if (assetIds.length === 0) return;
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const data = await exportPackage({
        projectName: projectName.trim() || 'spriteforge-export',
        assetIds,
        engine,
        includeSpritesheet,
        includeMetadata,
        includeTilePreview,
      });
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Export failed');
    }
    setLoading(false);
  }, [assetIds, projectName, engine, includeSpritesheet, includeMetadata, includeTilePreview]);

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">导出素材包</h2>
        {DEMO_MODE && (
          <span className="text-xs bg-amber-900/60 text-amber-300 border border-amber-700
                           px-2.5 py-1 rounded-full">
            DEMO
          </span>
        )}
      </div>

      {/* ---- step 1: load assets ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          步骤 1 — 加载素材
        </h3>
        <p className="text-xs text-gray-500">
          输入 task ID 加载要导出的素材列表。可加载多个任务的素材（多次加载追加）。
        </p>
        <div className="flex gap-2">
          <input
            className="input-field flex-1 font-mono text-sm"
            placeholder="粘贴 task_id..."
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
          />
          <button className="btn-secondary text-sm" onClick={handleFetchTask} disabled={loading}>
            加载
          </button>
        </div>
        {assetIds.length > 0 && (
          <p className="text-xs text-gray-400">
            已加载 <span className="text-brand-400 font-mono">{assetIds.length}</span> 个素材
          </p>
        )}
      </section>

      {/* ---- step 2: export settings ---- */}
      <section className="card space-y-5">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          步骤 2 — 导出设置
        </h3>

        {/* project name */}
        <div>
          <label className="text-xs text-gray-400 mb-1 block">项目名称</label>
          <input
            className="input-field text-sm w-64"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
          />
        </div>

        {/* Engine selector */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            目标引擎
          </label>
          <div className="flex gap-3">
            {([
              ['unity', 'Unity', 'Assets/Sprites/ 约定'],
              ['godot', 'Godot', 'assets/sprites/ 约定'],
              ['generic', 'Generic', '通用目录结构'],
            ] as [EngineType, string, string][]).map(([key, label, desc]) => (
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
                <div className="text-xs text-gray-500 mt-1">{desc}</div>
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
            desc="manifest.json 记录所有素材信息和参数"
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

      {/* ---- step 3: export ---- */}
      <button
        className="btn-primary w-full py-3 text-base"
        disabled={assetIds.length === 0 || loading}
        onClick={handleExport}
      >
        {loading ? '打包中...' : `导出 ${engine === 'unity' ? 'Unity' : engine === 'godot' ? 'Godot' : 'Generic'} ZIP 包`}
      </button>

      {/* ---- error ---- */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ---- result ---- */}
      {result && (
        <>
          {/* download card */}
          <section className="card space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                  导出成功
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {result.fileCount} 个文件 · {formatBytes(result.totalSizeBytes)}
                </p>
              </div>
              <a
                href={result.downloadUrl}
                download
                className="btn-primary text-sm py-2 px-6 inline-block"
              >
                下载 ZIP
              </a>
            </div>
          </section>

          {/* file structure preview */}
          <section className="card">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              导出结构预览
            </h3>
            <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4
                            text-xs text-green-400/90 font-mono leading-relaxed
                            overflow-x-auto max-h-80 overflow-y-auto">
              {renderFileTree(result.packageStructure.files)}
            </pre>
          </section>

          {/* README hint */}
          <section className="card">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
              README_IMPORT.md
            </h3>
            <p className="text-xs text-gray-500">
              ZIP 包内附有 {engine === 'unity' ? 'Unity' : engine === 'godot' ? 'Godot' : '通用'} 引擎导入说明，
              解压后查看 README_IMPORT.md 了解如何在目标引擎中配置素材。
            </p>
          </section>
        </>
      )}

      {/* empty state */}
      {!result && !loading && !error && (
        <section className="card text-center py-12">
          <p className="text-gray-600">加载素材并设置导出参数后，点击导出按钮</p>
          <p className="text-xs text-gray-700 mt-1">
            将生成包含素材、Sprite Sheet、元数据和引擎导入说明的 ZIP 包
          </p>
        </section>
      )}
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

/** Render a simple ASCII tree from a sorted file list. */
function renderFileTree(files: string[]): string {
  if (files.length === 0) return '(empty)';
  const sorted = [...files].sort();
  const lines: string[] = [];
  const roots = new Map<string, string[]>();

  for (const f of sorted) {
    const slash = f.indexOf('/');
    if (slash === -1) {
      lines.push(f);
    } else {
      const dir = f.substring(0, slash);
      const rest = f.substring(slash + 1);
      if (!roots.has(dir)) roots.set(dir, []);
      roots.get(dir)!.push(rest);
    }
  }

  for (const [dir, children] of roots) {
    lines.push(`${dir}/`);
    for (let i = 0; i < children.length; i++) {
      const prefix = i === children.length - 1 ? '└── ' : '├── ';
      lines.push(`  ${prefix}${children[i]}`);
    }
  }

  return lines.join('\n');
}
