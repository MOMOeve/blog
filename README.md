# 星野文记

个人博客：Vue 3 前端 + Django DRF 后端（monorepo）。

```text
blog/
  frontend/   # Vue 3 + TypeScript + Less + Vite
  backend/    # Django 5 + DRF + JWT
  docs/       # API 约定与部署说明
  start.py    # 一键启动前后端
```

## 功能

- 首页 / 文章列表 / 文章详情（Markdown 渲染）
- 摄影画廊（mediahub）
- 登录（JWT）、深浅主题切换
- Staff：写文章、编辑、草稿箱、封面/插图上传
- 独立 URL（可分享、可刷新）
- 图片本地存储；无图或加载失败时用渐变色块占位（`MediaCover`）

## 图片与媒体

| 类型 | 路径 |
|------|------|
| 文章封面（种子） | `/media/covers/*.svg` |
| 摄影（种子） | `/media/photos/*.svg` |
| 站点 Hero / 头像 | `/media/site/hero.svg`、`avatar.svg` |
| 用户上传 | `/media/uploads/年/月/` |

- 文件落在 `backend/media/`；开发时 Vite 代理 `/media` → Django
- `seed_content` / `seed_photos` 会生成本地 SVG，并同步到 `frontend/public/media/`
- 上传：`POST /api/v1/uploads/`（staff，multipart 字段 `file`，≤5MB）

## 快速启动

### Docker 一键启动（推荐）

需已安装 [Docker Desktop](https://docs.docker.com/get-docker/)。在项目根目录执行：

```bash
docker compose up --build
```

浏览器打开 http://localhost:8080/

- 演示账号（staff）：`demo@example.com` / `demo1234`
- Admin：http://localhost:8080/admin/
- Swagger：http://localhost:8080/api/docs/

可选：复制 `.env.example` 为 `.env` 后修改端口、密钥或数据库密码。停止用 `docker compose down`；连数据一起清掉用 `docker compose down -v`。

### 本地开发一键启动

需同时跑后端（8000）和前端（5173）。先完成下方「首次准备」，之后在项目根目录执行：

```bash
python start.py
```

按 `Ctrl+C` 可同时停止前后端。

### 首次准备

#### 1. 后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_content
python manage.py seed_photos
```

- Swagger：http://127.0.0.1:8000/api/docs/
- Admin：http://127.0.0.1:8000/admin/

演示账号（staff）：`demo@example.com` / `demo1234`

#### 2. 前端

```bash
cd frontend
npm install
copy .env.example .env
```

打开 http://localhost:5173/ 。Vite 会把 `/api`、`/media` 代理到 Django。

#### 3. 手动分别启动（可选）

```bash
# 终端 1
cd backend
.\.venv\Scripts\python manage.py runserver 8000

# 终端 2
cd frontend
npm run dev
```

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
| `/profile` | 个人资料（登录） |
| `/reset-password?token=…` | 重置密码 |

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

已完成：图片上传、独立 URL、草稿箱、Markdown 写作、本地媒体、色块占位。

### 优先（现有半成品）

- [x] 顶栏搜索：搜索图标接到文章搜索
- [x] 联系表单 / 页脚订阅：存库或发邮件
- [x] 文章列表分页（接口已有 `PAGE_SIZE`）

### 内容体验

- [x] Markdown 增强：代码高亮、目录 TOC、粘贴即上传图片
- [x] 摄影后台编辑（改说明 / 分类 / 排序 / 上传）
- [x] 相关文章、上一篇 / 下一篇
- [x] 阅读量、点赞

### 账号

- [x] 注册（登录弹窗可切换注册）
- [x] 改密码、找回密码
- [x] 读者 / 作者角色（不只 `is_staff`）
- [x] 个人资料页（头像、简介）

### 互动与分发

- [x] 评论（登录后评论 + 审核）
- [x] RSS（页脚链接 `/api/v1/feed/rss/`）
- [x] sitemap（`/api/v1/feed/sitemap.xml`）
- [x] 标签云、按年月归档

### 工程

- [x] 测试 + CI
- [x] 生产部署落地：Gunicorn + Nginx + MySQL（`docker compose up --build`，见 [docs/deploy.md](docs/deploy.md)）
