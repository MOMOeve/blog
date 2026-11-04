# 生产部署要点

## Docker Compose（推荐）

项目根目录已包含 `docker-compose.yml`：Nginx + Gunicorn + MySQL。

```bash
docker compose up --build -d
```

默认站点：http://localhost:8080/ 。上线前请复制 `.env.example` 为 `.env`，至少更换 `SECRET_KEY`、数据库密码，并把 `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` / `CORS_ALLOWED_ORIGINS` 改成实际域名。

媒体与静态文件分别落在 `media_data`、`static_data` 卷；数据库在 `mysql_data`。

密码重置邮件使用 `FRONTEND_BASE_URL`，必须指向读者实际访问的前端站点。Docker 未显式设置时默认使用 `http://localhost:${WEB_PORT:-8080}`；例如 `WEB_PORT=30080` 时为 `http://localhost:30080`。对外部署请在根目录 `.env` 显式配置 `FRONTEND_BASE_URL=https://your.domain.com`，然后重建/更新 backend 容器。前后端分开开发时，在 `backend/.env` 设置 `FRONTEND_BASE_URL=http://localhost:5173`。

默认邮箱后端为控制台输出。真实邮件投递需要另行配置邮箱后端及 SMTP；自动测试使用内存邮箱，不会对外发信。

## MySQL

1. 创建数据库（utf8mb4）
2. 编辑 `backend/.env`：

```env
DEBUG=False
SECRET_KEY=<强随机密钥>
USE_MYSQL=True
MYSQL_DATABASE=hoshino_blog
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
ALLOWED_HOSTS=your.domain.com
CORS_ALLOWED_ORIGINS=https://your.frontend.domain
```

3. 迁移：

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## 权限模型

- 匿名：可读已发布文章
- 登录读者：可对已发布文章提交评论，默认待审核
- `author`：可写自己的文章，并审核自己文章下的评论
- `is_staff`：可管理全部文章和评论
- Django Admin：`/admin/` 管理内容与用户

文章详情页为管理员和该文章作者显示“通过/撤回公开”。审核仅改变公开状态，不修改评论正文，不需要新增数据库字段。

## 一期回归检查

```bash
cd frontend
npm ci
npm test
npm run build
cd ..
docker compose up -d --build
docker compose ps
docker compose exec -T backend python manage.py test --verbosity 1
```

Markdown 回归使用独立 worker 与超时保护，覆盖竖线文本、代码高亮、目录、表格、任务列表及危险链接。后端覆盖评论权限矩阵和密码重置邮件地址/令牌边界。回滚用对应代码和锁文件重新构建镜像，保留数据库和媒体卷，不执行 `docker compose down -v`。

## 进程建议

- 后端：gunicorn / waitress + nginx 反代 `/api`
- 前端：`npm run build` 后由 nginx 托管 `frontend/dist`
- 媒体文件：`MEDIA_ROOT` 由 nginx 或对象存储提供

## 安全清单

- [ ] 更换 `SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] HTTPS
- [ ] CORS 仅放行正式前端域名
- [ ] 定期轮换 JWT / 数据库密码

## 备份

服务启动后可在项目根目录执行以下命令，备份数据库和媒体卷：

```powershell
.\docker\backup.ps1
```

备份文件会写入 `backups/`，应复制到独立的存储位置，并定期验证恢复流程。
