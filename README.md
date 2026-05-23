# SpriteForge AI

> 面向独立游戏开发者的 2D 游戏素材生成工具 — 参赛项目

## 题目选择

「2D 游戏素材生成」— 通过文本描述和简单参数，快速生成像素风 2D 游戏素材，并自动完成游戏资产化处理。

## 功能规划

- 支持角色、道具、Tile、UI 四类素材生成
- 支持像素风 32×32 / 64×64 输出
- 自动资产化处理（透明背景、裁剪、尺寸标准化、主体居中）
- Sprite Sheet 拼接 + JSON 元数据
- Tile 3×3 平铺预览 + 边缘一致性评分
- Unity / Godot ZIP 素材包导出
- 内置 DEMO 模式，无需外部 AI API 即可跑通完整流程

## 技术栈

> 待补充

## 运行方式

> 待补充

## 项目结构

```
spriteforge-ai/
├── frontend/          # React + Vite + TypeScript + Tailwind CSS
├── backend/           # Python FastAPI + Pillow
├── docs/              # 项目文档
├── examples/          # 样例素材与导出示例
│   ├── sample-assets/ # DEMO 模式内置素材
│   └── sample-export/ # 导出示例
├── .github/           # CI / PR 模板
└── README.md
```

## 第三方依赖说明

> 待补充

## 原创功能说明

> 待补充

## Demo 视频

> 链接待补充

## License

MIT
