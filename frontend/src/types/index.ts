/** Asset category */
export type AssetType = 'character' | 'prop' | 'tile' | 'ui';

/** Pixel size presets */
export type PixelSize = 32 | 64;

/** Target game engine for export */
export type EngineType = 'unity' | 'godot';

/** Generation request parameters */
export interface GenerateParams {
  prompt: string;
  assetType: AssetType;
  size: PixelSize;
  style: string;
  count: number;
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

/** Sprite sheet result */
export interface SpriteSheet {
  spritesheetUrl: string;
  spritesheetSize: [number, number];
  frames: SpriteFrame[];
  metadataUrl: string;
}

/** Tile edge consistency score */
export interface TileScore {
  score: number;
  edgeScores: {
    topBottomConsistency: number;
    leftRightConsistency: number;
  };
  overallRating: 'excellent' | 'good' | 'fair' | 'poor';
}

/** Tile 3x3 preview */
export interface TilePreview {
  tilePreviewUrl: string;
  tileSize: [number, number];
  previewSize: [number, number];
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
