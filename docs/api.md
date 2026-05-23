# API Documentation — SpriteForge AI

> 本文档随 API 实现进度逐步更新。当前为初始占位版本。

## 基础信息

- Base URL: `http://localhost:8000`
- Content-Type: `application/json`（文件上传使用 `multipart/form-data`）

## 接口列表

### 1. 生成素材

```
POST /api/generate
```

**Request Body:**

```json
{
  "prompt": "a brave knight with sword",
  "asset_type": "character",
  "size": 32,
  "style": "pixel",
  "count": 4
}
```

**Response:**

```json
{
  "assets": [
    {
      "id": "uuid",
      "type": "character",
      "size": 32,
      "image_url": "/output/uuid.png",
      "metadata": {}
    }
  ]
}
```

> 后续接口待实现时补充。
