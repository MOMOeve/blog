# API 约定（/api/v1）

Base URL 开发环境：通过 Vite 代理到 `http://127.0.0.1:8000`。

## Auth

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| POST | `/api/v1/auth/login/` | 否 | body: `{ email, password }` → `{ access, refresh, user }` |
| POST | `/api/v1/auth/refresh/` | 否 | body: `{ refresh }` → `{ access, refresh? }` |
| GET | `/api/v1/auth/me/` | Bearer | 当前用户 |
| POST | `/api/v1/auth/logout/` | Bearer | body: `{ refresh }` 拉黑 refresh |

`user` 形状：

```json
{ "id": 1, "username": "demo", "email": "demo@example.com", "displayName": "demo", "isStaff": true }
```

## Content

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | `/api/v1/posts/` | 否 | 列表；query: `category`, `search`, `featured`, `published`, `ordering` |
| GET | `/api/v1/posts/{id}/` | 否 | 详情（含 body） |
| GET | `/api/v1/posts/categories-list/` | 否 | `["全部", ...]` |
| GET | `/api/v1/categories/` | 否 | 分类 |
| GET | `/api/v1/tags/` | 否 | 标签 |
| POST | `/api/v1/posts/` | Staff | 新建（body 为 Markdown） |
| PUT/PATCH | `/api/v1/posts/{id}/` | Staff | 更新 |
| DELETE | `/api/v1/posts/{id}/` | Staff | 删除 |

Staff 可用 `?published=false` 获取草稿列表；`ordering=-updated_at` 按最近修改排序。

## Photography (mediahub)

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | `/api/v1/photos/` | 否 | 列表；query: `category` |
| GET | `/api/v1/photos/{id}/` | 否 | 详情 |
| GET | `/api/v1/photos/categories-list/` | 否 | `["全部", "自然", ...]` |
| POST/PUT/PATCH/DELETE | `/api/v1/photos/`… | Staff | 写操作需 `is_staff` |
| POST | `/api/v1/uploads/` | Staff | 上传图片（multipart `file`）→ `{ url, path, name, size }` |

照片字段：`{ id, title, location, date, img, aspect, category, description }`

上传限制：jpg/png/webp/gif/svg，最大 5MB；文件存 `media/uploads/年/月/`。

OpenAPI：`/api/docs/`

## 演示账号

- 邮箱：`demo@example.com`
- 密码：`demo1234`

## Seed

```bash
python manage.py seed_content
python manage.py seed_photos
```
