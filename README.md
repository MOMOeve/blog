# 星野文记

个人博客：Vue 3 前端 + Django DRF 后端（monorepo）。

```text
blog/
  frontend/   # Vue 3 + TypeScript + Less + Vite
  backend/    # Django 5 + DRF + JWT
  docs/       # API 约定与部署说明
```

## 功能

- 首页 / 文章列表 / 文章详情（Markdown 渲染）
- 摄影画廊（mediahub，图片走本地 `/media`）
- 登录（JWT）、深浅主题
- Staff：写文章、编辑、草稿箱、封面/插图上传
- 独立 URL，可分享、可刷新

## 快速启动

需同时跑后端（8000）和前端（5173）。

### 1. 后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_content
python manage.py seed_photos
python manage.py runserver 8000
```

- Swagger：http://127.0.0.1:8000/api/docs/
- Admin：http://127.0.0.1:8000/admin/

演示账号（staff）：`demo@example.com` / `demo1234`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173/ 。Vite 会把 `/api`、`/media` 代理到 Django。

## 页面路径

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/articles` | 文章列表 |
| `/articles/:id` | 文章详情 |
| `/write` | 写文章（staff） |
| `/write/:id` | 编辑文章（staff） |
| `/drafts` | 草稿箱（staff） |
| `/photography` | 摄影 |
| `/about` | 关于 |
| `/contact` | 联系 |

写作：正文为 Markdown；「保存草稿」进草稿箱，「发布」进详情。草稿可继续编辑、一键发布或删除。

## 环境变量

前端 `frontend/.env`：

- `VITE_API_BASE_URL=/api/v1`
- `VITE_USE_AUTH_MOCK=false`（仅 `true` 时用本地 mock 登录）

后端 `backend/.env`：

- 开发默认 `USE_MYSQL=False`（SQLite）
- 生产设 `USE_MYSQL=True` 并填写 `MYSQL_*`

## 二次修改

- 接口只经 `frontend/src/api/*` 与 Django `apps/*/serializers|views|urls`
- 新业务按 app 拆分（`accounts` / `content` / `mediahub`）
- 改契约后同步 [docs/api.md](docs/api.md) 与 OpenAPI

生产部署见 [docs/deploy.md](docs/deploy.md)。

## 剩余计划

已完成：图片上传、独立 URL、草稿箱、Markdown 写作。建议按下面顺序继续。

### 优先（现有半成品）

- [ ] 顶栏搜索：搜索图标接到文章搜索
- [ ] 联系表单 / 页脚订阅：存库或发邮件
- [ ] 文章列表分页（接口已有 `PAGE_SIZE`）

### 内容体验

- [ ] Markdown 增强：代码高亮、目录 TOC、粘贴即上传图片
- [ ] 摄影后台编辑（改说明 / 分类 / 排序 / 上传）
- [ ] 相关文章、上一篇 / 下一篇
- [ ] 阅读量、点赞

### 账号

- [ ] 注册、改密码、找回密码
- [ ] 读者 / 作者角色（不只 `is_staff`）
- [ ] 个人资料页（头像、简介）

### 互动与分发

- [ ] 评论（登录后评论 + 审核）
- [ ] RSS / sitemap
- [ ] 标签云、按年月归档

### 工程

- [ ] 测试 + CI
- [ ] 生产部署落地：Gunicorn + Nginx + MySQL（见 [docs/deploy.md](docs/deploy.md)）
