import type { GenerationProvider, RuntimeConfig } from '../types';

/** Read-only subset of RuntimeConfig needed by mode label helpers. */
export type RuntimeConfigLike = Pick<
  RuntimeConfig,
  'demo_mode' | 'image_provider' | 'ai_enabled' | 'provider_label' | 'wanxiang_configured'
> | null | undefined;

/**
 * Return a human-readable label for the current generation mode,
 * taking both the userʼs form selection and the backend runtime config
 * into account.
 */
export function getGenerationModeLabel(
  selectedProvider: GenerationProvider,
  runtimeConfig?: RuntimeConfigLike,
): string {
  if (selectedProvider === 'demo') {
    return 'Demo 内置素材';
  }

  if (selectedProvider === 'wanxiang') {
    return runtimeConfig?.wanxiang_configured
      ? '通义万相 AI 生成（已配置）'
      : '通义万相 AI 生成（未配置 Key）';
  }

  // auto — describe what the backend will actually use
  if (runtimeConfig?.provider_label) {
    return `自动：${runtimeConfig.provider_label}`;
  }

  if (runtimeConfig?.demo_mode) {
    return '自动：Demo 内置素材';
  }

  if (runtimeConfig?.image_provider === 'wanxiang') {
    return '自动：通义万相 AI 生成';
  }

  return '自动：跟随后端配置';
}

/**
 * Return a tone that drive badge styling.
 *
 * - ``demo``   — amber (built-in / demo)
 * - ``ai``     — green (AI available)
 * - ``warning`` — amber (AI selected but might not work)
 * - ``auto``   — blue (following backend)
 */
export function getGenerationModeTone(
  selectedProvider: GenerationProvider,
  runtimeConfig?: RuntimeConfigLike,
): 'demo' | 'ai' | 'warning' | 'auto' {
  if (selectedProvider === 'demo') return 'demo';

  if (selectedProvider === 'wanxiang') {
    return runtimeConfig?.wanxiang_configured ? 'ai' : 'warning';
  }

  if (runtimeConfig?.demo_mode) return 'demo';
  if (runtimeConfig?.image_provider === 'wanxiang') return 'ai';

  return 'auto';
}

/** CSS classes for each tone. */
export function getGenerationModeBadgeClass(tone: 'demo' | 'ai' | 'warning' | 'auto'): string {
  switch (tone) {
    case 'demo':
      return 'bg-amber-900/60 text-amber-300 border-amber-700';
    case 'ai':
      return 'bg-green-900/60 text-green-300 border-green-700';
    case 'warning':
      return 'bg-amber-900/60 text-amber-300 border-amber-700';
    case 'auto':
      return 'bg-blue-900/60 text-blue-300 border-blue-700';
  }
}
