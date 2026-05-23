export default function SpriteSheetTool() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">Sprite Sheet 工具</h2>

      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          帧设置
        </h3>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">帧宽度</label>
            <input type="number" className="input-field" defaultValue={32} disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">帧高度</label>
            <input type="number" className="input-field" defaultValue={32} disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">列数</label>
            <input type="number" className="input-field" defaultValue={4} disabled />
          </div>
        </div>
      </section>

      {/* Preview placeholder */}
      <section className="card">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          Sprite Sheet 预览
        </h3>
        <div className="border-2 border-dashed border-gray-800 rounded-lg p-16 text-center">
          <p className="text-gray-600">先进入「素材生成」生成素材，然后回到此页面拼接</p>
          <p className="text-xs text-gray-700 mt-1">支持拖拽帧排序</p>
        </div>
      </section>

      {/* JSON metadata placeholder */}
      <section className="card">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          元数据 (JSON)
        </h3>
        <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4 text-xs text-gray-500 font-mono overflow-x-auto">
{`// 拼接后将在此显示帧坐标 JSON
// 示例:
// {
//   "frames": [
//     { "index": 0, "x": 0,  "y": 0, "width": 32, "height": 32 },
//     { "index": 1, "x": 32, "y": 0, "width": 32, "height": 32 }
//   ]
// }`}
        </pre>
      </section>
    </div>
  );
}
