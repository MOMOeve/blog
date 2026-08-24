"""Wait for MySQL, migrate, seed once, then start Gunicorn."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

SEEDED_MARK = Path('/app/media/.seeded')


def run(args: list[str]) -> None:
    subprocess.check_call(args)


def truthy(name: str, default: str = '0') -> bool:
    return os.environ.get(name, default).strip().lower() in {'1', 'true', 'yes', 'on'}


def wait_for_mysql() -> None:
    import pymysql

    host = os.environ.get('MYSQL_HOST', 'db')
    port = int(os.environ.get('MYSQL_PORT', '3306'))
    user = os.environ.get('MYSQL_USER', 'blog')
    password = os.environ.get('MYSQL_PASSWORD', 'blogpass')
    database = os.environ.get('MYSQL_DATABASE', 'hoshino_blog')

    last_error: Exception | None = None
    for attempt in range(1, 61):
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=3,
            )
            conn.close()
            print(f'[entrypoint] MySQL ready ({host}:{port})', flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f'[entrypoint] waiting for MySQL ({attempt}/60): {exc}', flush=True)
            time.sleep(2)
    raise SystemExit(f'MySQL not ready: {last_error}')


def maybe_seed() -> None:
    if not truthy('RUN_SEED', '1'):
        print('[entrypoint] RUN_SEED disabled, skip seed', flush=True)
        return
    if SEEDED_MARK.exists():
        print('[entrypoint] seed already applied, skip', flush=True)
        return
    run([sys.executable, 'manage.py', 'seed_content'])
    run([sys.executable, 'manage.py', 'seed_photos'])
    SEEDED_MARK.parent.mkdir(parents=True, exist_ok=True)
    SEEDED_MARK.touch()
    print('[entrypoint] seed completed', flush=True)


def main() -> None:
    if truthy('USE_MYSQL', 'True'):
        wait_for_mysql()

    run([sys.executable, 'manage.py', 'migrate', '--noinput'])
    run([sys.executable, 'manage.py', 'collectstatic', '--noinput'])
    maybe_seed()

    workers = os.environ.get('GUNICORN_WORKERS', '2')
    os.execvp(
        'gunicorn',
        [
            'gunicorn',
            'config.wsgi:application',
            '--bind',
            '0.0.0.0:8000',
            '--workers',
            workers,
            '--timeout',
            '60',
            '--access-logfile',
            '-',
            '--error-logfile',
            '-',
        ],
    )


if __name__ == '__main__':
    main()
