# 生产部署要点

## Docker Compose（推荐）

项目根目录已包含 `docker-compose.yml`：Nginx + Gunicorn + MySQL。

```bash
docker compose up --build -d
```

默认站点：http://localhost:8080/ 。上线前请复制 `.env.example` 为 `.env`，至少更换 `SECRET_KEY`、数据库密码，并把 `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` / `CORS_ALLOWED_ORIGINS` 改成实际域名。

媒体与静态文件分别落在 `media_data`、`static_data` 卷；数据库在 `mysql_data`。

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
- 登录用户：可读
- `is_staff`：可写文章（DRF `IsStaffOrReadOnly`）
- Django Admin：`/admin/` 管理内容与用户

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
