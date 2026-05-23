# Architecture — SpriteForge AI

## 设计原则

1. **前后端分离**：前端只负责 UI 与用户交互，所有图像处理逻辑在后端完成
2. **管线化设计**：生成 → 处理 → 拼接 → 检测 → 导出，每环节独立可替换
3. **Provider 抽象**：AI 生成层可插拔，DEMO / 真实 API 实现同一接口
4. **引擎感知导出**：导出模块理解 Unity 和 Godot 的目录约定

## 总体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ Sidebar │ │ Gallery  │ │ SpriteSheet  │ │ ExportPanel    │  │
│  │ (参数)   │ │ (预览)   │ │ View (帧预览) │ │ (导出)         │  │
│  └────┬────┘ └────┬─────┘ └──────┬───────┘ └───────┬────────┘  │
│       └───────────┴──────────────┴───────────────┘             │
│                          │ api.ts                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP REST
┌──────────────────────────┼──────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐   │
│  │                     Routers                               │   │
│  │  /generate  /process  /spritesheet  /tile/*  /export     │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐   │
│  │                   Services Layer                          │   │
│  │                                                           │   │
│  │  Generator ──► Processor ──► SpriteSheet ──► Packager    │   │
│  │      │                                      │             │   │
│  │      ├── AIGenerator (real API)             │             │   │
│  │      └── DemoGenerator (built-in assets)    │             │   │
│  │                                             │             │   │
│  │                    TileChecker ─────────────┘             │   │
│  │                    (preview + scoring)                     │   │
│  └───────────────────────────────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────▼──────────────────────────────────┐   │
│  │                     Utils                                 │   │
│  │  image_utils.py  demo_provider.py                        │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## 处理管线（Pipeline）

这是 SpriteForge AI 区别于普通文生图工具的核心设计：

```
 Step 1           Step 2            Step 3           Step 4          Step 5
┌─────────┐     ┌──────────┐      ┌──────────┐     ┌──────────┐    ┌──────────┐
│ Generate │────►│ Process  │─────►│ Sprite   │────►│ Tile     │───►│ Package  │
│          │     │          │      │ Sheet    │     │ Check    │    │ & Export │
│ · prompt │     │· 透明背景 │      │· 拼接     │     │· 3×3预览  │    │· ZIP打包  │
│ · type   │     │· 裁剪空白 │      │· JSON元数据│    │· 边缘评分 │    │· 引擎适配 │
│ · size   │     │· 标准化   │      │          │     │          │    │          │
│ · style  │     │· 主体居中 │      │          │     │          │    │          │
└─────────┘     └──────────┘      └──────────┘     └──────────┘    └──────────┘
     │                                                                    │
     │              DEMO 模式下跳过 AI，直接用内置素材                      │
     └────────────────────────────────────────────────────────────────────┘
```

## 前端架构

### 技术选型

| 技术 | 选型理由 |
|------|----------|
| React 18 | 生态成熟，组件化开发高效 |
| Vite | 极速 HMR，TypeScript 原生支持 |
| TypeScript | 类型安全，便于评审 |
| Tailwind CSS | 原子化样式，快速构建 UI |
| React Router | SPA 路由，轻量级 |

### 组件树

```
App
├── Header                        # 顶部导航栏
│   └── DEMO_MODE 状态指示器
├── HomePage                      # 主工作台
│   ├── Sidebar                   # 左侧参数面板
│   │   ├── PromptInput           #   文本 prompt 输入框
│   │   ├── AssetTypePicker       #   四类素材选择（角色/道具/Tile/UI）
│   │   ├── StyleParams           #   尺寸 32/64 + 像素风开关
│   │   └── GenerateButton        #   生成按钮 + Loading 状态
│   ├── ContentArea               # 中间预览区
│   │   ├── AssetGallery          #   素材画廊（Grid 布局）
│   │   │   └── AssetCard         #     单素材卡片 + 操作菜单
│   │   ├── SpriteSheetView       #   Spritesheet 预览 + 帧边界标注
│   │   └── TilePreview           #   3×3 平铺预览 + 评分展示
│   └── ExportPanel               # 右侧导出面板
│       ├── EngineSelector        #   Unity / Godot 选择
│       └── DownloadButton        #   下载 ZIP
└── AboutPage                     # 关于页
```

### 状态管理

MVP 阶段使用 React 内置 Hooks，无需引入状态管理库：

- `useGenerateAsset` — 管理生成请求状态（idle / loading / success / error）
- `useExport` — 管理导出下载状态
- 组件间通过 props 传递，不做全局状态

## 后端架构

### 技术选型

| 技术 | 选型理由 |
|------|----------|
| FastAPI | 高性能异步框架，自动生成 Swagger 文档 |
| Pydantic v2 | 类型校验 + JSON Schema 生成 |
| Pillow | 纯 Python 图像处理，覆盖所有需求 |
| OpenCV | Tile 边缘检测（可选，Pillow 也可实现） |

### API 路由设计

| 路径 | 方法 | 说明 | 依赖管线步骤 |
|------|------|------|-------------|
| `/api/generate` | POST | 生成原始素材 | Step 1 |
| `/api/process` | POST | 后处理（透明/裁剪/标准化） | Step 2 |
| `/api/spritesheet` | POST | Sprite Sheet 拼接 + JSON 元数据 | Step 3 |
| `/api/tile/preview` | POST | Tile 3×3 平铺预览 | Step 4 |
| `/api/tile/score` | POST | Tile 边缘一致性评分 | Step 4 |
| `/api/export` | POST | ZIP 打包导出 | Step 5 |
| `/api/assets` | GET | 列出已生成的素材 | — |

### Provider 模式（AI 生成层抽象）

```python
# 抽象接口
class GeneratorProvider(ABC):
    @abstractmethod
    def generate(self, prompt, asset_type, size, style, count) -> list[Asset]: ...

# DEMO 实现
class DemoGenerator(GeneratorProvider):
    # 从 examples/sample-assets/ 加载预置素材
    ...

# 真实 AI 实现
class AIGenerator(GeneratorProvider):
    # 调用外部 AI API
    ...
```

### 目录约定

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 全局配置 + DEMO_MODE 开关
│   ├── routers/             # 路由层——薄层，只做参数接收和响应
│   ├── services/            # 服务层——业务逻辑
│   ├── models/              # Pydantic schemas
│   └── utils/               # 工具函数
├── output/                  # 运行时输出目录（.gitignore）
├── uploads/                 # 上传文件暂存（.gitignore）
└── requirements.txt
```

## DEMO 模式架构

```
DEMO_MODE=true (默认)
     │
     ├── 前端：VITE_DEMO_MODE=true
     │   └── UI 顶部显示 「DEMO 模式」指示器
     │
     └── 后端：config.DEMO_MODE = True
         └── GeneratorProvider = DemoGenerator
             └── 读取 examples/sample-assets/ 下预置素材
                 ├── characters/   # 角色素材（.png）
                 ├── props/       # 道具素材（.png）
                 ├── tiles/       # Tile 素材（.png）
                 └── ui/          # UI 素材（.png）
```

DEMO 模式的关键设计决策：
- 前后端**独立控制**：前端可通过环境变量切换 UI 状态，后端通过配置切换生成逻辑
- DemoGenerator 产出的数据结构与 AIGenerator **完全一致**，确保上层调用无感知
- 内置素材覆盖四类+双尺寸，可充分验证管线

## 安全设计

- 文件上传限制：仅允许 PNG，最大 5MB
- 路径穿越防护：所有文件路径使用 `os.path.basename` 消毒
- CORS 限制：开发环境下仅允许 `localhost:5173`
- 生成数量限制：单次最多 16 张
