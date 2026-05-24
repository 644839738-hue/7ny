import { useEffect, useState } from 'react';
import type { RuntimeConfig } from '../../types';
import { getRuntimeConfig } from '../../services/api';
import { getGenerationModeLabel, getGenerationModeTone, getGenerationModeBadgeClass } from '../../utils/generationMode';
import { getProjectSettings } from '../../utils/projectSettings';

export default function Header() {
  const [rtConfig, setRtConfig] = useState<RuntimeConfig | null>(null);
  const lastProvider = getProjectSettings().generationProvider;

  useEffect(() => {
    getRuntimeConfig().then(setRtConfig).catch(() => {});
  }, []);

  const label = rtConfig
    ? `后端默认：${getGenerationModeLabel('auto', rtConfig)}`
    : '加载中...';
  const tone = getGenerationModeTone('auto', rtConfig);

  return (
    <header className="h-14 border-b border-gray-800 bg-gray-950 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-xl">🎮</span>
        <h1 className="text-lg font-bold tracking-tight">
          SpriteForge <span className="text-brand-400">AI</span>
        </h1>
      </div>

      <div className="flex items-center gap-4 text-sm">
        {rtConfig && (
          <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${getGenerationModeBadgeClass(tone)}`}>
            {label}
          </span>
        )}
        <span className="text-xs text-gray-600" title={`表单当前选择：${lastProvider}`}>
          生成模式以表单选择为准
        </span>
        <span className="text-gray-500">v0.0.1</span>
      </div>
    </header>
  );
}
