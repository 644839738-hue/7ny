/** Asset category */
export type AssetType = 'character' | 'item' | 'tile' | 'ui';

/** Visual style presets */
export type ArtStyle = 'pixel_art' | 'cartoon' | 'dark_fantasy';

/** Pixel size presets */
export type PixelSize = 32 | 64 | 128;

/** Target game engine for export */
export type EngineType = 'unity' | 'godot' | 'generic';

/** Generation provider choice */
export type GenerationProvider = 'auto' | 'demo' | 'wanxiang';

/** Generation request parameters */
export interface GenerateParams {
  projectName: string;
  assetType: AssetType;
  prompt: string;
  style: ArtStyle;
  size: PixelSize;
  count: number;
  targetEngine: EngineType;
  transparentBackground: boolean;
  generationProvider: GenerationProvider;
}

/** Project settings persisted to localStorage */
export interface ProjectSettings {
  projectName: string;
  defaultAssetType: AssetType;
  defaultStyle: ArtStyle;
  defaultSize: PixelSize;
  defaultCount: number;
  defaultTargetEngine: EngineType;
  transparentBackground: boolean;
  generationProvider: GenerationProvider;
}

/** Runtime config from GET /api/runtime-config */
export interface RuntimeConfig {
  demo_mode: boolean;
  image_provider: string;
  ai_enabled: boolean;
  provider_label: string;
}

/** A single generated asset */
export interface Asset {
  id: string;
  assetType: AssetType;
  size: PixelSize;
  style: string;
  imageUrl: string;
  thumbnailUrl: string;
  metadata: AssetMetadata;
}

export interface AssetMetadata {
  prompt: string;
  generatedAt: string;
  generationMode: 'demo' | 'ai';
}

/** Sprite sheet frame info */
export interface SpriteFrame {
  index: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

/** Sprite sheet request */
export interface SpriteSheetRequest {
  assetIds: string[];
  animationName: string;
  frameWidth: number;
  frameHeight: number;
  fps: number;
  columns: number;
}

/** Sprite sheet result */
export interface SpriteSheet {
  spritesheetUrl: string;
  spritesheetSize: [number, number];
  frames: SpriteFrame[];
  metadataUrl: string;
  animationName: string;
  frameWidth: number;
  frameHeight: number;
  frameCount: number;
  fps: number;
}

/** Tile preview request */
export interface TilePreviewRequest {
  assetId: string;
}

/** Tile 3x3 preview */
export interface TilePreview {
  tilePreviewUrl: string;
  tileSize: [number, number];
  previewSize: [number, number];
}

/** Tile score request */
export interface TileScoreRequest {
  assetId: string;
}

/** Tile edge consistency score */
export interface TileScore {
  score: number;
  edgeScores: {
    topBottomConsistency: number;
    leftRightConsistency: number;
  };
  overallRating: 'excellent' | 'good' | 'fair' | 'poor';
  suggestion: string;
}

/** Export request */
export interface ExportRequest {
  projectName: string;
  assetIds: string[];
  engine: EngineType;
  includeSpritesheet: boolean;
  includeMetadata: boolean;
  includeTilePreview: boolean;
}

/** Export result */
export interface ExportResult {
  downloadUrl: string;
  packageStructure: {
    engine: EngineType;
    files: string[];
  };
  fileCount: number;
  totalSizeBytes: number;
}

/** API error response */
export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

/** Navigation tabs */
export type NavTab =
  | 'dashboard'
  | 'settings'
  | 'generator'
  | 'spritesheet'
  | 'tile'
  | 'export';
