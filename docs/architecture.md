# Architecture — SpriteForge AI

## 总体架构

```
┌─────────────┐     HTTP/REST     ┌─────────────┐
│   Frontend   │ ◄──────────────► │   Backend    │
│  React+Vite  │                   │  FastAPI     │
│  TypeScript  │                   │  Python      │
└─────────────┘                   └──────┬───────┘
                                         │
                                   ┌─────▼───────┐
                                   │   Services   │
                                   │ Generator    │
                                   │ Processor    │
                                   │ Spritesheet  │
                                   │ TileChecker  │
                                   │ Packager     │
                                   └─────────────┘
```

## 前端架构

- **框架**：React 18 + Vite + TypeScript + Tailwind CSS
- **状态管理**：React Hooks（MVP 阶段无需 Redux）
- **路由**：React Router（Home / About）

### 组件树

```
App
├── Header
├── HomePage
│   ├── Sidebar
│   │   ├── PromptInput
│   │   ├── AssetTypePicker
│   │   └── StyleParams
│   ├── AssetGallery
│   │   ├── AssetCard
│   │   ├── SpriteSheetView
│   │   └── TilePreview
│   └── ExportPanel
└── AboutPage
```

## 后端架构

- **框架**：FastAPI + Pydantic
- **图像处理**：Pillow + OpenCV
- **AI 生成**：可配置 Provider 模式，DEMO 模式下使用内置素材

### API 路由

| 路径 | 方法 | 说明 |
|------|------|------|
| /api/generate | POST | 生成素材 |
| /api/process | POST | 后处理 |
| /api/spritesheet | POST | Sprite Sheet 拼接 |
| /api/tile/preview | POST | Tile 3×3 平铺 |
| /api/tile/score | POST | Tile 边缘评分 |
| /api/export | POST | ZIP 导出 |

## DEMO 模式

前端通过 `VITE_DEMO_MODE=true` 环境变量控制。
后端通过 `config.py` 中的 `DEMO_MODE` 控制。
DEMO 模式下，所有 API 返回 `examples/sample-assets/` 中的预置素材。

> 本文档随开发进度持续更新。
