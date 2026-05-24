import type { AssetListResponse, ExportRequest, ExportResult, GeneratedAssetRecord, GenerateParams, RuntimeConfig, SpriteSheet, SpriteSheetRequest, TilePreview, TilePreviewRequest, TileScore, TileScoreRequest } from '../types';
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

/** Fetch the backend runtime config (provider status, mode, etc.). */
export function getRuntimeConfig() {
  return request<RuntimeConfig>('/runtime-config');
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
      generation_provider: params.generationProvider,
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

/** Score a tile's edge consistency for seamless tiling. */
export function checkTileScore(params: TileScoreRequest) {
  return request<TileScore>('/tile/score', {
    method: 'POST',
    body: JSON.stringify({
      asset_id: params.assetId,
    }),
  });
}

/** Build a 3x3 tiling preview for a tile asset. */
export function buildTilePreview(params: TilePreviewRequest) {
  return request<TilePreview>('/tile/preview', {
    method: 'POST',
    body: JSON.stringify({
      asset_id: params.assetId,
    }),
  });
}

/** List generated asset history records. */
export function listAssets(params?: {
  asset_type?: string;
  project_name?: string;
  limit?: number;
  offset?: number;
}) {
  const qs = new URLSearchParams();
  if (params?.asset_type) qs.set('asset_type', params.asset_type);
  if (params?.project_name) qs.set('project_name', params.project_name);
  if (params?.limit != null) qs.set('limit', String(params.limit));
  if (params?.offset != null) qs.set('offset', String(params.offset));
  const query = qs.toString();
  return request<AssetListResponse>(`/assets${query ? `?${query}` : ''}`);
}

/** Get a single asset record by ID. */
export function getAsset(assetId: string) {
  return request<GeneratedAssetRecord>(`/assets/${assetId}`);
}

/** Delete an asset record by ID. */
export function deleteAsset(assetId: string) {
  return request<{ ok: boolean }>(`/assets/${assetId}`, { method: 'DELETE' });
/** Fetch backend runtime generation config. */
export function getRuntimeConfig() {
  return request<RuntimeConfig>('/runtime-config');
}

/** Export assets as a ZIP package for a target engine. */
export function exportPackage(params: ExportRequest) {
  return request<ExportResult>('/export', {
    method: 'POST',
    body: JSON.stringify({
      project_name: params.projectName,
      asset_ids: params.assetIds,
      engine: params.engine,
      include_spritesheet: params.includeSpritesheet,
      include_metadata: params.includeMetadata,
      include_tile_preview: params.includeTilePreview,
    }),
  });
}
