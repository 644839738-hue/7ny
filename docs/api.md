# API Documentation — SpriteForge AI

## 基础信息

| 项目 | 内容 |
|------|------|
| Base URL | `http://127.0.0.1:8001` |
| Content-Type | `application/json` |
| 文件上传 | `multipart/form-data` |
| 文档地址 | `http://127.0.0.1:8001/docs` （Swagger UI 自动生成） |
| DEMO 模式 | 默认开启，无需外部 API key |

## 通用约定

### 错误响应格式

所有接口在出错时返回以下格式：

```json
{
  "error": {
    "code": "INVALID_ASSET_TYPE",
    "message": "asset_type 必须是 character / prop / tile / ui 之一"
  }
}
```

### 素材对象（Asset）

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "asset_type": "character",
  "size": 32,
  "style": "pixel",
  "image_url": "/output/550e8400.png",
  "thumbnail_url": "/output/550e8400_thumb.png",
  "metadata": {
    "prompt": "a brave knight",
    "generated_at": "2026-05-23T10:30:00Z",
    "generation_mode": "demo"
  }
}
```

---

## 接口列表

### 1. 创建素材生成任务

```
POST /api/generate
```

提交素材生成请求，立即返回任务 ID。通过 `GET /api/tasks/{task_id}` 轮询结果。

**Request Body:**

```json
{
  "project_name": "my-game",
  "asset_type": "character",
  "prompt": "a brave knight with sword",
  "style": "pixel_art",
  "size": 32,
  "count": 4,
  "target_engine": "unity",
  "transparent_background": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_name | string | 是 | 项目名称，1-100 字符 |
| asset_type | string | 是 | 素材类型：`character` / `item` / `tile` / `ui` |
| prompt | string | 是 | 文本描述，1-500 字符 |
| style | string | 否 | 美术风格：`pixel_art` / `cartoon` / `dark_fantasy`，默认 `pixel_art` |
| size | int | 否 | 像素尺寸：`32` / `64` / `128`，默认 `32` |
| count | int | 否 | 生成数量，1-16，默认 `4` |
| target_engine | string | 否 | 目标引擎：`unity` / `godot` / `generic`，默认 `unity` |
| transparent_background | bool | 否 | 是否透明背景，默认 `true` |

**Response (200):**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "message": "Task created"
}
```

> **DEMO 模式**：任务同步完成，`status` 直接返回 `ready`。

---

### 2. 查询任务状态

```
GET /api/tasks/{task_id}
```

轮询任务进度，任务完成时返回生成的素材列表。

**Response (200) — 进行中:**

```json
{
  "task_id": "550e8400-...",
  "status": "generating",
  "progress": "2/4 assets generated",
  "assets": [],
  "created_at": "2026-05-23T10:30:00Z",
  "error": null
}
```

**Response (200) — 已完成:**

```json
{
  "task_id": "550e8400-...",
  "status": "ready",
  "progress": "4/4 assets generated (demo)",
  "assets": [
    {
      "id": "uuid-1",
      "name": "character_32x32_1",
      "type": "character",
      "width": 32,
      "height": 32,
      "image_url": "/output/uuid-1.png",
      "metadata": {
        "prompt": "a brave knight with sword",
        "generated_at": "2026-05-23T10:30:01Z",
        "generation_mode": "demo"
      }
    }
  ],
  "created_at": "2026-05-23T10:30:00Z",
  "error": null
}
```

**Response (404):**

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "No task with id 'nonexistent'"
  }
}
```

---

### 3. 素材后处理

```
POST /api/process
```

对已生成的素材执行透明背景移除、空白裁剪、尺寸标准化、主体居中。

**Request Body:**

```json
{
  "asset_ids": ["uuid-1", "uuid-2"]
}
```

**Response (200):**

```json
{
  "processed": [
    {
      "id": "uuid-1",
      "processed_url": "/output/uuid-1_processed.png",
      "original_size": [48, 56],
      "processed_size": [32, 32],
      "crop_box": [8, 12, 40, 44],
      "center_offset": [0, 0]
    }
  ]
}
```

---

### 4. Sprite Sheet 拼接

```
POST /api/spritesheet
```

将已生成的素材帧拼接为单张 Sprite Sheet，同时生成 JSON 元数据文件（含帧坐标与动画信息）。

**Request Body:**

```json
{
  "asset_ids": ["uuid-1", "uuid-2", "uuid-3", "uuid-4"],
  "animation_name": "walk_right",
  "frame_width": 32,
  "frame_height": 32,
  "fps": 12,
  "columns": 4
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asset_ids | string[] | 是 | 已生成素材的 ID 列表，1-64 个 |
| animation_name | string | 否 | 动画名称，默认 `"default"` |
| frame_width | int | 否 | 帧宽（px），默认 32 |
| frame_height | int | 否 | 帧高（px），默认 32 |
| fps | int | 否 | 帧率，默认 12 |
| columns | int | 否 | 每行列数，默认 4 |

**Response (200):**

```json
{
  "spritesheet_url": "/output/spritesheet_uuid.png",
  "spritesheet_size": [128, 32],
  "frames": [
    { "index": 0, "x": 0, "y": 0, "width": 32, "height": 32 },
    { "index": 1, "x": 32, "y": 0, "width": 32, "height": 32 },
    { "index": 2, "x": 64, "y": 0, "width": 32, "height": 32 },
    { "index": 3, "x": 96, "y": 0, "width": 32, "height": 32 }
  ],
  "metadata_url": "/output/spritesheet_uuid.json",
  "animation_name": "walk_right",
  "frame_width": 32,
  "frame_height": 32,
  "frame_count": 4,
  "fps": 12
}
```

**JSON 元数据文件内容：**

```json
{
  "animation_name": "walk_right",
  "frame_width": 32,
  "frame_height": 32,
  "frame_count": 4,
  "columns": 4,
  "rows": 1,
  "fps": 12,
  "spritesheet_size": [128, 32],
  "animations": {
    "walk_right": { "from": 0, "to": 3, "fps": 12 }
  },
  "frames": [
    { "index": 0, "x": 0, "y": 0, "width": 32, "height": 32 }
  ]
}
```

---

### 5. Tile 3×3 平铺预览

```
POST /api/tile/preview
```

将单张 Tile 素材拼接为 3×3 网格，用于检查平铺效果。

**Request Body:**

```json
{
  "asset_id": "uuid-tile-1"
}
```

**Response (200):**

```json
{
  "tile_preview_url": "/output/tile_preview_uuid.png",
  "tile_size": [32, 32],
  "preview_size": [96, 96]
}
```

---

### 6. Tile 边缘一致性评分

```
POST /api/tile/score
```

检测 Tile 四边（上/下/左/右）的像素 RGB 均值差异，给出 0-100 的无缝性评分。分数越高代表平铺后边缘过渡越自然。

**Request Body:**

```json
{
  "asset_id": "uuid-tile-1"
}
```

**Response (200):**

```json
{
  "score": 87,
  "edge_scores": {
    "top_bottom_consistency": 92,
    "left_right_consistency": 82
  },
  "overall_rating": "good",
  "details": {
    "top_edge_mean_rgb": [128, 64, 32],
    "bottom_edge_mean_rgb": [130, 62, 34],
    "left_edge_mean_rgb": [128, 64, 32],
    "right_edge_mean_rgb": [140, 70, 40]
  }
}
```

| 评分区间 | 评级 | 含义 |
|---------|------|------|
| 90-100 | excellent | 无缝平铺，可直接使用 |
| 70-89 | good | 轻微接缝，建议微调 |
| 50-69 | fair | 可见接缝，需手动修 |
| < 50 | poor | 明显断裂，建议重新生成 |

---

### 7. ZIP 导出

```
POST /api/export
```

将所有指定素材打包为 ZIP，按照 Unity 或 Godot 的目录约定组织。

**Request Body:**

```json
{
  "asset_ids": ["uuid-1", "uuid-2", "uuid-tile-1"],
  "engine": "unity",
  "include_spritesheet": true,
  "include_metadata": true,
  "include_tile_preview": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asset_ids | string[] | 是 | 要导出的素材 ID 列表 |
| engine | string | 是 | 目标引擎：`unity` 或 `godot` |
| include_spritesheet | bool | 否 | 是否包含 Sprite Sheet，默认 true |
| include_metadata | bool | 否 | 是否包含 JSON 元数据，默认 true |
| include_tile_preview | bool | 否 | 是否包含 Tile 平铺预览，默认 true |

**Response (200):**

```json
{
  "download_url": "/output/spriteforge_export_20260523_103000.zip",
  "package_structure": {
    "engine": "unity",
    "files": [
      "Assets/Sprites/character_001.png",
      "Assets/Sprites/prop_001.png",
      "Assets/Sprites/tile_001.png",
      "Assets/Sprites/spritesheet.png",
      "Assets/Sprites/spritesheet.json",
      "Assets/Sprites/tile_preview.png"
    ]
  },
  "file_count": 6,
  "total_size_bytes": 245760
}
```

**导出目录结构：**

```
# Unity 导出
spriteforge_export_20260523_103000.zip
└── Assets/
    └── Sprites/
        ├── character_001.png
        ├── character_001.png.meta
        ├── spritesheet.png
        └── spritesheet.json

# Godot 导出
spriteforge_export_20260523_103000.zip
└── assets/
    └── sprites/
        ├── character_001.png
        ├── character_001.png.import
        ├── spritesheet.png
        └── spritesheet.json
```

---

### 8. 列出已生成素材

```
GET /api/assets
```

**Response (200):**

```json
{
  "assets": [ ... ],
  "total": 4
}
```
