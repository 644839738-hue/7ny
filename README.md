# SpriteForge AI

> 面向 2D 游戏开发工作流的 AI 素材生成与资产化管线 — 参赛项目

## 题目选择

「**2D 游戏素材生成**」— 通过文本描述和简单参数生成像素风 2D 游戏素材，并自动完成从「AI 生成图像」到「游戏引擎可导入资产」的工程化处理。

## 项目简介

SpriteForge AI **不是普通的文生图工具**。传统 AI 图像生成器（DALL·E、Midjourney 等）产出的图像无法直接用于游戏开发——它们缺少透明背景、尺寸不统一、无 Sprite Sheet 元数据、Tile 边缘可能断裂。SpriteForge AI 在「生成」和「可用」之间架设了一条完整的资产化管线。

### 核心工作流

```
输入 Prompt + 参数  →  AI 生成（或 DEMO 素材）  →  自动后处理  →  预览 / 检测  →  引擎适配导出
```

## 核心功能

| 功能 | 说明 | 创新点 |
|------|------|--------|
| 文本/参数生成素材 | 输入 prompt + 选择类型/尺寸/风格，一键生成 | 面向游戏资产的结构化生成，非泛化文生图 |
| 四类素材支持 | 角色（Character）、道具（Prop）、Tile、UI | 覆盖 2D 游戏核心素材类型 |
| 像素风双尺寸 | 32×32 和 64×64 输出 | 适配主流像素游戏规格 |
| 自动资产化后处理 | 透明背景 → 空白裁剪 → 尺寸标准化 → 主体居中 | **完整管线，非单点功能** |
| Sprite Sheet 拼接 | 多帧素材自动拼接 + JSON 帧元数据 | 直出引擎可用格式 |
| Tile 3×3 平铺预览 | 单 Tile 自动拼成 3×3 网格 | 直观检查平铺效果 |
| Tile 边缘一致性评分 | 检测四边 RGB 差异，输出 0-100 无缝评分 | **自研检测算法** |
| Unity / Godot 导出 | 按引擎目录约定打包 ZIP | **引擎感知导出** |
| DEMO 模式 | 无需外部 AI API，内置样例素材跑通全流程 | **确保可复现可评审** |

## 技术栈

| 层 | 技术 | 用途 |
|----|------|------|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS | Web 交互界面 |
| Backend | Python FastAPI + Pydantic v2 | REST API 服务 |
| Image Processing | Pillow + OpenCV | 图像处理、Tile 检测 |
| AI Generation | 可配置 Provider（默认 DEMO 模式） | 素材生成 |
| Export | Python zipfile | ZIP 打包 |

## 项目结构

```
spriteforge-ai/
├── frontend/                 # React + Vite + TypeScript + Tailwind CSS
│   ├── public/
│   └── src/
│       ├── components/       # UI 组件
│       ├── pages/            # 页面
│       ├── services/         # API 调用封装
│       ├── hooks/            # 自定义 Hooks
│       ├── types/            # TypeScript 类型定义
│       └── config/           # 配置（含 DEMO 开关）
├── backend/                  # Python FastAPI
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── models/           # Pydantic Schemas
│   │   └── utils/            # 工具函数
│   └── requirements.txt
├── docs/                     # 项目文档
│   ├── prd.md               # 产品需求文档
│   ├── architecture.md      # 架构设计文档
│   └── api.md               # API 文档
├── examples/
│   ├── sample-assets/        # DEMO 模式内置素材
│   └── sample-export/        # 导出示例
├── .github/
│   └── pull_request_template.md
└── README.md
```

## 运行方式

### 前置要求

- Node.js 18+
- npm 9+

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`。

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端 API 文档访问 `http://localhost:8000/docs`。

### 环境变量（后端）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SPRITEFORGE_DEMO_MODE` | `true` | 设为 `false` 启用外部 AI 生成 |
| `IMAGE_API_KEY` | (空) | 外部图像生成 API 的 Key / Token |
| `IMAGE_API_BASE_URL` | (空) | 外部图像生成 API 的基础 URL |

> **安全提示**：请勿将 `IMAGE_API_KEY` 写入代码或提交到 Git。
> 使用环境变量或 `.env` 文件（已在 `.gitignore` 中排除）。

### DEMO 模式 vs AI 模式

| 模式 | DEMO_MODE | 行为 |
|------|-----------|------|
| DEMO | `true`（默认） | 使用内置样例素材，无需任何 API Key |
| AI | `false` | 调用外部图像生成 API；若失败自动回退 DEMO |

## 第三方依赖说明

> 待补充 — 将在各阶段 PR 中随依赖引入逐步更新

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| React 18 | ^18.3 | 前端框架 | MIT |
| Vite | ^5.3 | 构建工具 | MIT |
| React Router | ^6.23 | 前端路由 | MIT |
| Tailwind CSS | ^3.4 | 样式框架 | MIT |
| FastAPI | ^0.111 | 后端 REST 框架 | MIT |
| Uvicorn | ^0.30 | ASGI 服务器 | BSD |
| Pydantic | ^2.7 | 数据校验与序列化 | MIT |
| Pillow | 待定 | 图像处理 | HPND |
| OpenCV | 待定 | Tile 边缘检测 | Apache 2.0 |

## 原创功能说明

> **声明**：本项目的原创核心是 **游戏资产工作流管线**（后处理、Sprite Sheet、Tile 检测、引擎导出），
> 而非 AI 图像生成本身。外部 AI 生成能力为可选接入模块，默认 DEMO 模式无需任何外部 API。

1. **资产化后处理管线** — 透明背景移除、空白区域裁剪、尺寸标准化、主体居中的完整处理链路，串联为自动化管线
2. **Tile 边缘一致性评分算法** — 基于四边 RGB 均值比对的 Tile 无缝性评估方法，填补 AI 生成 Tile 的质量检测空白
3. **DEMO 模式 + 自动回退** — 前后端均可无外部 API 运行；AI 模式失败时自动回退 DEMO，保证流程不中断
4. **引擎感知导出** — 自动生成 Unity `.meta` 占位和 Godot `.import` 占位，按引擎目录约定组织 ZIP 包结构
5. **Provider 可插拔 AI 层** — 通过抽象接口隔离生成后端，Demo / AI 无感切换，便于扩展

## Demo 视频

> 链接待补充

## License

MIT
