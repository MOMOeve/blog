from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.mediahub.models import Photo
from apps.mediahub.placeholders import sync_to_frontend_public, write_placeholder_svg

# 本地 SVG 占位图（不依赖外网图床）
SEED_PHOTOS = [
    {
        'slug': 'fuji',
        'title': '富士山倒影',
        'location': '日本·山梨县',
        'taken_on': '2026年5月',
        'aspect': 'landscape',
        'category': '自然',
        'description': '湖面如镜，倒映着那座永恒的山。黎明前的蓝，是宇宙最深处的颜色。',
        'sort_order': 1,
        'colors': ('#0a1628', '#1a3a5c', '#7eb8f7'),
    },
    {
        'slug': 'dusk-road',
        'title': '黄昏公路',
        'location': '法国·普罗旺斯',
        'taken_on': '2026年4月',
        'aspect': 'landscape',
        'category': '旅行',
        'description': '光把道路变成了一条流动的金河，通向某个还不知道名字的地方。',
        'sort_order': 2,
        'colors': ('#1a0f08', '#8b4513', '#f5c842'),
    },
    {
        'slug': 'kyoto',
        'title': '京都小巷',
        'location': '日本·京都',
        'taken_on': '2026年3月',
        'aspect': 'portrait',
        'category': '城市',
        'description': '石板路在细雨中发光，每一块都像一片被时间打磨过的记忆。',
        'sort_order': 3,
        'colors': ('#12101a', '#3d2a4a', '#c4a0d8'),
    },
    {
        'slug': 'osaka',
        'title': '大阪街道',
        'location': '日本·大阪',
        'taken_on': '2026年3月',
        'aspect': 'landscape',
        'category': '城市',
        'description': '霓虹与人潮，现代与传统，在同一条街道上安然共存。',
        'sort_order': 4,
        'colors': ('#0d0818', '#2a1840', '#ff6b9d'),
    },
    {
        'slug': 'rain-puddle',
        'title': '雨夜水洼',
        'location': '日本·东京',
        'taken_on': '2026年2月',
        'aspect': 'landscape',
        'category': '城市',
        'description': '世界在地上的积水里翻了个身，灯光在里面漂浮，比天上的星更近。',
        'sort_order': 5,
        'colors': ('#060a14', '#1a2840', '#4a90d9'),
    },
    {
        'slug': 'storm-cloud',
        'title': '积雨云',
        'location': '中国·云南',
        'taken_on': '2026年8月',
        'aspect': 'portrait',
        'category': '自然',
        'description': '云朵的阴影扫过山谷，凉意随之而来，像是大地在轻声叹息。',
        'sort_order': 6,
        'colors': ('#101820', '#3a4a58', '#a8b8c8'),
    },
    {
        'slug': 'coast',
        'title': '暮色海岸',
        'location': '希腊·圣托里尼',
        'taken_on': '2026年7月',
        'aspect': 'landscape',
        'category': '旅行',
        'description': '海与天在橙色中失去了边界，只剩下光本身在那里沉默地燃烧。',
        'sort_order': 7,
        'colors': ('#1a0a08', '#c45c20', '#f5c842'),
    },
    {
        'slug': 'neon',
        'title': '夜色霓虹',
        'location': '日本·大阪',
        'taken_on': '2026年3月',
        'aspect': 'portrait',
        'category': '城市',
        'description': '霓虹的光在潮湿的空气里洇开，像是一首被雨淋湿的诗。',
        'sort_order': 8,
        'colors': ('#080610', '#1a0a28', '#00e5ff'),
    },
    {
        'slug': 'above-clouds',
        'title': '云层之上',
        'location': '飞机·成都-东京',
        'taken_on': '2026年5月',
        'aspect': 'landscape',
        'category': '自然',
        'description': '从高处看，云是一片安静的海。我们每天都从它下面走过，却忘了它有多美。',
        'sort_order': 9,
        'colors': ('#0a1520', '#2a4a6a', '#e8f0f8'),
    },
]


class Command(BaseCommand):
    help = '导入演示摄影数据（生成本地占位图）'

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / 'photos'
        for item in SEED_PHOTOS:
            slug = item['slug']
            filename = f'{slug}.svg'
            path = media_dir / filename
            w, h = (900, 600) if item['aspect'] == 'landscape' else (600, 900)
            write_placeholder_svg(path, item['title'], width=w, height=h, colors=item['colors'])
            sync_to_frontend_public(path, f'photos/{filename}')
            photo, created = Photo.objects.update_or_create(
                title=item['title'],
                defaults={
                    'location': item['location'],
                    'taken_on': item['taken_on'],
                    'image_url': f'/media/photos/{filename}',
                    'aspect': item['aspect'],
                    'category': item['category'],
                    'description': item['description'],
                    'sort_order': item['sort_order'],
                    'published': True,
                },
            )
            action = '创建' if created else '更新'
            self.stdout.write(f'{action}: {photo.title} → {photo.image_url}')
        self.stdout.write(self.style.SUCCESS(f'完成，共 {Photo.objects.count()} 张照片'))
