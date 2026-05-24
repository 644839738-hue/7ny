# SpriteForge AI

> 面向 2D 游戏开发工作流的 AI 素材生成与资产化管线

---

## 目录

- [1. 项目简介](#1-项目简介)
- [2. 选择题目](#2-选择题目)
- [3. 目标用户](#3-目标用户)
- [4. 核心功能](#4-核心功能)
- [5. 创新点](#5-创新点)
- [6. 技术架构](#6-技术架构)
- [7. 项目结构](#7-项目结构)
- [8. 本地运行方式](#8-本地运行方式)
- [9. Demo 模式说明](#9-demo-模式说明)
- [10. 生成历史与素材库](#10-生成历史与素材库)
- [11. 环境变量说明](#11-环境变量说明)
- [12. 第三方依赖与用途](#12-第三方依赖与用途)
- [13. 原创功能说明](#13-原创功能说明)
- [14. API 文档入口](#14-api-文档入口)
- [15. Demo 视频链接](#15-demo-视频链接)
- [16. PR 与 Commit 规范](#16-pr-与-commit-规范)
- [17. 学术诚信与知识产权说明](#17-学术诚信与知识产权说明)

---

## 1. 项目简介

SpriteForge AI 是一个面向 2D 游戏开发的素材生成与资产化处理工具。用户通过文本描述和简单参数即可生成像素风格的游戏素材（角色、道具、Tile、UI），并自动完成从"生成图像"到"游戏引擎可直接导入的资产"之间的全部工程化处理。

**核心区别**：市面上的 AI 图像生成器（DALL·E、Midjourney、Stable Diffusion 等）产出的图像无法直接用于游戏开发——它们缺少透明背景、尺寸不统一、无 Sprite Sheet 元数据、Tile 边缘可能断裂。SpriteForge AI 在"生成"和"可用"之间架设了一条完整的资产化管线。

本项目为竞赛参赛作品，聚焦于**游戏资产工作流管线的工程实现**，而非 AI 图像生成模型本身。

---

## 2. 选择题目

**题目二：2D 游戏素材生成**

通过文本描述和结构化参数生成像素风格 2D 游戏素材，并自动完成透明背景处理、尺寸标准化、Sprite Sheet 拼接、Tile 无缝检测和引擎适配导出。

---

## 3. 目标用户

| 用户群体 | 场景 | 核心需求 |
|----------|------|----------|
| 独立游戏开发者 | 一人兼顾程序与美术 | 快速产出风格统一的可用素材 |
| 小型 2D 游戏团队（2-5 人） | 有程序但缺美术 | 降低美术产能瓶颈 |
| Game Jam 参赛者 | 48 小时内需大量素材 | 快速迭代，即刻可用 |

---

## 4. 核心功能

### 素材生成

- 支持四种素材类型：**角色（Character）**、**道具（Item）**、**Tile**、**UI**
- 三种美术风格：像素风（pixel_art）、卡通（cartoon）、暗黑幻想（dark_fantasy）
- 三种像素尺寸：32×32、64×64、128×128
- 可配置透明背景、生成数量（1-16）

### 资产化处理管线

| 步骤 | 功能 | 说明 |
|------|------|------|
| 后处理 | 透明背景移除、空白裁剪、尺寸标准化、主体居中 | 将 AI 生成的原始图像处理为规范素材 |
| Sprite Sheet | 多帧拼接为单张 Spritesheet + JSON 帧元数据 | 直出引擎可用格式，含帧坐标和动画信息 |
| Tile 预览 | 单张 Tile 自动拼接为 3×3 平铺预览 | 直观检查平铺效果 |
| Tile 评分 | 检测四边 RGB 差异，输出 0-100 无缝评分 | 量化评估 Tile 质量 |
| 引擎导出 | 按 Unity / Godot / Generic 目录约定打包 ZIP | 含 README_IMPORT.md 导入说明 |

### 前端交互

- 完整 Web UI：素材生成、Sprite Sheet 工具、Tile 预览与检测、导出面板
- Sprite Sheet 动画预览（CSS backgroundPosition 逐帧播放）
- 文件树结构预览
- Demo 模式状态指示器

---

## 5. 创新点

1. **完整资产化管线**：将"AI 生成图像"到"游戏引擎可用资产"的所有处理环节串联为自动化管线，而非单点功能
2. **Tile 边缘一致性评分算法**：基于四边 RGB 均值比对的 Tile 无缝性量化评估，填补 AI 生成 Tile 的质量检测空白
3. **Demo 模式 + 自动回退架构**：前后端均可无外部 API 运行，AI 模式失败时自动回退 Demo，确保流程不中断、项目可复现
4. **引擎感知导出**：根据目标引擎（Unity / Godot）生成对应的目录结构和导入说明文档
5. **Provider 可插拔 AI 层**：通过抽象接口隔离生成后端，Demo / 外部 AI 无感切换

---

## 6. 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React 18)                     │
│  TypeScript + Vite + Tailwind CSS + React Router          │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌────────┐  │
│  │Generator │ │SpriteSheet   │ │Tile      │ │Export  │  │
│  │          │ │Tool          │ │Preview   │ │Page    │  │
│  └────┬─────┘ └──────┬───────┘ └────┬─────┘ └───┬────┘  │
│       └──────────────┴──────────────┴────────────┘       │
│                          │ HTTP REST                       │
└──────────────────────────┼───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│                   Backend (FastAPI)                        │
│                           │                                │
│  ┌────────────────────────▼──────────────────────────┐   │
│  │  Routers: /generate /process /spritesheet           │   │
│  │           /tile/preview /tile/score /export         │   │
│  └────────────────────────┬──────────────────────────┘   │
│                           │                                │
│  ┌────────────────────────▼──────────────────────────┐   │
│  │  Services Layer                                     │   │
│  │  Generator → Processor → SpriteSheet → Tile → ZIP  │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                                │
│  ┌────────────────────────▼──────────────────────────┐   │
│  │  Utils: image_utils.py / demo_provider.py           │   │
│  └────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘

处理管线:
  Step 1: Generate → Step 2: Process → Step 3: SpriteSheet
  → Step 4: Tile Check → Step 5: Export
```

| 层 | 技术 | 用途 |
|----|------|------|
| 前端框架 | React 18 + TypeScript | Web 交互界面 |
| 构建工具 | Vite 5 | 开发服务器与生产构建 |
| 样式 | Tailwind CSS 3 | 原子化 CSS |
| 路由 | React Router 6 | SPA 客户端路由 |
| 后端框架 | FastAPI + Pydantic v2 | REST API 服务 |
| 服务器 | Uvicorn | ASGI 服务器 |
| 图像处理 | Pillow | 透明背景、裁剪、缩放、拼接、边缘检测 |
| 打包 | Python zipfile | ZIP 导出 |

---

## 7. 项目结构

```
spriteforge-ai/
├── frontend/                         # React + Vite + TypeScript + Tailwind
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── layout/               # Header, Sidebar
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # 仪表盘
│   │   │   ├── ProjectSettings.tsx   # 项目设置
│   │   │   ├── AssetGenerator.tsx    # 素材生成表单
│   │   │   ├── SpriteSheetTool.tsx   # Sprite Sheet 工具 + 动画预览
│   │   │   ├── TilePreview.tsx       # Tile 3×3 预览 + 边缘评分
│   │   │   └── ExportPage.tsx        # 引擎导出面板
│   │   ├── services/
│   │   │   └── api.ts                # API 调用封装
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript 类型定义
│   │   ├── config/
│   │   │   └── demo.ts               # DEMO 模式配置
│   │   ├── App.tsx                   # 根组件 + 路由
│   │   └── main.tsx                  # 入口
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts                # 含 API 代理配置
│   └── tailwind.config.js
├── backend/                          # Python FastAPI
│   ├── app/
│   │   ├── main.py                   # 应用入口 + 路由注册
│   │   ├── config.py                 # 环境变量配置
│   │   ├── routers/
│   │   │   ├── health.py             # GET /health, GET /api/runtime-config
│   │   │   ├── generate.py           # POST /api/generate
│   │   │   ├── assets.py             # GET/DELETE /api/assets
│   │   │   ├── process.py            # POST /api/process
│   │   │   ├── spritesheet.py        # POST /api/spritesheet
│   │   │   ├── tile.py               # POST /api/tile/preview + /tile/score
│   │   │   └── export.py             # POST /api/export
│   │   ├── services/
│   │   │   ├── generator.py          # 任务调度
│   │   │   ├── image_generation_service.py  # AI Provider 抽象层
│   │   │   ├── wanxiang_image_provider.py   # 通义万相 Provider
│   │   │   ├── provider_base.py      # Provider 抽象基类
│   │   │   ├── asset_repository.py   # SQLite 素材持久化
│   │   │   ├── processor.py          # 后处理服务
│   │   │   ├── spritesheet.py        # Sprite Sheet 拼接
│   │   │   ├── tile.py               # Tile 3×3 预览
│   │   │   ├── tile_score.py         # Tile 边缘评分
│   │   │   └── export_service.py     # ZIP 导出
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic 模型
│   │   └── utils/
│   │       ├── demo_provider.py      # Demo 素材提供器
│   │       └── image_utils.py        # 图像处理工具函数
│   ├── tests/
│   │   ├── test_image_utils.py       # 17 tests
│   │   ├── test_spritesheet.py       # 6 tests
│   │   ├── test_tile.py              # 5 tests
│   │   ├── test_tile_score.py        # 8 tests
│   │   ├── test_export.py            # 8 tests
│   │   ├── test_asset_repository.py  # 12 tests
│   │   └── test_assets_api.py        # 8 tests
│   ├── output/                       # 运行时输出目录（.gitignore）
│   ├── data/                         # SQLite 数据库（.gitignore）
│   └── requirements.txt
├── docs/
│   ├── prd.md                        # 产品需求文档
│   ├── architecture.md               # 架构设计文档
│   ├── api.md                        # API 接口文档
│   └── demo-script.md                # Demo 视频讲解脚本
├── examples/
│   ├── sample-assets/                # Demo 模式内置样例素材（8 张 PNG）
│   └── sample-export/                # 示例导出包结构（Dark Dungeon）
│       ├── images/
│       ├── spritesheets/
│       ├── tiles/
│       ├── manifest.json
│       └── README_IMPORT.md
└── README.md
```

---

## 8. 本地运行方式

### 前置要求

| 工具 | 最低版本 |
|------|----------|
| Node.js | 18+ |
| npm | 9+ |
| Python | 3.10+ |
| pip | 23+ |

### 1) 克隆项目

```bash
git clone <repo-url>
cd spriteforge-ai
```

### 2) 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

后端启动后：
- API 服务：`http://localhost:8001`
- Swagger 文档：`http://localhost:8001/docs`
- 健康检查：`http://localhost:8001/health`

### 3) 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端启动后访问 `http://localhost:5173`。

Vite 开发服务器已配置代理，`/api` 和 `/output` 请求自动转发到 `http://localhost:8001`。

### 4) 运行测试

```bash
# 后端测试（64 个）
cd backend
python -m pytest tests/ -v

# 前端类型检查
cd frontend
npx tsc --noEmit
```

---

## 9. Demo 模式说明

Demo 模式是 SpriteForge AI 的核心架构特性——**无需任何外部 AI API Key 即可运行完整流程**。

### 工作原理

```
DEMO_MODE=true (默认)
    │
    ├── 前端: 从 GET /api/runtime-config 读取后端真实运行模式
    │   └── AssetGenerator 页面顶部显示 Provider 状态标记（Demo 内置素材 / 通义万相 AI 生成）
    │
    └── 后端: SPRITEFORGE_DEMO_MODE=true (或 DEMO_MODE=true)
        └── DemoImageProvider 使用 examples/sample-assets/ 下内置素材
            ├── character_32.png, character_64.png
            ├── item_32.png, item_64.png
            ├── tile_32.png, tile_64.png
            └── ui_32.png, ui_64.png

DEMO_MODE=false + IMAGE_PROVIDER=wanxiang + DASHSCOPE_API_KEY=xxx
    │
    └── 后端: 调用 DashScope 通义万相 API 生成真实游戏素材
        └── 失败时自动回退到 Demo Provider（需 ALLOW_DEMO_FALLBACK=true）
```

### 启用通义万相 AI 生成

```bash
# 1. 复制环境变量模板
cp backend/.env.example backend/.env

# 2. 编辑 backend/.env，填入阿里云 DashScope API Key
#    DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 3. 重启后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 前端请求级 Provider 选择

前端 AssetGenerator 页面提供三个生成后端选项：

| 选项 | 行为 |
|------|------|
| **Auto** | 跟随后端 .env 配置自动选择 |
| **Demo** | 强制使用内置样例素材（不调用任何 AI API） |
| **通义万相** | 强制使用 DashScope 通义万相 AI 生成 |

用户可在素材生成页实时切换，或在项目配置页设置默认值。

### 动态项目配置

项目配置页（Project Settings）允许用户自定义默认生成参数，包括项目名称、素材类型、美术风格、像素尺寸、生成数量、目标引擎、透明背景、生成后端。配置保存在浏览器的 localStorage 中，无需后端存储。

素材生成页在加载时自动读取项目配置中的默认值作为表单初始值。

### 关键设计

- 内置样例素材覆盖全部四种类型 + 三种尺寸
- DemoImageProvider 输出数据结构与 WanxiangImageProvider 完全一致
- 上层服务无感知，切换 Provider 无需修改业务代码
- 外部 AI 调用失败时**自动回退**到 Demo Provider，保证流程不中断
- 支持请求级 Provider 选择，前端可覆盖后端默认配置

### Demo 模式下的完整流程验证

```
生成素材 → 透明背景/裁剪/标准化 → Sprite Sheet 拼接
→ Tile 3×3 预览 → Tile 边缘评分 → ZIP 导出
```

全部步骤在 Demo 模式下均可正常执行。

---

## 10. 生成历史与素材库

后端使用 SQLite 保存生成过的素材记录，便于查看历史生成结果。

### 数据库位置

- 数据库文件：`backend/data/spriteforge.db`
- 该文件在 `.gitignore` 中排除，**不提交到 Git**
- 数据库在首次启动时自动创建（通过 `main.py` 的 startup event）

### 数据内容

每次素材生成成功后，每条生成的 asset 会被写入 `generated_assets` 表，包含：

- 素材 ID、任务 ID、项目名称、素材类型
- Prompt、风格、尺寸、目标引擎
- 使用的 AI Provider
- 图片 URL、元数据 JSON

### 前端查询

前端素材库页面可以通过 `/api/assets` 查询历史素材：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/assets` | 列出历史素材（支持 `asset_type` / `project_name` 筛选，支持分页） |
| `GET` | `/api/assets/{id}` | 查询单个素材详情 |
| `DELETE` | `/api/assets/{id}` | 删除历史记录 |

> **注意**：删除 API 仅删除数据库记录，**不删除图片文件**。如需释放磁盘空间，请手动清理 `backend/output/` 和 `backend/data/` 目录。

---

## 11. 环境变量说明

### 后端环境变量

| 变量 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `DEMO_MODE` | `true` | 否 | `true`=使用内置样例素材；`false`=调用 AI API |
| `SPRITEFORGE_DEMO_MODE` | `true` | 否 | 兼容别名，与 `DEMO_MODE` 等价 |
| `IMAGE_PROVIDER` | `demo` | 否 | 默认 Provider：`demo` / `wanxiang` |
| `DASHSCOPE_API_KEY` | (空) | 仅 Wanxiang | 阿里云 DashScope API Key |
| `WANXIANG_MODEL` | `wanx-v1` | 否 | 通义万相模型版本 |
| `WANXIANG_SIZE` | `1024*1024` | 否 | 生成图像尺寸 |
| `WANXIANG_N` | `1` | 否 | 单次 API 调用生成数量 |
| `ALLOW_DEMO_FALLBACK` | `true` | 否 | AI 生成失败时自动回退 Demo |
| `IMAGE_API_KEY` | (空) | 仅非 Demo | 外部图像生成 API 的 Key / Token |
| `IMAGE_API_BASE_URL` | (空) | 仅非 Demo | 外部图像生成 API 的基础 URL |
| `SPRITEFORGE_HOST` | `0.0.0.0` | 否 | 后端绑定地址 |
| `SPRITEFORGE_PORT` | `8001` | 否 | 后端绑定端口 |

### 设置方式

```bash
# 推荐：复制模板后编辑
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入你的 API Key

# 或直接设置环境变量
# Linux / macOS
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Windows PowerShell
$env:DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

> **安全警告**：切勿将 `DASHSCOPE_API_KEY` 写入代码或提交到版本控制。`backend/.env` 已在 `.gitignore` 中排除。

---

## 12. 第三方依赖与用途

### 后端依赖（Python）

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| [FastAPI](https://github.com/tiangolo/fastapi) | ^0.111 | REST API 框架，自动生成 Swagger 文档 | MIT |
| [Uvicorn](https://github.com/encode/uvicorn) | ^0.30 | ASGI 服务器，运行 FastAPI 应用 | BSD |
| [Pydantic](https://github.com/pydantic/pydantic) | ^2.7 | 请求/响应数据校验与序列化 | MIT |
| [Pillow](https://github.com/python-pillow/Pillow) | ^10.0 | 图像处理：透明背景、裁剪、缩放、拼接、RGB 边缘检测 | HPND |
| [python-multipart](https://github.com/Kludex/python-multipart) | ^0.0.9 | 文件上传解析（FastAPI 依赖） | Apache 2.0 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | ^1.0 | 从 .env 文件加载环境变量 | BSD |
| [requests](https://github.com/psf/requests) | ^2.31 | HTTP 客户端（调用 DashScope API） | Apache 2.0 |
| [dashscope](https://github.com/aliyun/dashscope-sdk) | ^1.0 | 阿里云 DashScope SDK | Apache 2.0 |

（注：数据库使用 Python 标准库 sqlite3，无需额外依赖）

### 后端测试依赖

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| [pytest](https://github.com/pytest-dev/pytest) | ^7.4 | 测试框架 | MIT |

### 前端依赖（Node.js）

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| [React](https://github.com/facebook/react) | ^18.3 | 前端 UI 框架 | MIT |
| [React DOM](https://github.com/facebook/react) | ^18.3 | React DOM 渲染器 | MIT |
| [React Router](https://github.com/remix-run/react-router) | ^6.23 | SPA 客户端路由 | MIT |
| [Vite](https://github.com/vitejs/vite) | ^5.3 | 构建工具 + 开发服务器 | MIT |
| [TypeScript](https://github.com/microsoft/TypeScript) | ^5.4 | 类型安全 JavaScript 超集 | Apache 2.0 |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) | ^3.4 | 原子化 CSS 样式框架 | MIT |
| [PostCSS](https://github.com/postcss/postcss) | ^8.4 | CSS 后处理器（Tailwind 依赖） | MIT |
| [Autoprefixer](https://github.com/postcss/autoprefixer) | ^10.4 | CSS 浏览器前缀自动补全 | MIT |
| [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react) | ^4.3 | Vite React JSX 编译插件 | MIT |

### 未使用的外部服务

本项目在 Demo 模式下**不依赖任何外部 AI API**。所有素材生成使用内置样例素材。图像处理（透明背景、裁剪、缩放、拼接、边缘检测）全部使用 Pillow 本地完成，不调用任何外部图像处理服务。

外部 AI API 接入为**可选模块**——仅在 `SPRITEFORGE_DEMO_MODE=false` 时启用，且需用户自行提供 API Key。该模块当前为 stub 实现（占位），等待对接具体 AI 服务商。

---

## 13. 原创功能说明

### 重要声明

> **本项目的原创核心是"游戏资产工作流管线"**（素材后处理、Sprite Sheet 拼接与元数据生成、Tile 边缘一致性评分、引擎感知导出），**而非 AI 图像生成模型本身**。
>
> AI 图像生成能力为可选接入的外部服务，默认 Demo 模式使用内置静态样例素材，不涉及任何 AI 模型推理。

### 原创功能清单

| 功能 | 原创内容 | 实现方式 |
|------|----------|----------|
| **资产化后处理管线** | 透明背景移除 → 空白裁剪 → 尺寸标准化 → 主体居中的完整自动化链路 | `image_utils.py` 中自实现的 `process_asset()` 管线函数 |
| **Sprite Sheet 拼接** | 多帧素材自动拼接为规范 Sprite Sheet + JSON 帧元数据（含动画段定义） | `spritesheet.py` 中自实现的拼接逻辑和元数据生成 |
| **Tile 边缘一致性评分** | 基于四边 RGB 均值欧几里得距离的 0-100 无缝性量化评分算法 | `tile_score.py` 中自实现的边缘提取、RGB 比对和评分公式 |
| **引擎感知导出** | 按 Unity / Godot / Generic 目录约定组织 ZIP 结构，附带引擎特定导入说明 | `export_service.py` 中三套 README 模板和目录构建逻辑 |
| **Demo 模式 + 自动回退** | 无外部依赖运行完整流程；AI 模式失败自动回退 Demo | Provider 抽象层 + config 驱动的工厂模式 |
| **CSS 动画预览** | 纯前端 CSS backgroundPosition 驱动的 Sprite Sheet 逐帧动画播放 | `SpriteSheetTool.tsx` 中 AnimationPreview 组件 |

### 非原创但合理使用的部分

- **前端 UI 框架**：React、Tailwind CSS、React Router（标准前端技术栈）
- **后端 Web 框架**：FastAPI、Pydantic、Uvicorn（标准 Python Web 技术栈）
- **图像底层操作**：Pillow 的 `Image.open()`、`resize()`、`paste()`、`getpixel()` 等标准 API
- **ZIP 打包**：Python 标准库 `zipfile`
- **AI 图像生成**（可选模块）：若对接外部 API（如 OpenAI DALL·E、Stability AI），图像生成能力来自第三方服务，本项目仅负责调用和结果处理

---

## 14. API 文档入口

### Swagger UI（交互式文档）

后端启动后访问：**`http://localhost:8000/docs`**

支持直接在浏览器中测试所有 API 端点。

### ReDoc（只读文档）

访问：**`http://localhost:8000/redoc`**

### 端点总览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `GET` | `/api/runtime-config` | 返回后端实际 Provider 状态与模式 |
| `POST` | `/api/generate` | 创建素材生成任务 |
| `GET` | `/api/tasks/{task_id}` | 查询任务状态与结果 |
| `POST` | `/api/process` | 素材后处理（透明/裁剪/标准化） |
| `POST` | `/api/spritesheet` | Sprite Sheet 拼接 |
| `POST` | `/api/tile/preview` | Tile 3×3 平铺预览 |
| `POST` | `/api/tile/score` | Tile 边缘一致性评分 |
| `POST` | `/api/export` | ZIP 导出 |
| `GET` | `/api/assets` | 列出已生成素材（支持筛选、分页） |
| `GET` | `/api/assets/{id}` | 查询单个素材详情 |
| `DELETE` | `/api/assets/{id}` | 删除素材历史记录 |

详细请求/响应格式见 [docs/api.md](docs/api.md)。

---

## 15. Demo 视频链接

> **待录制** — 视频链接占位

### 视频脚本

完整的讲解脚本见 **[docs/demo-script.md](docs/demo-script.md)**。

主题：**Dark Dungeon Pixel RPG** — 一个像素风地牢 Roguelike 游戏的素材生成案例。

脚本覆盖流程（预计 3-4 分钟）：
1. 项目介绍（30s）
2. 创建项目 "Dark Dungeon" + 设定 Godot 引擎（25s）
3. 生成四类素材：骑士角色、地牢地砖、血药道具、血条 UI（50s）
4. 后处理管线：透明背景、裁剪、标准化、居中（30s）
5. Sprite Sheet 拼接 + CSS 动画预览（35s）
6. Tile 3×3 平铺预览 + 边缘一致性评分（40s）
7. 导出 Godot ZIP 包 + 结构展示（30s）
8. 总结（15s）

### 示例导出结构

`examples/sample-export/` 目录展示了一个完整的 "Dark Dungeon" 导出包结构：

```
examples/sample-export/
├── images/
│   └── README.txt         ← 素材文件说明
├── spritesheets/
│   └── README.txt         ← Sprite Sheet 说明
├── tiles/
│   └── README.txt         ← Tile 预览说明
├── manifest.json          ← 素材清单（4 个素材 + spritesheet + tile）
└── README_IMPORT.md       ← Godot 导入说明
```

### 录制建议

- 浏览器窗口 1920×1080，缩放 100%
- 如条件允许，在终端同步展示 `tree output/` 和 `pytest tests/ -v`
- 后期加入字幕标注关键操作

---

## 16. PR 与 Commit 规范

### Commit Message 格式

```
<type>(<scope>): <subject>
```

| type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `docs` | 文档更新 |
| `style` | 代码风格（不影响功能） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖 |

**示例**：
```
feat(tile): add 3x3 tiling preview endpoint and frontend page
fix(spritesheet): correct frame coordinate calculation for non-square frames
docs(readme): add third-party dependency declarations
```

### PR 规范

- 每个 PR 聚焦单一功能或修复
- PR 标题使用中文或英文，与 commit 风格一致
- PR 描述包含 Summary + Test plan
- 合并前确保：TypeScript 类型检查通过 + Vite 构建成功 + 后端测试全绿

### 分支策略

- `main` — 稳定分支，任意时间点可运行
- 功能分支从 `main` 创建，合并后删除
- 本项目共规划约 18 个增量 PR，渐进构建完整功能

---

## 17. 学术诚信与知识产权说明

### 代码原创性

- 本项目所有代码（前端组件、后端服务、图像处理算法、测试用例）均为手工编写
- 未直接复制任何开源项目的完整文件或模块
- 使用的第三方库均通过包管理器（npm / pip）标准方式引入，并在 [§12](#12-第三方依赖与用途) 中逐一列出版本、用途和许可证

### AI 生成能力说明

- **本项目不包含自研 AI 图像生成模型**
- Demo 模式下使用的素材为纯 Python（struct + zlib）生成的占位图像，不涉及任何 AI 推理
- 外部 AI API 接入为可选模块，需用户自行配置第三方服务（如 OpenAI DALL·E API、Stability AI API 等）
- 若对接外部 AI 服务，图像生成能力归该服务提供商所有，本项目仅负责：
  1. 将用户 prompt 和参数转发至 API
  2. 对返回的图像执行后处理管线
  3. 将处理后的资产打包导出

### 样例素材

- `examples/sample-assets/` 目录下的 PNG 文件为纯色占位素材，使用 Python 脚本生成，不涉及任何版权素材
- 所有素材文件均为原创占位图，不包含任何第三方游戏的美术资源

### 第三方库许可证合规

所有第三方依赖均为 MIT、BSD、Apache 2.0 或 HPND 等宽松许可证，允许在竞赛项目中自由使用。完整列表见 [§12](#12-第三方依赖与用途)。

### 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pillow (PIL Fork) 文档](https://pillow.readthedocs.io/)
- [React 官方文档](https://react.dev/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Vite 官方文档](https://vitejs.dev/)
- Unity / Godot 引擎导入规范来自各自官方文档

---

## License

MIT
