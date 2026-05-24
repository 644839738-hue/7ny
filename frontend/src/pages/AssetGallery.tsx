import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { GeneratedAssetRecord } from '../types';
import { deleteAsset, listAssets } from '../services/api';
import { getAssetUrl } from '../utils/assetUrl';

const TYPE_LABELS: Record<string, string> = {
  character: '角色',
  item: '道具',
  tile: 'Tile',
  ui: 'UI',
};

const TYPE_FILTERS = [
  { key: '', label: '全部' },
  { key: 'character', label: '角色' },
  { key: 'item', label: '道具' },
  { key: 'tile', label: 'Tile' },
  { key: 'ui', label: 'UI' },
];

export default function AssetGallery() {
  const [assets, setAssets] = useState<GeneratedAssetRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [deleting, setDeleting] = useState<string | null>(null);

  const fetchAssets = useCallback(async () => {
    setError('');
    setLoading(true);
    try {
      const data = await listAssets({
        asset_type: typeFilter || undefined,
        limit: 100,
      });
      setAssets(data.items);
      setTotal(data.total);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '加载失败');
    }
    setLoading(false);
  }, [typeFilter]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const handleDelete = useCallback(async (id: string) => {
    if (!window.confirm('确认删除该素材记录？此操作不可撤销。')) return;
    setDeleting(id);
    try {
      await deleteAsset(id);
      setAssets((prev) => prev.filter((a) => a.id !== id));
      setTotal((prev) => prev - 1);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '删除失败');
    }
    setDeleting(null);
  }, []);

  const handleDownload = useCallback(async (asset: GeneratedAssetRecord) => {
    try {
      const resp = await fetch(getAssetUrl(asset.image_url));
      if (!resp.ok) throw new Error('Download failed');
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${asset.name}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError('下载失败，请检查后端是否启动');
    }
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">素材库</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            已生成素材历史记录 {total > 0 && `(${total} 条)`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/generator"
            className="text-sm text-brand-400 hover:text-brand-300 transition-colors"
          >
            前往素材生成
          </Link>
          <button
            className="text-sm text-gray-400 hover:text-gray-200 transition-colors"
            onClick={fetchAssets}
            disabled={loading}
          >
            {loading ? '刷新中...' : '刷新'}
          </button>
        </div>
      </div>

      {/* type filter */}
      <div className="flex gap-2">
        {TYPE_FILTERS.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => setTypeFilter(key)}
            className={`px-4 py-1.5 rounded-lg border text-sm transition-all duration-150 ${
              typeFilter === key
                ? 'border-brand-500 bg-brand-600/20 text-brand-300'
                : 'border-gray-700/80 bg-gray-800/40 text-gray-400 hover:border-gray-600 hover:bg-gray-800/60'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* error */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* loading */}
      {loading && (
        <div className="card text-center py-12">
          <p className="text-gray-500">加载中...</p>
        </div>
      )}

      {/* empty state */}
      {!loading && !error && assets.length === 0 && (
        <section className="card text-center py-12 space-y-3">
          <p className="text-gray-500">暂无已生成的素材</p>
          <p className="text-xs text-gray-600">
            前往
            <Link to="/generator" className="text-brand-400 hover:text-brand-300 mx-1">
              素材生成
            </Link>
            页面创建新素材
          </p>
        </section>
      )}

      {/* asset grid */}
      {!loading && assets.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {assets.map((asset) => (
            <div
              key={asset.id}
              className="card group relative flex flex-col"
            >
              {/* image */}
              <div
                className="w-full aspect-square border border-gray-700 rounded-lg mb-3 overflow-hidden
                           bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')]
                           flex items-center justify-center"
              >
                <img
                  src={getAssetUrl(asset.image_url)}
                  alt={asset.name}
                  className="max-w-full max-h-full pixelated"
                  style={{ imageRendering: 'pixelated' }}
                  loading="lazy"
                />
              </div>

              {/* info */}
              <div className="flex-1 space-y-1">
                <div className="text-xs font-mono text-gray-300 truncate" title={asset.name}>
                  {asset.name}
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                    {TYPE_LABELS[asset.asset_type] || asset.asset_type}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                    {asset.size}px
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                    {asset.style}
                  </span>
                </div>
                {asset.metadata?.warning != null && (
                  <p className="text-[9px] text-amber-400 leading-tight"
                     title={String(asset.metadata.warning)}>
                    {(asset.metadata.warning as string).slice(0, 50)}...
                  </p>
                )}
                <p className="text-[10px] text-gray-600">
                  {new Date(asset.created_at).toLocaleString('zh-CN', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>

              {/* actions */}
              <div className="flex gap-2 mt-3 pt-3 border-t border-gray-800/60">
                <button
                  className="flex-1 text-xs py-1.5 rounded bg-gray-800/60 text-gray-400
                             hover:bg-gray-700/60 hover:text-gray-200 transition-colors"
                  onClick={() => handleDownload(asset)}
                >
                  下载
                </button>
                <button
                  className="flex-1 text-xs py-1.5 rounded bg-red-900/20 text-red-400
                             hover:bg-red-900/40 hover:text-red-300 transition-colors"
                  onClick={() => handleDelete(asset.id)}
                  disabled={deleting === asset.id}
                >
                  {deleting === asset.id ? '删除中...' : '删除'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
