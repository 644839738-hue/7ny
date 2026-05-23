import { DEMO_MODE } from '../config/demo';

export default function ProjectSettings() {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-bold">项目配置</h2>

      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          生成设置
        </h3>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              运行模式
            </label>
            <p className="text-sm text-gray-500">
              当前: <span className="text-amber-400 font-medium">{DEMO_MODE ? 'DEMO 模式' : 'AI 模式'}</span>
              — 通过环境变量 <code className="bg-gray-800 px-1.5 py-0.5 rounded text-xs">VITE_DEMO_MODE</code> 切换
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              AI Provider
            </label>
            <select className="input-field w-64" disabled={DEMO_MODE}>
              <option>Demo Provider (内置)</option>
              <option disabled>OpenAI DALL·E (待接入)</option>
              <option disabled>Stability AI (待接入)</option>
            </select>
            {DEMO_MODE && (
              <p className="text-xs text-amber-400/80 mt-1">
                DEMO 模式下仅可使用内置 Provider
              </p>
            )}
          </div>
        </div>
      </section>

      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          默认参数
        </h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              默认素材尺寸
            </label>
            <select className="input-field" defaultValue={32}>
              <option value={32}>32 × 32</option>
              <option value={64}>64 × 64</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              默认素材类型
            </label>
            <select className="input-field" defaultValue="character">
              <option value="character">角色 (Character)</option>
              <option value="prop">道具 (Prop)</option>
              <option value="tile">Tile</option>
              <option value="ui">UI</option>
            </select>
          </div>
        </div>
      </section>

      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          导出设置
        </h3>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            默认目标引擎
          </label>
          <select className="input-field w-64" defaultValue="unity">
            <option value="unity">Unity</option>
            <option value="godot">Godot</option>
          </select>
        </div>
      </section>
    </div>
  );
}
