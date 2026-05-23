import { useCallback, useState } from 'react';
import type { TilePreview as TilePreviewResult } from '../types';
import { buildTilePreview, getTask } from '../services/api';
import { DEMO_MODE } from '../config/demo';

export default function TilePreview() {
  // ---- form state ----
  const [taskId, setTaskId] = useState('');
  const [assets, setAssets] = useState<{ id: string; name: string; type: string; width: number; height: number; image_url: string }[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState('');

  // ---- result state ----
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<TilePreviewResult | null>(null);

  // ---- fetch assets from a completed task ----
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
      const tileAssets = (task.assets || []).filter((a) => a.type === 'tile');
      if (tileAssets.length === 0) {
        setError('Task has no tile assets — generate tile-type assets first');
      } else {
        setAssets(tileAssets);
        setError('');
        if (tileAssets.length === 1) setSelectedAssetId(tileAssets[0].id);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch task');
    }
    setLoading(false);
  }, [taskId]);

  // ---- build 3×3 preview ----
  const handlePreview = useCallback(async () => {
    if (!selectedAssetId) return;
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const data = await buildTilePreview({ assetId: selectedAssetId });
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Preview failed');
    }
    setLoading(false);
  }, [selectedAssetId]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Tile 预览与检测</h2>
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
          步骤 1 — 加载 Tile 素材
        </h3>
        <p className="text-xs text-gray-500">
          先在「素材生成」页面生成 tile 类型的素材，然后在此输入 task ID 加载。
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
        {assets.length > 0 && (
          <div>
            <label className="text-xs text-gray-400 mb-1 block">
              选择 Tile（{assets.length} 个可用）：
            </label>
            <select
              className="input-field w-full text-sm"
              value={selectedAssetId}
              onChange={(e) => setSelectedAssetId(e.target.value)}
            >
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.width}×{a.height})
                </option>
              ))}
            </select>
          </div>
        )}
      </section>

      {/* ---- step 2: generate preview ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          步骤 2 — 3×3 平铺预览
        </h3>
        <button
          className="btn-primary w-full py-3 text-base"
          disabled={!selectedAssetId || loading}
          onClick={handlePreview}
        >
          {loading ? '生成中...' : '生成 3×3 平铺预览'}
        </button>
      </section>

      {/* ---- error ---- */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ---- result ---- */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 3×3 preview image */}
          <section className="card space-y-3">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              3×3 平铺预览 ({result.previewSize[0]}×{result.previewSize[1]})
            </h3>
            <p className="text-xs text-gray-600">
              原始 Tile：{result.tileSize[0]}×{result.tileSize[1]}px
            </p>
            <div className="bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')] rounded-lg p-2 flex items-center justify-center">
              <img
                src={result.tilePreviewUrl}
                alt="3×3 Tile Preview"
                className="max-w-full pixelated"
                style={{ imageRendering: 'pixelated' }}
              />
            </div>
            <a
              href={result.tilePreviewUrl}
              download
              className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
            >
              下载 PNG
            </a>
          </section>

          {/* edge scoring (placeholder for PR #14) */}
          <section className="card">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              边缘一致性评分
            </h3>
            <div className="flex flex-col items-center justify-center h-full">
              <div className="text-4xl font-bold text-gray-700 font-mono">--</div>
              <p className="text-xs text-gray-600 mt-2">0-100，分数越高无缝效果越好</p>

              <div className="mt-4 space-y-2 w-full">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>上-下边一致性</span>
                  <span className="font-mono">--</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div className="bg-gray-700 h-1.5 rounded-full" style={{ width: '0%' }} />
                </div>

                <div className="flex justify-between text-xs text-gray-500">
                  <span>左-右边一致性</span>
                  <span className="font-mono">--</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div className="bg-gray-700 h-1.5 rounded-full" style={{ width: '0%' }} />
                </div>
              </div>

              <div className="mt-4">
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-500">
                  等待数据
                </span>
              </div>
            </div>
          </section>
        </div>
      )}

      {/* empty state */}
      {!result && !loading && !error && (
        <section className="card text-center py-12">
          <p className="text-gray-600">加载 Tile 素材后，点击生成按钮查看 3×3 平铺效果</p>
          <p className="text-xs text-gray-700 mt-1">
            平铺预览可帮助您检查 Tile 在重复排列时的边缘过渡效果
          </p>
        </section>
      )}
    </div>
  );
}
