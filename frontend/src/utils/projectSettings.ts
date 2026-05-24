import type { ProjectSettings } from '../types';

const STORAGE_KEY = 'spriteforge_project_settings';

const DEFAULTS: ProjectSettings = {
  projectName: 'Dark Dungeon Demo',
  defaultAssetType: 'item',
  defaultStyle: 'pixel_art',
  defaultSize: 32,
  defaultCount: 1,
  defaultTargetEngine: 'godot',
  transparentBackground: true,
  generationProvider: 'auto',
};

export function getProjectSettings(): ProjectSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return { ...DEFAULTS, ...JSON.parse(raw) };
    }
  } catch {
    // corrupted data — fall through to defaults
  }
  return { ...DEFAULTS };
}

export function saveProjectSettings(settings: ProjectSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export function resetProjectSettings(): ProjectSettings {
  localStorage.removeItem(STORAGE_KEY);
  return { ...DEFAULTS };
}
