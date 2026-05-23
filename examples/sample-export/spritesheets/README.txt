This directory would contain generated Sprite Sheet files.

In a real "Dark Dungeon" export, you would find:
  - spritesheet_knight_walk.png  — the sprite sheet image (128×32 for 4 frames of 32×32)
  - spritesheet_knight_walk.json — frame coordinates and animation metadata

The JSON metadata includes:
  - animation_name, fps, frame_width, frame_height
  - frames[] array with x, y, width, height for each frame
  - animations{} dict with from/to range for each animation clip
