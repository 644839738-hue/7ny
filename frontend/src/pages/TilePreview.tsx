export default function TilePreview() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">Tile 预览与检测</h2>

      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          选择 Tile
        </h3>
        <p className="text-sm text-gray-500">
          选择一张已生成的 Tile 素材进行 3×3 平铺预览和边缘一致性评分。
        </p>
        <select className="input-field w-64" disabled>
          <option>-- 暂无 Tile 素材，请先生成 --</option>
        </select>
      </section>

      {/* 3×3 preview */}
      <div className="grid grid-cols-2 gap-6">
        <section className="card">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            3×3 平铺预览
          </h3>
          <div className="border-2 border-dashed border-gray-800 rounded-lg aspect-square
                          flex items-center justify-center">
            <p className="text-gray-600 text-sm text-center px-4">
              选择 Tile 后将在此显示<br />3×3 平铺效果
            </p>
          </div>
        </section>

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
    </div>
  );
}
