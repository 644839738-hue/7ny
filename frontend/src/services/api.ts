import type { GenerateParams, SpriteSheet, SpriteSheetRequest, TilePreview, TilePreviewRequest } from '../types';
import { API_BASE } from '../config/demo';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body?.error?.message || `HTTP ${resp.status}`);
  }
  return resp.json();
}

/** Submit a generation request, returns { task_id, status }. */
export function generateAssets(params: GenerateParams) {
  return request<{ task_id: string; status: string }>('/generate', {
    method: 'POST',
    body: JSON.stringify({
      project_name: params.projectName,
      asset_type: params.assetType,
      prompt: params.prompt,
      style: params.style,
      size: params.size,
      count: params.count,
      target_engine: params.targetEngine,
      transparent_background: params.transparentBackground,
    }),
  });
}

/** Poll task status and get assets when ready. */
export function getTask(taskId: string) {
  return request<{
    task_id: string;
    status: string;
    assets: {
      id: string;
      name: string;
      type: string;
      width: number;
      height: number;
      image_url: string;
      metadata: Record<string, unknown>;
    }[];
    error?: string;
    warning?: string;
  }>(`/tasks/${taskId}`);
}

/** Build a sprite-sheet from existing asset IDs. */
export function buildSpriteSheet(params: SpriteSheetRequest) {
  return request<SpriteSheet>('/spritesheet', {
    method: 'POST',
    body: JSON.stringify({
      asset_ids: params.assetIds,
      animation_name: params.animationName,
      frame_width: params.frameWidth,
      frame_height: params.frameHeight,
      fps: params.fps,
      columns: params.columns,
    }),
  });
}

/** Build a 3×3 tiling preview for a tile asset. */
export function buildTilePreview(params: TilePreviewRequest) {
  return request<TilePreview>('/tile/preview', {
    method: 'POST',
    body: JSON.stringify({
      asset_id: params.assetId,
    }),
  });
}
