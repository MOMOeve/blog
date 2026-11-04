# API 约定（/api/v1）

Base URL 开发环境：通过 Vite 代理到 `http://127.0.0.1:8000`。

## Auth

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| POST | `/api/v1/auth/register/` | 否 | body: `{ email, password, displayName? }` → 注册并返回 JWT |
| POST | `/api/v1/auth/login/` | 否 | body: `{ email, password }` → `{ access, refresh, user }` |
| POST | `/api/v1/auth/refresh/` | 否 | body: `{ refresh }` → `{ access, refresh? }` |
| GET | `/api/v1/auth/me/` | Bearer | 当前用户 |
| PATCH | `/api/v1/auth/me/` | Bearer | 更新资料 `{ displayName?, bio?, avatar? }` |
| POST | `/api/v1/auth/password/change/` | Bearer | `{ currentPassword, newPassword }` |
| POST | `/api/v1/auth/password/reset/` | 否 | `{ email }` → 发送重置链接（开发环境输出到控制台） |
| POST | `/api/v1/auth/password/reset/confirm/` | 否 | `{ token, newPassword }` |
| POST | `/api/v1/auth/logout/` | Bearer | body: `{ refresh }` 拉黑 refresh |

`user` 形状：

```json
{
  "id": 1,
  "username": "demo",
  "email": "demo@example.com",
  "displayName": "demo",
  "role": "staff",
  "isStaff": true,
  "isAuthor": true,
  "bio": "",
  "avatar": ""
}
```

角色：`reader`（读者，默认）、`author`（作者，可写文章）、`staff`（管理员，Django Admin + 全部权限）。Admin 可在用户资料里将读者提升为作者。

## Content

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | `/api/v1/posts/` | 否 | 列表；query: `category`, `tag`, `year`, `month`, `search`, `featured`, `published`, `ordering` |
| GET | `/api/v1/posts/{id}/` | 否 | 详情（含 body、viewCount、likeCount、liked、related、prev、next、canModerateComments）；首次访问计阅读 |
| POST | `/api/v1/posts/{id}/like/` | 否 | 切换点赞；header: `X-Visitor-Id`（匿名去重） |
| GET | `/api/v1/posts/{id}/comments/` | 否 | 已审核评论列表；管理员和文章作者可见该文章待审评论 |
| POST | `/api/v1/posts/{id}/comments/` | 登录 | body: `{ body }` → 提交评论（默认待审核） |
| PATCH | `/api/v1/posts/{id}/comments/{comment_id}/` | 文章作者/Staff | 仅接受 `{ "approved": true或false }`，通过或撤回公开 |
| GET | `/api/v1/posts/tag-cloud/` | 否 | 标签云 `[{ name, count }]` |
| GET | `/api/v1/posts/archive/` | 否 | 年月归档 `[{ year, month, count }]` |
| GET | `/api/v1/feed/rss/` | 否 | RSS 2.0 订阅源 |
| GET | `/api/v1/feed/sitemap.xml` | 否 | XML sitemap |
| GET | `/api/v1/posts/categories-list/` | 否 | `["全部", ...]` |
| GET | `/api/v1/categories/` | 否 | 分类 |
| GET | `/api/v1/tags/` | 否 | 标签 |
| POST | `/api/v1/posts/` | 作者/Staff | 新建（body 为 Markdown） |
| PUT/PATCH | `/api/v1/posts/{id}/` | 作者/Staff | 更新（作者仅自己的文章） |
| DELETE | `/api/v1/posts/{id}/` | 作者/Staff | 删除（作者仅自己的文章） |

Staff 可用 `?published=false` 获取草稿列表；作者可见自己的草稿；`ordering=-updated_at` 按最近修改排序。

文章详情与评论路径均支持数字 ID 或 slug。评论只接受已发布文章；正文长度为 2～2000 个字符。创建返回 201，服务器固定待审；公众不可见待审评论。审核返回更新后评论；非审核者返回 403，跨文章评论 ID 返回 404；非布尔或额外审核字段返回 400。前端根据服务端 `canModerateComments` 显示审核按钮，服务端仍对每次请求验证权限。

找回密码邮件链接以 `FRONTEND_BASE_URL` 为基址，与请求 Host 无关。token 一小时内有效、仅可使用一次；成功重置使该用户其他未使用 token 同时失效。请求接口对存在和不存在的邮箱保持相同响应。

## Photography (mediahub)

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | `/api/v1/photos/` | 否 | 列表；query: `category` |
| GET | `/api/v1/photos/{id}/` | 否 | 详情 |
| GET | `/api/v1/photos/categories-list/` | 否 | `["全部", "自然", ...]` |
| POST | `/api/v1/photos/` | Staff | 新建；body: `{ title, location?, date?, img, aspect?, category, description?, sort_order?, published? }` |
| PATCH | `/api/v1/photos/{id}/` | Staff | 更新 |
| DELETE | `/api/v1/photos/{id}/` | Staff | 删除 |
| POST | `/api/v1/uploads/` | 作者/Staff | 上传图片（multipart `file`）→ `{ url, path, name, size }` |
| POST | `/api/v1/uploads/avatar/` | 登录 | 上传头像（≤2MB）→ `{ url, path }` |

照片字段：`{ id, title, location, date, img, aspect, category, description }`

上传限制：jpg/png/webp/gif，文章插图最大 5MB；头像最大 2MB；文件会校验真实图片格式并存储在 `media/uploads/年/月/`。

## Inbox

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| POST | `/api/v1/contact/` | 否 | body: `{ name, email, subject?, message }` → 联系留言 |
| POST | `/api/v1/subscribe/` | 否 | body: `{ email }` → 邮件订阅（重复订阅返回 200） |

Staff 可在 Django Admin「收件箱」中查看留言与订阅列表。

种子本地图：

- 文章封面：`/media/covers/*.svg`
- 摄影：`/media/photos/*.svg`
- 站点：`/media/site/hero.svg`、`/media/site/avatar.svg`

OpenAPI：`/api/docs/`

## 演示账号

- 邮箱：`demo@example.com`
- 密码：`demo1234`

## Seed

```bash
python manage.py seed_content
python manage.py seed_photos
```
