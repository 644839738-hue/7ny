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
