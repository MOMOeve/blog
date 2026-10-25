"""本地 SVG 占位图生成（不依赖外网图床）。"""

from __future__ import annotations

from pathlib import Path


def write_placeholder_svg(
    path: Path,
    title: str,
    *,
    width: int = 900,
    height: int = 600,
    colors: tuple[str, str, str] = ('#0a1628', '#1a3a5c', '#7eb8f7'),
) -> None:
    c0, c1, c2 = colors
    path.parent.mkdir(parents=True, exist_ok=True)
    font_size = 28 if width >= height else 24
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c0}"/>
      <stop offset="55%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#g)"/>
  <circle cx="{width * 0.78}" cy="{height * 0.22}" r="{min(width, height) * 0.12}" fill="{c2}" opacity="0.35"/>
  <text x="50%" y="52%" text-anchor="middle" fill="#f0f4ff" font-family="Segoe UI, sans-serif"
        font-size="{font_size}" opacity="0.92">{title}</text>
</svg>
'''
    path.write_text(svg, encoding='utf-8')


def sync_to_frontend_public(src: Path, relative_under_media: str) -> Path | None:
    """把 media 文件同步到 frontend/public/media，便于 Vite 无后端时也能显示。"""
    try:
        from django.conf import settings

        blog_root = Path(settings.BASE_DIR).parent
        dest = blog_root / 'frontend' / 'public' / 'media' / relative_under_media
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        return dest
    except Exception:
        return None
