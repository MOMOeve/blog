from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.content.models import Category, Post, Tag
from apps.mediahub.placeholders import sync_to_frontend_public, write_placeholder_svg

COVER_COLORS = [
    ('#0a1628', '#1a3a5c', '#7eb8f7'),
    ('#1a0f08', '#8b4513', '#f5c842'),
    ('#12101a', '#3d2a4a', '#c4a0d8'),
    ('#0d0818', '#2a1840', '#ff6b9d'),
    ('#060a14', '#1a2840', '#4a90d9'),
    ('#101820', '#3a4a58', '#a8b8c8'),
    ('#1a0a08', '#c45c20', '#f5c842'),
    ('#080610', '#1a0a28', '#00e5ff'),
    ('#0a1520', '#2a4a6a', '#e8f0f8'),
]

SEED_POSTS = [
    {
        'slug': 'typescript-rewrite',
        'title': '用 TypeScript 重写了整个项目之后',
        'title_en': 'After Rewriting the Entire Project in TypeScript',
        'category': '代码',
        'date': (2026, 8, 14),
        'read_time': '10 分钟',
        'excerpt': '花了两周时间把一个积累了三年的 JavaScript 项目迁移到 TypeScript。过程痛苦，结果值得——不只是类型安全，更是一次强迫自己重新理解整个代码结构的机会。',
        'featured': True,
        'tags': ['代码', 'TypeScript'],
    },
    {
        'slug': 'jlpt-n2',
        'title': 'JLPT N2 备考：那些真正有用的方法',
        'title_en': 'JLPT N2 Prep: Methods That Actually Worked',
        'category': '语言',
        'date': (2026, 7, 28),
        'read_time': '8 分钟',
        'excerpt': '备考六个月，刷了三套真题，最后以 142 分通过。回头看，有些方法确实有效，有些完全是在浪费时间。这篇写给同样在准备 N2 的你。',
        'featured': False,
        'tags': ['语言', 'JLPT'],
    },
    {
        'slug': 'code-at-2am',
        'title': '深夜写代码是一种什么体验',
        'title_en': 'What It Feels Like to Code at 2 AM',
        'category': '生活',
        'date': (2026, 7, 10),
        'read_time': '5 分钟',
        'excerpt': '凌晨两点，一个 bug 终于复现了。窗外的城市安静下来，屏幕的光是房间里唯一的颜色。这种时刻有一种奇怪的专注，像是整个世界只剩下你和这段代码。',
        'featured': False,
        'tags': ['生活', '随笔'],
    },
    {
        'slug': 'zustand',
        'title': 'React 状态管理：我从 Redux 换到了 Zustand',
        'title_en': 'State Management: Why I Switched from Redux to Zustand',
        'category': '代码',
        'date': (2026, 6, 22),
        'read_time': '7 分钟',
        'excerpt': '不是说 Redux 不好，而是对于中型项目，它的样板代码确实太多了。Zustand 让我写得更少，想得更清楚。附上迁移过程中踩过的几个坑。',
        'featured': False,
        'tags': ['代码', 'React'],
    },
    {
        'slug': 'naming-joke',
        'title': '为什么我用语言给变量命名（开玩笑的）',
        'title_en': 'Why I Name Variables in Japanese (Just Kidding)',
        'category': '语言',
        'date': (2026, 6, 5),
        'read_time': '4 分钟',
        'excerpt': '学语言和写代码有一个共同点：你以为你理解了，直到你试着用它解释一件事，才发现自己其实一知半解。语言学习就像 debug，总在意想不到的地方出错。',
        'featured': False,
        'tags': ['语言', '随笔'],
    },
    {
        'slug': 'side-project',
        'title': '记录一次完整的个人项目从零到上线',
        'title_en': 'A Full Journey: From Zero to Deployed Side Project',
        'category': '代码',
        'date': (2026, 5, 18),
        'read_time': '12 分钟',
        'excerpt': '从想法到上线用了四十天。技术栈选择、数据库设计、部署踩坑，以及最后没人用的轻微沮丧——全都记在这里了。',
        'featured': False,
        'tags': ['代码', '项目'],
    },
    {
        'slug': 'anki-review',
        'title': 'Anki 用了两年之后，我的诚实评价',
        'title_en': 'My Honest Review of Anki After Two Years',
        'category': '语言',
        'date': (2026, 5, 3),
        'read_time': '6 分钟',
        'excerpt': 'Anki 不是万能的，但它确实改变了我记单词的方式。间隔重复这件事一旦理解了原理，就很难再用其他方法。聊聊我怎么建牌、怎么坚持的。',
        'featured': False,
        'tags': ['语言', '工具'],
    },
    {
        'slug': 'dev-setup-2026',
        'title': '我的开发环境配置（2026版）',
        'title_en': 'My Dev Environment Setup (2026 Edition)',
        'category': '代码',
        'date': (2026, 4, 15),
        'read_time': '9 分钟',
        'excerpt': 'Terminal、编辑器、常用工具、字体、主题……每隔一段时间整理一次自己的开发环境，其实也是一次审视自己工作习惯的机会。',
        'featured': False,
        'tags': ['代码', '工具'],
    },
    {
        'slug': 'n3-grammar',
        'title': '从零开始学 N3 文法的那半年',
        'title_en': 'The Six Months I Spent Learning N3 Grammar from Zero',
        'category': '语言',
        'date': (2026, 3, 28),
        'read_time': '11 分钟',
        'excerpt': '「〜ところだ」和「〜ばかりだ」到底有什么区别？学语言的人都懂那种感觉：每搞懂一个文法，就又发现一个更令人头大的。但这就是乐趣所在。',
        'featured': False,
        'tags': ['语言', '文法'],
    },
]


class Command(BaseCommand):
    help = '导入演示文章数据（本地封面图），并创建演示账号 demo@example.com / demo1234'

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@example.com', 'is_staff': True},
        )
        if created or not user.has_usable_password():
            user.set_password('demo1234')
            user.email = 'demo@example.com'
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS('创建演示账号 demo@example.com / demo1234'))
        else:
            self.stdout.write('演示账号已存在')

        site_dir = Path(settings.MEDIA_ROOT) / 'site'
        covers_dir = Path(settings.MEDIA_ROOT) / 'covers'

        hero_path = site_dir / 'hero.svg'
        write_placeholder_svg(
            hero_path,
            '星野文记',
            width=1800,
            height=900,
            colors=('#060a18', '#1a2848', '#f5c842'),
        )
        sync_to_frontend_public(hero_path, 'site/hero.svg')

        avatar_path = site_dir / 'avatar.svg'
        write_placeholder_svg(
            avatar_path,
            '星野凛',
            width=400,
            height=400,
            colors=('#121a2e', '#3b7fc4', '#7eb8f7'),
        )
        sync_to_frontend_public(avatar_path, 'site/avatar.svg')
        self.stdout.write('站点图：/media/site/hero.svg, /media/site/avatar.svg')

        for i, item in enumerate(SEED_POSTS):
            category, _ = Category.objects.get_or_create(name=item['category'])
            tag_objs = []
            for tag_name in item['tags']:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tag_objs.append(tag)

            filename = f"{item['slug']}.svg"
            cover_path = covers_dir / filename
            write_placeholder_svg(
                cover_path,
                item['title'][:12],
                width=900,
                height=500,
                colors=COVER_COLORS[i % len(COVER_COLORS)],
            )
            sync_to_frontend_public(cover_path, f'covers/{filename}')
            cover_url = f'/media/covers/{filename}'

            published_at = timezone.make_aware(datetime(*item['date'], 12, 0, 0))
            post, created_post = Post.objects.update_or_create(
                title=item['title'],
                defaults={
                    'title_en': item['title_en'],
                    'category': category,
                    'excerpt': item['excerpt'],
                    'body': item['excerpt'],
                    'cover_image': cover_url,
                    'read_time': item['read_time'],
                    'featured': item['featured'],
                    'published': True,
                    'author': user,
                    'published_at': published_at,
                },
            )
            post.tags.set(tag_objs)
            action = '创建' if created_post else '更新'
            self.stdout.write(f'{action}: {post.title} → {cover_url}')

        self.stdout.write(self.style.SUCCESS(f'完成，共 {Post.objects.count()} 篇文章'))
