param(
    [string]$OutputDir = "./backups"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$dbFile = Join-Path $OutputDir "database-$stamp.sql"
$mediaFile = Join-Path $OutputDir "media-$stamp.tar.gz"

docker compose exec -T db sh -c 'mysqldump --no-tablespaces -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' > $dbFile
if ($LASTEXITCODE -ne 0) { throw '数据库备份失败' }

$resolvedOutput = (Resolve-Path $OutputDir).Path
docker run --rm -v hoshino-blog_media_data:/data -v "${resolvedOutput}:/backup" alpine:3.20 tar czf "/backup/media-$stamp.tar.gz" -C /data .
if ($LASTEXITCODE -ne 0) { throw '媒体文件备份失败' }

Write-Host "备份完成：$dbFile"
Write-Host "备份完成：$mediaFile"
