"""
Export service — bundle assets into a ZIP for Unity / Godot / Generic.

Produces a zip with the following structure::

    /images/           — individual asset images
    /spritesheets/     — sprite-sheet PNG + JSON  (optional)
    /tiles/            — tile preview PNGs         (optional)
    manifest.json      — asset catalogue
    README_IMPORT.md   — engine-specific import instructions
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import OUTPUT_DIR
from app.models.schemas import EngineType


def _find_asset_file(asset_id: str) -> Optional[Path]:
    """Locate an asset file in OUTPUT_DIR by its UUID stem."""
    for candidate in Path(OUTPUT_DIR).iterdir():
        if candidate.is_file() and candidate.stem == asset_id:
            return candidate
    return None


# ---------------------------------------------------------------------------
# README templates
# ---------------------------------------------------------------------------

_README_UNITY = """\
# SpriteForge Export — Unity 导入说明

## 目录结构

```
Assets/
└── Sprites/
    ├── *.png          ← 导入此处
    ├── *.png.meta     ← Unity 自动生成，无需关注
    ├── spritesheet.png
    └── spritesheet.json
```

## 导入步骤

1. 将 `images/` 目录中的 PNG 文件拖放至 Unity 的 `Assets/Sprites/` 文件夹。
2. 选中每张素材，在 Inspector 面板中设置：
   - **Texture Type**: Sprite (2D and UI)
   - **Filter Mode**: Point (no filter)   ← 像素风务必关闭平滑
   - **Compression**: None
   - **Pixels Per Unit**: 与素材尺寸一致（如 32）
3. 若使用 Sprite Sheet：
   - 将 `spritesheets/spritesheet.png` 拖入 `Assets/Sprites/`
   - 设置 **Sprite Mode** = Multiple
   - 点击 **Sprite Editor** → Slice → Grid by Cell Size → Apply
   - 动画片段参考 `spritesheets/spritesheet.json` 中的帧坐标
4. 创建 Animation Clip：Window → Animation → Animation → 拖入帧序列

## 额外说明

- `.meta` 文件由 Unity 自动生成，导出包中未包含，导入后自动创建
- 如需透明背景，请在 Sprite 导入设置中勾选 **Alpha Is Transparency**
"""

_README_GODOT = """\
# SpriteForge Export — Godot 导入说明

## 目录结构

```
assets/
└── sprites/
    ├── *.png          ← 导入此处
    ├── *.png.import   ← Godot 自动生成
    ├── spritesheet.png
    └── spritesheet.json
```

## 导入步骤

1. 将 `images/` 目录中的 PNG 文件复制到 Godot 项目的 `assets/sprites/` 文件夹。
2. 在 Godot 文件系统面板中选中每张素材，在 Import 面板中设置：
   - **Filter**: 取消勾选   ← 像素风必须关闭纹理过滤
   - **Mipmaps**: 取消勾选
   - **Compress**: Lossless
3. 若使用 Sprite Sheet：
   - 将 `spritesheets/spritesheet.png` 复制到同一目录
   - 创建 `Sprite2D` 节点，将 spritesheet.png 拖到 Texture 属性
   - 在 Inspector 中设置 **Region** = Enabled
   - 参考 `spritesheets/spritesheet.json` 中的帧坐标调整 region rect
4. 动画设置：
   - 创建 `AnimationPlayer` 节点
   - 或使用 `AnimatedSprite2D` 添加 `SpriteFrames` 资源
   - 按 `spritesheet.json` 中的 fps 切分帧序列

## 额外说明

- `.import` 文件由 Godot 自动生成，导出包中未包含
- 透明背景 PNG 在 Godot 中自动识别，无需额外设置
"""

_README_GENERIC = """\
# SpriteForge Export — 通用导入说明

## 目录结构

```
images/           — 独立素材图片（PNG 格式，RGBA 透明）
spritesheets/     — Sprite Sheet 拼接图 + JSON 元数据
tiles/            — Tile 3×3 平铺预览
manifest.json     — 素材清单
```

## 素材格式

| 属性 | 值 |
|------|-----|
| 格式 | PNG |
| 色彩 | RGBA (含透明通道) |
| 像素尺寸 | 32 / 64 / 128 px |

## 引擎适配建议

### Unity
- 导入至 `Assets/Sprites/`
- Texture Type → Sprite (2D and UI)
- Filter Mode → Point (像素风不模糊)

### Godot
- 导入至项目 `assets/sprites/`
- Import 面板 → Filter 取消勾选
- Compress → Lossless

### RPG Maker / GameMaker / 其他
- 直接使用 `images/` 下的 PNG 文件
- 像素对齐：确保引擎关闭纹理平滑/抗锯齿

## JSON 元数据

每张素材的生成参数、尺寸、处理记录均在 `manifest.json` 中。
Sprite Sheet 帧坐标见 `spritesheets/spritesheet.json`。
"""

_READMES: dict[EngineType, str] = {
    EngineType.UNITY: _README_UNITY,
    EngineType.GODOT: _README_GODOT,
    EngineType.GENERIC: _README_GENERIC,
}


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------


def build_export(
    project_name: str,
    asset_ids: list[str],
    engine: EngineType,
    include_spritesheet: bool = True,
    include_metadata: bool = True,
    include_tile_preview: bool = True,
) -> dict:
    """Bundle assets into a ZIP archive and return the response dict."""

    # Collect asset files
    asset_files: list[tuple[str, Path]] = []  # (asset_id, full_path)
    for aid in asset_ids:
        fp = _find_asset_file(aid)
        if fp is not None:
            asset_files.append((aid, fp))

    # Collect spritesheet files from OUTPUT_DIR
    ss_files: list[Path] = []
    if include_spritesheet:
        for candidate in Path(OUTPUT_DIR).iterdir():
            if not candidate.is_file():
                continue
            if candidate.stem.startswith("spritesheet_"):
                ss_files.append(candidate)

    # Collect tile preview files from OUTPUT_DIR
    tile_files: list[Path] = []
    if include_tile_preview:
        for candidate in Path(OUTPUT_DIR).iterdir():
            if not candidate.is_file():
                continue
            if candidate.stem.startswith("tile_preview_"):
                tile_files.append(candidate)

    # Build ZIP in memory, then write to OUTPUT_DIR
    zip_bytes: bytes
    file_list: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # ---- images/ ----
        images_dir = root / "images"
        images_dir.mkdir()
        for aid, src in asset_files:
            dst = images_dir / src.name
            dst.write_bytes(src.read_bytes())
            file_list.append(f"images/{src.name}")

        # ---- spritesheets/ ----
        if ss_files:
            ss_dir = root / "spritesheets"
            ss_dir.mkdir()
            for src in ss_files:
                dst = ss_dir / src.name
                dst.write_bytes(src.read_bytes())
                file_list.append(f"spritesheets/{src.name}")

        # ---- tiles/ ----
        if tile_files:
            tiles_dir = root / "tiles"
            tiles_dir.mkdir()
            for src in tile_files:
                dst = tiles_dir / src.name
                dst.write_bytes(src.read_bytes())
                file_list.append(f"tiles/{src.name}")

        # ---- manifest.json ----
        manifest = {
            "project_name": project_name,
            "target_engine": engine.value,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "assets": [
                {
                    "id": aid,
                    "file_path": f"images/{src.name}",
                }
                for aid, src in asset_files
            ],
            "spritesheets": [
                f"spritesheets/{p.name}" for p in ss_files
            ],
            "tiles": [
                f"tiles/{p.name}" for p in tile_files
            ],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        file_list.append("manifest.json")

        # ---- README_IMPORT.md ----
        readme = _READMES.get(engine, _README_GENERIC)
        readme_path = root / "README_IMPORT.md"
        readme_path.write_text(readme, encoding="utf-8")
        file_list.append("README_IMPORT.md")

        # ---- ZIP ----
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for frel in file_list:
                zf.write(root / frel, frel)
        zip_bytes = zip_buf.getvalue()

    # Write ZIP to OUTPUT_DIR
    export_id = str(uuid.uuid4())
    zip_filename = f"export_{export_id}.zip"
    zip_path = Path(OUTPUT_DIR) / zip_filename
    zip_path.write_bytes(zip_bytes)

    return {
        "download_url": f"/output/{zip_filename}",
        "package_structure": {
            "engine": engine.value,
            "files": sorted(file_list),
        },
        "file_count": len(file_list),
        "total_size_bytes": len(zip_bytes),
    }
