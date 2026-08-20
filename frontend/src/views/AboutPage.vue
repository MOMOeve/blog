<script setup lang="ts">
import { AVATAR_IMG } from '../data/posts'
import MediaCover from '../components/MediaCover.vue'

const timeline = [
  {
    year: '2020',
    title: '写下第一行代码',
    desc: '大学选修了一门 Python 课，交了第一份作业之后就再也停不下来了。那时候完全不知道自己在做什么，但调试成功的瞬间让人上瘾。',
  },
  {
    year: '2021',
    title: '开始自学前端',
    desc: 'HTML、CSS、JavaScript——一边跟着教程敲，一边做自己的小项目。踩了很多坑，学会了如何 Google 错误信息。',
  },
  {
    year: '2022',
    title: '语言学习起步',
    desc: '因为喜欢看动画和玩游戏，决定正式开始学语言。五十音图背了两遍才记住，ひらがな 写得歪歪扭扭，但很快就爱上了这门语言。',
  },
  {
    year: '2023',
    title: '通过 JLPT N3',
    desc: '备考四个月，N3 一次通过。意识到语言学习和编程有很多相通之处——都需要大量输入，都需要在实际使用中犯错，都无法靠死记硬背掌握。',
  },
  {
    year: '2024',
    title: '第一个上线的个人项目',
    desc: 'React + Node.js，从域名注册到部署用了快两个月。虽然没什么人用，但从那之后对整个 web 开发的链路有了完整的理解。',
  },
  {
    year: '2025',
    title: '通过 JLPT N2，开始写这个博客',
    desc: 'N2 通过之后决定把学习过程和代码笔记记录下来。写给未来的自己看，也希望对同样在路上的人有一点用。',
  },
]

const influences = [
  {
    name: 'Dan Abramov',
    field: 'React / 写作',
    quote: "Don't try to be clever. Write code that communicates.",
  },
  {
    name: 'Matt Pocock',
    field: 'TypeScript',
    quote: "TypeScript is not about restrictions. It's about communication.",
  },
  {
    name: '核心语言',
    field: '语言学习',
    quote: '语言学习最重要的是大量可理解输入，其次是开口用它。',
  },
  {
    name: 'Paul Graham',
    field: '写作 / 思维',
    quote: 'Writing is not just a way to communicate ideas. Writing is how you think.',
  },
]

const techStack = [
  { name: 'TypeScript + React', type: '主力前端' },
  { name: 'Node.js + Hono', type: '后端' },
  { name: 'PostgreSQL + Prisma', type: '数据库' },
  { name: 'Neovim + VS Code', type: '编辑器' },
  { name: 'Wezterm + zsh', type: '终端' },
  { name: 'Anki + Immersion Kit', type: '语言工具' },
  { name: 'WaniKani', type: '汉字记忆' },
  { name: 'Obsidian', type: '笔记' },
]

const stats = [
  { label: '语言学习', value: 'N2', sub: '目标 N1' },
  { label: '前端经验', value: '4 年', sub: '自学起步' },
  { label: 'Anki 卡片', value: '6,200+', sub: '累计复习' },
  { label: '个人项目', value: '11 个', sub: '3 个在用' },
]

const focusTags = ['React', 'TypeScript', 'Hono', '语言 N1', 'immersion learning', 'side projects']
</script>

<template>
  <div class="page-shell about">
    <div class="page-header" style="margin-bottom: 0">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner" style="padding-bottom: 0">
        <p class="page-eyebrow">✦ &nbsp; ABOUT</p>
        <h1 class="page-title">
          关于
          <span class="page-title__sub">· 一点自述</span>
        </h1>
      </div>
    </div>

    <div class="container about__profile">
      <div class="about__layout">
        <div class="about__aside">
          <div class="about__avatar">
            <MediaCover :src="AVATAR_IMG" alt="作者" label="星野凛" seed="avatar" />
          </div>
          <div class="about__identity">
            <h2 class="font-display">星野 凛</h2>
            <p class="font-body">Frontend Dev · 语言学习者</p>
            <div class="about__rule" />
            <div class="about__stats">
              <div v-for="s in stats" :key="s.label" class="stat">
                <p class="font-display">{{ s.value }}</p>
                <p class="font-body">{{ s.label }}</p>
                <span class="font-body">{{ s.sub }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="about__bio">
          <blockquote class="font-serif">
            "代码和语言，都是我试图理解世界的方式。<br />
            一个用逻辑，一个用语言。"
          </blockquote>
          <div class="about__text font-body">
            <p>
              我是一名自学前端开发者，同时也是一个语言学习者。技术栈以 TypeScript 和 React 为主，
              目前也在探索后端和全栈方向。代码对我来说不只是一门谋生技能，更是一种思考和创作的方式。
            </p>
            <p>
              学语言起初只是为了能看懂字幕，后来越学越深，现在已经通过了 JLPT N2，
              正在备考 N1。语言让我意识到：语言是文化的容器，每学会一种新的表达，
              就像是打开了看世界的一个新角度。
            </p>
            <p>
              这个博客是我的学习记录和思考出口。我不是什么权威，只是一个在路上的人，
              把走过的弯路和想清楚的事情写下来。如果对你也有用，那就更好了。
            </p>
          </div>
          <div class="about__tags">
            <span v-for="tag in focusTags" :key="tag" class="font-body">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="divider-light about__divider" />
    </div>

    <div class="container about__timeline">
      <h2 class="section-title font-display">
        <span class="bar" />
        学习时间线
        <span class="sub font-serif">· 从第一行代码到现在</span>
      </h2>
      <div class="timeline">
        <div v-for="(item, i) in timeline" :key="i" class="timeline__item">
          <div class="timeline__dot" />
          <div class="timeline__content">
            <span class="font-body year">{{ item.year }}</span>
            <div>
              <h3 class="font-display">{{ item.title }}</h3>
              <p class="font-body">{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container about__cols">
      <div>
        <h2 class="section-title font-display">
          <span class="bar" />
          影响我的人和资源
        </h2>
        <div class="influences">
          <div v-for="(inf, i) in influences" :key="i" class="influence">
            <div class="influence__avatar font-display">{{ inf.name[0] }}</div>
            <div>
              <div class="influence__head">
                <span class="font-display">{{ inf.name }}</span>
                <span class="font-body">· {{ inf.field }}</span>
              </div>
              <p class="font-serif">"{{ inf.quote }}"</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h2 class="section-title font-display">
          <span class="bar" />
          工具与技术栈
        </h2>
        <div class="stack">
          <div v-for="(item, i) in techStack" :key="i" class="stack__row">
            <div>
              <span class="dot" />
              <span class="name">{{ item.name }}</span>
            </div>
            <span class="type font-body">{{ item.type }}</span>
          </div>
        </div>
        <div class="stack__note">
          <p class="font-serif">
            工具会过时，但思考问题的方式不会。 选工具，选那个让你把精力放在真正重要的事情上的那个。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.about__profile {
  padding-top: 4rem;
  padding-bottom: 4rem;
}

.about__layout {
  display: grid;
  gap: 3.5rem;
  align-items: start;

  @media (min-width: 768px) {
    grid-template-columns: 260px 1fr;
  }
}

.about__aside {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;

  @media (min-width: 768px) {
    align-items: flex-start;
  }
}

.about__avatar {
  width: 12rem;
  height: 12rem;
  overflow: hidden;
  border: 1px solid rgba(245, 200, 66, 0.25);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
    filter: saturate(0.85) brightness(0.85);
  }
}

.about__identity {
  text-align: center;
  width: 100%;

  @media (min-width: 768px) {
    text-align: left;
  }

  h2 {
    font-size: 1.125rem;
    color: var(--color-fg);
    letter-spacing: 0.1em;
    margin: 0 0 0.125rem;
  }

  > .font-body {
    font-size: 0.75rem;
    color: var(--color-secondary);
    letter-spacing: 0.2em;
    margin: 0 0 1.25rem;
  }
}

.about__rule {
  height: 1px;
  margin-bottom: 1.25rem;
  background: linear-gradient(90deg, rgba(245, 200, 66, 0.3), transparent);
}

.about__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.stat {
  padding: 0.75rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: rgba(11, 16, 40, 0.5);

  .font-display {
    font-size: 1rem;
    color: var(--color-primary);
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0 0 0.25rem;
  }

  .font-body {
    font-size: 0.6rem;
    color: var(--color-dim);
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0;
  }

  span {
    display: block;
    font-size: 0.58rem;
    color: #2f3f56;
    letter-spacing: 0.05em;
    margin-top: 0.125rem;
  }
}

.about__bio {
  blockquote {
    margin: 0 0 1.5rem;
    padding: 0 0 0 1.5rem;
    border-left: 2px solid rgba(245, 200, 66, 0.3);
    background: rgba(245, 200, 66, 0.02);
    font-style: italic;
    font-size: 1.125rem;
    color: var(--color-soft);
    line-height: 2;
  }
}

.about__text {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  font-size: 0.875rem;
  color: var(--color-muted-fg);
  line-height: 1.8;
  font-weight: 300;

  p {
    margin: 0;
  }
}

.about__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 0.5rem;

  span {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    padding: 0.25rem 0.75rem;
    border: 1px solid rgba(126, 184, 247, 0.15);
    color: var(--color-secondary);
    background: rgba(126, 184, 247, 0.05);
  }
}

.about__divider {
  margin-bottom: 4rem;
}

.about__timeline {
  margin-bottom: 5rem;
}

.section-title {
  font-size: 1rem;
  color: var(--color-fg);
  letter-spacing: 0.12em;
  margin: 0 0 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;

  .bar {
    width: 1.5rem;
    height: 1px;
    background: var(--color-secondary);
    opacity: 0.5;
  }

  .sub {
    font-style: italic;
    color: #3d5070;
    font-size: 0.875rem;
    font-weight: 400;
  }
}

.timeline {
  position: relative;
  padding-left: 1.5rem;

  @media (min-width: 768px) {
    padding-left: 3rem;
  }

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.5rem;
    bottom: 0.5rem;
    width: 1px;
    background: linear-gradient(
      180deg,
      rgba(126, 184, 247, 0.3),
      rgba(245, 200, 66, 0.2),
      rgba(126, 184, 247, 0.1)
    );

    @media (min-width: 768px) {
      left: 1rem;
    }
  }
}

.timeline__item {
  position: relative;
  margin-bottom: 2.5rem;

  &:hover .timeline__dot {
    border-color: var(--color-primary);
    box-shadow: 0 0 8px rgba(245, 200, 66, 0.4);
  }
}

.timeline__dot {
  position: absolute;
  left: -1.5rem;
  top: 0.375rem;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: var(--color-bg);
  border: 1px solid rgba(245, 200, 66, 0.5);
  transition: all 0.3s;

  @media (min-width: 768px) {
    left: -3rem;
  }
}

.timeline__content {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;

  .year {
    font-family: ui-monospace, monospace;
    font-size: 0.75rem;
    color: var(--color-primary);
    letter-spacing: 0.1em;
    flex-shrink: 0;
    margin-top: 0.125rem;
    opacity: 0.7;
  }

  h3 {
    font-size: 0.875rem;
    color: var(--color-fg);
    letter-spacing: 0.06em;
    margin: 0 0 0.5rem;
  }

  p {
    font-size: 0.75rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    margin: 0;
  }
}

.about__cols {
  display: grid;
  gap: 2.5rem;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.influences {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.influence {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid rgba(126, 184, 247, 0.07);
  background: rgba(11, 16, 40, 0.5);
  transition: border-color 0.3s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.18);
  }
}

.influence__avatar {
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  border: 1px solid rgba(245, 200, 66, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.influence__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;

  .font-display {
    font-size: 0.75rem;
    color: var(--color-fg);
    letter-spacing: 0.05em;
  }

  .font-body {
    font-size: 0.6rem;
    color: #3d5070;
    letter-spacing: 0.05em;
  }
}

.influence .font-serif {
  margin: 0;
  font-style: italic;
  font-size: 0.75rem;
  color: var(--color-dim);
  line-height: 1.6;
}

.stack__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(126, 184, 247, 0.07);

  > div {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--color-secondary);
    opacity: 0.5;
    transition: all 0.2s;
  }

  .name {
    font-family: ui-monospace, monospace;
    font-size: 0.875rem;
    color: var(--color-soft);
    transition: color 0.2s;
  }

  .type {
    font-size: 0.65rem;
    color: #3d5070;
    letter-spacing: 0.05em;
  }

  &:hover {
    .dot {
      opacity: 1;
      box-shadow: 0 0 4px #7eb8f7;
    }

    .name {
      color: var(--color-fg);
    }
  }
}

.stack__note {
  margin-top: 2rem;
  padding: 1.25rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: linear-gradient(135deg, rgba(11, 16, 40, 0.7), rgba(8, 12, 28, 0.8));

  p {
    margin: 0;
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-muted-fg);
    line-height: 1.8;
  }
}
</style>
