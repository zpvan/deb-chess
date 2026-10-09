# Material You 改版实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 deb-chess 前端从暖纸色绘本风全面改为 Material 3(Material You)蓝色单主色风格,支持浅色/深色切换。

**Architecture:** 纯前端改版,后端零改动。核心是一套双主题 CSS 变量(`src/index.css`)+ Tailwind 色名映射(`tailwind.config.js`),组件内的硬编码色逐个替换为语义化变量;新增 useDarkMode hook 与 ThemeToggle 组件。

**Tech Stack:** Tailwind CSS 3.4(darkMode: class 已配好)、React 19、Playwright(视觉验证)。

**Spec:** `docs/superpowers/specs/2026-10-09-material-you-redesign-design.md`

## Token 总表(所有任务共用,后续任务引用此表)

| Tailwind 色名 | 浅色值 | 深色值 | 用途 |
|---|---|---|---|
| `primary` | #0B57D0 | #A8C7FA | 主按钮、强调 |
| `on-primary` | #FFFFFF | #062E6F | primary 上的文字 |
| `primary-container` | #D3E3FD | #004A77 | 徽章、选中态、浅色强调底 |
| `on-primary-container` | #041E49 | #D3E3FD | primary-container 上的文字 |
| `surface` | #F9F9FF | #121318 | 页面背景、顶栏 |
| `surface-container` | #EDEDF4 | #1E1F25 | 卡片 |
| `on-surface` | #191C20 | #E2E2E9 | 正文 |
| `on-surface-variant` | #44474E | #C4C6D0 | 次要文字 |
| `outline-variant` | #C4C6D0 | #44474E | 细分割线、非强调描边 |
| `success-container` | #C2E8CE | #0E3A1F | 答对提示框底 |
| `on-success-container` | #0E3A1F | #C2E8CE | 答对提示框字 |
| `error-container` | #F9DEDC | #5C1410 | 答错/失败提示框底 |
| `on-error-container` | #410E0B | #F9DEDC | 答错提示框字 |
| `star` | #F9AB00 | #FDD663 | 星星、当前步骤圆点 |
| `hint-container` | #FFF3CD | #3E3000 | 提示框底 |
| `on-hint-container` | #574500 | #FFE082 | 提示框字 |
| `board-light` | #E8EEF9 | #3D4351 | 棋盘浅格 |
| `board-dark` | #769CDF | #5A6B8C | 棋盘深格 |
| `board-last-light` | #B3CCF5 | #4A5570 | 最近一步·浅格 |
| `board-last-dark` | #5B84CC | #6B7DA0 | 最近一步·深格 |
| `board-select` | #A8C7FA | #7DA4E8 | 选中格 |
| `board-check` | #EA4335 | #F28B82 | 被将军的王格 |

阴影:卡片 `shadow-[0_1px_2px_rgba(0,0,0,0.1),0_1px_3px_1px_rgba(0,0,0,0.07)]`(elevation 1);hover/主按钮 `shadow-[0_1px_2px_rgba(0,0,0,0.15),0_2px_6px_2px_rgba(0,0,0,0.1)]`(elevation 2)。

---

### Task 1: 主题 token 与 Tailwind 映射

**Files:**
- Modify: `src/index.css`(全量替换)
- Modify: `tailwind.config.js`(全量替换)

- [ ] **Step 1: 全量替换 src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ===== Material You 主题 token(浅色 / 深色)===== */
@layer base {
  :root {
    --primary: #0b57d0;
    --on-primary: #ffffff;
    --primary-container: #d3e3fd;
    --on-primary-container: #041e49;
    --surface: #f9f9ff;
    --surface-container: #ededf4;
    --on-surface: #191c20;
    --on-surface-variant: #44474e;
    --outline-variant: #c4c6d0;
    --success-container: #c2e8ce;
    --on-success-container: #0e3a1f;
    --error-container: #f9dedc;
    --on-error-container: #410e0b;
    --star: #f9ab00;
    --hint-container: #fff3cd;
    --on-hint-container: #574500;
    --board-light: #e8eef9;
    --board-dark: #769cdf;
    --board-last-light: #b3ccf5;
    --board-last-dark: #5b84cc;
    --board-select: #a8c7fa;
    --board-check: #ea4335;
  }

  .dark {
    --primary: #a8c7fa;
    --on-primary: #062e6f;
    --primary-container: #004a77;
    --on-primary-container: #d3e3fd;
    --surface: #121318;
    --surface-container: #1e1f25;
    --on-surface: #e2e2e9;
    --on-surface-variant: #c4c6d0;
    --outline-variant: #44474e;
    --success-container: #0e3a1f;
    --on-success-container: #c2e8ce;
    --error-container: #5c1410;
    --on-error-container: #f9dedc;
    --star: #fdd663;
    --hint-container: #3e3000;
    --on-hint-container: #ffe082;
    --board-light: #3d4351;
    --board-dark: #5a6b8c;
    --board-last-light: #4a5570;
    --board-last-dark: #6b7da0;
    --board-select: #7da4e8;
    --board-check: #f28b82;
  }

  html {
    -webkit-font-smoothing: antialiased;
  }

  body {
    font-family: Roboto, -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: var(--on-surface);
    background-color: var(--surface);
    transition: background-color 0.2s ease, color 0.2s ease;
  }
}

.font-display {
  font-family: Roboto, -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-weight: 700;
  letter-spacing: 0.01em;
}

/* Material elevation */
.elev-1 {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1), 0 1px 3px 1px rgba(0, 0, 0, 0.07);
}
.elev-2 {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15), 0 2px 6px 2px rgba(0, 0, 0, 0.1);
}
/* state layer:按钮 hover 遮罩 */
.state-layer {
  position: relative;
}
.state-layer:hover::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: currentColor;
  opacity: 0.08;
  pointer-events: none;
}

@keyframes boardshake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  60% { transform: translateX(-5px); }
  80% { transform: translateX(5px); }
}

@keyframes confetti-fall {
  0% { transform: translateY(-5vh) rotate(0deg); opacity: 1; }
  100% { transform: translateY(110vh) rotate(720deg); opacity: 0.6; }
}
```

注意:原 shadcn 的 `--background` 等 HSL token 全部删除(ui 组件库已删,无人引用)。

- [ ] **Step 2: 全量替换 tailwind.config.js**

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        "on-primary": "var(--on-primary)",
        "primary-container": "var(--primary-container)",
        "on-primary-container": "var(--on-primary-container)",
        surface: "var(--surface)",
        "surface-container": "var(--surface-container)",
        "on-surface": "var(--on-surface)",
        "on-surface-variant": "var(--on-surface-variant)",
        "outline-variant": "var(--outline-variant)",
        "success-container": "var(--success-container)",
        "on-success-container": "var(--on-success-container)",
        "error-container": "var(--error-container)",
        "on-error-container": "var(--on-error-container)",
        star: "var(--star)",
        "hint-container": "var(--hint-container)",
        "on-hint-container": "var(--on-hint-container)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

- [ ] **Step 3: 验证构建**

Run: `npm run build`
Expected: 构建成功(TS 无错;页面此时配色会乱,属预期,后续任务修复组件)。

- [ ] **Step 4: Commit**

```bash
git add src/index.css tailwind.config.js
git commit -m "feat: Material You theme tokens and tailwind mapping"
```

### Task 2: 深色模式基础设施

**Files:**
- Create: `src/hooks/useDarkMode.ts`
- Create: `src/components/ThemeToggle.tsx`
- Modify: `index.html`(Roboto + 防闪烁脚本)

- [ ] **Step 1: useDarkMode hook**

`src/hooks/useDarkMode.ts`:

```ts
import { useCallback, useEffect, useState } from 'react'

const KEY = 'deb-chess-theme'

function initial(): boolean {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'dark') return true
    if (saved === 'light') return false
  } catch { /* ignore */ }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

export function useDarkMode(): [boolean, () => void] {
  const [dark, setDark] = useState<boolean>(initial)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try {
      localStorage.setItem(KEY, dark ? 'dark' : 'light')
    } catch { /* ignore */ }
  }, [dark])

  const toggle = useCallback(() => setDark((d) => !d), [])
  return [dark, toggle]
}
```

- [ ] **Step 2: ThemeToggle 组件**

`src/components/ThemeToggle.tsx`:

```tsx
import { Moon, Sun } from 'lucide-react'
import { useDarkMode } from '@/hooks/useDarkMode'

export default function ThemeToggle() {
  const [dark, toggle] = useDarkMode()
  return (
    <button
      onClick={toggle}
      aria-label={dark ? '切换到浅色模式' : '切换到深色模式'}
      className="p-2 rounded-full text-on-surface-variant hover:bg-on-surface/10 transition"
    >
      {dark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
```

- [ ] **Step 3: index.html 引入 Roboto + 防闪烁脚本**

替换 `<head>` 内的 title 行,在其后追加:

```html
    <title>deb-chess 练级营</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet" />
    <script>
      (function () {
        var t = null
        try { t = localStorage.getItem('deb-chess-theme') } catch (e) {}
        var dark = t === 'dark' || (t !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches)
        if (dark) document.documentElement.classList.add('dark')
      })()
    </script>
```

- [ ] **Step 4: 验证构建 + 手动检查**

Run: `npm run build`(构建成功),`./start.sh` 起服务,控制台执行 `document.documentElement.classList.add('dark')` 后 body 背景应变深色(#121318)。

- [ ] **Step 5: Commit**

```bash
git add src/hooks/useDarkMode.ts src/components/ThemeToggle.tsx index.html
git commit -m "feat: dark mode infrastructure with theme toggle"
```

### Task 3: ChessBoard 配色 token 化

**Files:**
- Modify: `src/components/ChessBoard.tsx`

- [ ] **Step 1: 替换棋盘配色**

`src/components/ChessBoard.tsx` 中 `backgroundColor` 三元表达式整体替换为:

```tsx
                style={{
                  backgroundColor: isCheck
                    ? 'var(--board-check)'
                    : isSel
                      ? 'var(--board-select)'
                      : isHi
                        ? 'var(--primary-container)'
                        : isLast
                          ? dark
                            ? 'var(--board-last-dark)'
                            : 'var(--board-last-light)'
                          : dark
                            ? 'var(--board-dark)'
                            : 'var(--board-light)',
                }}
```

- [ ] **Step 2: 目标点/吃子圈/箭头/描边/坐标文字换 token**

同文件中:
- 空位目标点:`bg-[#2e7d52]/60` → `bg-primary/60`
- 吃子圈:`ring-[#e05252]/80` → `ring-[var(--board-check)]/80`
- 箭头 marker `<path ... fill="#2e7d52" />` → `fill="var(--primary)"`
- 箭头 `<line ... stroke="#2e7d52"` → `stroke="var(--primary)"`
- 外框:`ring-[#7a5a33]` → `ring-[var(--outline-variant)]`;阴影 `shadow-[0_18px_40px_-18px_rgba(80,50,10,0.45)]` → `shadow-[0_18px_40px_-18px_rgba(0,0,0,0.4)]`
- 两处坐标文字颜色:`dark ? 'text-[#f3e3c3]' : 'text-[#b07848]'` → `dark ? 'text-[var(--board-light)]' : 'text-[var(--board-dark)]'`
- 棋子颜色保留不动(白子 #ffffff/黑子 #2b2118 在两种主题下对比度都够;棋子 textShadow 不动)。

- [ ] **Step 3: 验证构建**

Run: `npm run build`
Expected: 构建成功。

- [ ] **Step 4: Commit**

```bash
git add src/components/ChessBoard.tsx
git commit -m "feat: tokenize chess board colors for Material You"
```

### Task 4: Home 页 Material 化

**Files:**
- Modify: `src/pages/Home.tsx`(全量替换)

- [ ] **Step 1: 全量替换 Home.tsx**

```tsx
import ChessBoard from '@/components/ChessBoard'
import ThemeToggle from '@/components/ThemeToggle'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, BookOpen, Crown, Swords, Flag, Gamepad2 } from 'lucide-react'

interface Props {
  onStart: () => void
}

export default function Home({ onStart }: Props) {
  const { xp, totalStars, rank, starsOf } = useProgress()
  const { flatLevels, totalPuzzles } = useCurriculum()
  const nextLevel = flatLevels.find((f) => starsOf(f.level.id) === 0)

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* 顶栏 */}
      <header className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <span className="text-3xl" style={{ fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif' }}>♞</span>
          <span className="font-display text-xl flex-1">deb-chess 练级营</span>
          <div className="flex items-center gap-1 text-sm font-bold bg-primary-container text-on-primary-container px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-star text-star" /> {totalStars}
          </div>
          <div className="hidden sm:block text-sm font-bold bg-surface-container px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {xp}分
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* 主视觉 */}
      <section className="max-w-5xl mx-auto px-4 pt-10 pb-14 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary-container text-on-primary-container text-sm font-bold mb-5">
            世界冠军鲍比·菲舍尔的学棋方法
          </div>
          <h1 className="font-display text-4xl sm:text-5xl leading-tight mb-5">
            从<span className="text-primary">终局</span>开始,
            <br />
            一步步成为小棋王!
          </h1>
          <p className="text-lg text-on-surface-variant leading-relaxed mb-8">
            专为一年级小棋士设计:先看图想一想,再动手走棋,答对就能赢星星。
            跟着菲舍尔的练习法,从最简单的“底线杀”练起,直到学会完整的开局!
          </p>
          <div className="flex flex-wrap gap-4">
            <button onClick={onStart}
              className="state-layer px-8 py-4 rounded-full bg-primary text-on-primary font-display text-xl flex items-center gap-2 transition elev-2 hover:-translate-y-0.5">
              <Play size={22} className="fill-current" />
              {nextLevel && nextLevel.index > 0 ? `继续闯关(第 ${nextLevel.index + 1} 关)` : '开始闯关'}
            </button>
          </div>
          <div className="mt-6 flex items-center gap-4 text-sm text-on-surface-variant">
            <span>♟ 共 {flatLevels.length} 关</span>
            <span>⭐ {totalPuzzles} 道互动棋题</span>
            <span>⚔️ 实战对弈</span>
            <span>🏆 星星奖励</span>
          </div>
        </div>
        <div className="max-w-[420px] w-full mx-auto">
          <ChessBoard
            fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"
            arrows={[['a1', 'a8']]}
            highlight={['f7', 'g7', 'h7']}
          />
          <p className="text-center text-sm text-on-surface-variant mt-3 font-bold">
            菲舍尔最著名的“底线杀”:车冲 a8,黑王被自己的小兵困住!
          </p>
        </div>
      </section>

      {/* 学习路径 */}
      <section className="max-w-5xl mx-auto px-4 pb-16">
        <h2 className="font-display text-3xl mb-2 text-center">为什么是“倒着学”?</h2>
        <p className="text-center text-on-surface-variant mb-10 max-w-xl mx-auto">
          菲舍尔在《Bobby Fischer Teaches Chess》里说:先学杀王,棋越下越有目标。本站按这个思路设计了三段旅程。
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              icon: <Crown size={26} />,
              color: '#2E7D52',
              title: '第一章 · 终局',
              desc: '单车、单后、单马、单象、单兵——谁能杀光杆王?怎么杀?',
            },
            {
              icon: <Swords size={26} />,
              color: '#E07B2A',
              title: '第二章 · 中局',
              desc: '击双、牵制、闪将、得子四大武器,挑战“连续杀”。',
            },
            {
              icon: <Flag size={26} />,
              color: '#2F6FBA',
              title: '第三章 · 开局',
              desc: '意大利、西班牙、后翼弃兵、西西里、古印度——经典开局套路一网打尽。',
            },
            {
              icon: <Gamepad2 size={26} />,
              color: '#7C4DA0',
              title: '实战篇 · 对弈',
              desc: '和电脑真刀真枪下棋,再用“车王杀王”实操检验真本事。',
            },
          ].map((c) => (
            <div key={c.title} className="rounded-3xl p-6 bg-surface-container hover:-translate-y-1 transition elev-1 hover:elev-2">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white mb-4" style={{ backgroundColor: c.color }}>
                {c.icon}
              </div>
              <h3 className="font-display text-xl mb-2" style={{ color: c.color }}>{c.title}</h3>
              <p className="text-on-surface-variant leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 菲舍尔方法 */}
      <section className="bg-primary-container text-on-primary-container py-14">
        <div className="max-w-5xl mx-auto px-4 grid md:grid-cols-[auto_1fr] gap-8 items-center">
          <div className="text-7xl text-center" style={{ fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif' }}>♚</div>
          <div>
            <div className="flex items-center gap-2 mb-3 font-bold">
              <BookOpen size={18} /> 菲舍尔练习法
            </div>
            <blockquote className="text-lg leading-relaxed">
              “这本书会教你更快地分析棋题,找到要记住的关键模式。
              只要从头开始一题一题做下去,几秒钟之内你就能认出杀棋。”
            </blockquote>
            <p className="mt-3 opacity-75">—— 鲍比·菲舍尔,14 岁成为美国冠军,后来的世界冠军</p>
          </div>
        </div>
      </section>

      <footer className="max-w-5xl mx-auto px-4 py-8 text-center text-sm text-on-surface-variant">
        <p>学习进度保存在本机服务器的数据库里,换浏览器也不丢哦。</p>
      </footer>
    </div>
  )
}
```

- [ ] **Step 2: 验证构建**

Run: `npm run build`
Expected: 构建成功。

- [ ] **Step 3: Commit**

```bash
git add src/pages/Home.tsx
git commit -m "feat: restyle home page to Material You"
```

### Task 5: Map 页 Material 化

**Files:**
- Modify: `src/pages/Map.tsx`(全量替换)

- [ ] **Step 1: 全量替换 Map.tsx**

```tsx
import ThemeToggle from '@/components/ThemeToggle'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, ChevronLeft } from 'lucide-react'

interface Props {
  onOpen: (levelId: string) => void
  onHome: () => void
}

export default function MapPage({ onOpen, onHome }: Props) {
  const { starsOf, totalStars, xp, rank } = useProgress()
  const { chapters, flatLevels } = useCurriculum()

  return (
    <div className="min-h-screen bg-surface text-on-surface pb-24">
      {/* 顶部状态栏 */}
      <div className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onHome} className="p-2 rounded-full hover:bg-on-surface/10 transition" aria-label="首页">
            <ChevronLeft size={22} />
          </button>
          <div className="font-display text-xl flex-1">闯关地图</div>
          <div className="flex items-center gap-1 text-sm font-bold bg-primary-container text-on-primary-container px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-star text-star" /> {totalStars}
          </div>
          <div className="text-sm font-bold bg-surface-container px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {xp}分
          </div>
          <ThemeToggle />
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-8">
        {chapters.map((ch) => (
          <section key={ch.id} className="mb-12">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-display text-lg shrink-0 elev-1"
                style={{ backgroundColor: ch.color }}>
                {ch.badge.slice(0, 2)}
              </div>
              <div>
                <h2 className="font-display text-2xl" style={{ color: ch.color }}>{ch.title}</h2>
                <p className="text-on-surface-variant text-[15px] leading-relaxed">{ch.intro}</p>
              </div>
            </div>

            <div className="relative ml-6 border-l-4 border-dashed border-outline-variant pl-8 flex flex-col gap-4">
              {ch.levels.map((lv) => {
                const stars = starsOf(lv.id)
                const idx = flatLevels.findIndex((f) => f.level.id === lv.id)
                return (
                  <button
                    key={lv.id}
                    onClick={() => onOpen(lv.id)}
                    className="relative text-left rounded-3xl p-5 transition group bg-surface-container elev-1 hover:elev-2 hover:-translate-y-0.5"
                  >
                    <span className="absolute -left-[47px] top-1/2 -translate-y-1/2 w-6 h-6 rounded-full border-4 border-[var(--surface)]"
                      style={{ backgroundColor: stars > 0 ? ch.color : 'var(--star)' }} />
                    <div className="flex items-center gap-4">
                      <div className="w-11 h-11 rounded-full flex items-center justify-center font-display text-lg shrink-0"
                        style={{ backgroundColor: `${ch.color}22`, color: ch.color }}>
                        {stars > 0 ? <Star size={20} className="fill-current" /> : <Play size={18} className="fill-current" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-display text-lg leading-tight">
                          第 {idx + 1} 关 · {lv.title}
                        </div>
                        <div className="text-sm text-on-surface-variant">{lv.goal}</div>
                      </div>
                      {stars > 0 && (
                        <div className="flex gap-0.5 shrink-0">
                          {[1, 2, 3].map((n) => (
                            <Star key={n} size={18} strokeWidth={1.5}
                              className={n <= stars ? 'fill-star text-star' : 'fill-outline-variant/30 text-outline-variant'} />
                          ))}
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </section>
        ))}

        <p className="text-center text-sm text-on-surface-variant mt-4">
          跟着菲舍尔的方法:先把终局的“杀王”练熟,再学中局战术,最后学开局。循序渐进,每关都能拿星星!
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证构建**

Run: `npm run build`
Expected: 构建成功。

- [ ] **Step 3: Commit**

```bash
git add src/pages/Map.tsx
git commit -m "feat: restyle map page to Material You"
```

### Task 6: Lesson 页 Material 化

**Files:**
- Modify: `src/pages/Lesson.tsx`(全量替换)

说明:逻辑部分(state、handlers)与现状完全一致,只替换视觉。`st.chapter_soft` 弃用(背景统一 surface);章节色 `accent` 保留用于徽章/步骤圆点/主按钮;错误/成功/提示框换 token;ThemeToggle 加入顶栏。

- [ ] **Step 1: 全量替换 Lesson.tsx**

```tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import ChessBoard from '@/components/ChessBoard'
import Confetti from '@/components/Confetti'
import ThemeToggle from '@/components/ThemeToggle'
import { sounds } from '@/lib/sound'
import { api, ApiError, type SessionState } from '@/lib/api'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { ArrowLeft, ArrowRight, Lightbulb, RotateCcw, Star, Map as MapIcon, Swords } from 'lucide-react'

interface Props {
  levelId: string
  onExit: () => void
  onNext: (() => void) | null
}

const BOT_LABELS: Record<string, string> = {
  random: '随便走',
  greedy: '贪吃鬼',
  smart: '小聪明',
  master: '大师 Stockfish',
}

export default function Lesson({ levelId, onExit, onNext }: Props) {
  const { refresh } = useProgress()
  const { stockfishAvailable } = useCurriculum()

  const [st, setSt] = useState<SessionState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [wrongFlash, setWrongFlash] = useState(0)
  const [showHint, setShowHint] = useState(false)
  const [wrongChoices, setWrongChoices] = useState<number[]>([])
  const [pickedChoice, setPickedChoice] = useState<number | null>(null)
  // 对手回应延迟动画:后端已推进局面,前端先展示自己走完的局面,700ms 后再展示回应
  const [replyShown, setReplyShown] = useState(false)
  const replyTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const start = useCallback(async () => {
    try {
      const s = await api.createSession(levelId)
      setSt(s)
      setError(null)
      setReplyShown(false)
      setPickedChoice(null)
      setWrongChoices([])
      setShowHint(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载失败,请检查后端是否启动')
    }
  }, [levelId])

  useEffect(() => {
    void start()
    return () => {
      if (replyTimer.current) clearTimeout(replyTimer.current)
    }
  }, [start])

  const apply = (s: SessionState) => {
    if (s.step_index !== st?.step_index) {
      setShowHint(false)
      setWrongChoices([])
      setPickedChoice(null)
    }
    setSt(s)
    setReplyShown(false)
    if (replyTimer.current) clearTimeout(replyTimer.current)
    if (s.reply) {
      replyTimer.current = setTimeout(() => {
        setReplyShown(true)
        sounds.move()
      }, 700)
    }
    if (s.finished) void refresh().catch(() => undefined)
  }

  /** 会话过期(404)时重建会话从头开始本关,返回 true 表示已处理 */
  const recover404 = async (e: unknown): Promise<boolean> => {
    if (e instanceof ApiError && e.status === 404) {
      await start()
      return true
    }
    return false
  }

  const handleMove = async (uci: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionMove(st.session_id, uci)
      if (s.last_result === 'wrong') {
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else if (st.step.type === 'play') {
        sounds.move()
        if (s.play_status === 'won') sounds.checkmate()
        else if (s.play_status === 'lost' || s.play_status === 'draw') sounds.error()
      } else if (s.solved) {
        if (st.step.type === 'move') sounds.success()
        else sounds.checkmate() // mate / line 完成
      } else {
        sounds.move() // line 剧本中段
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const handleChoice = async (i: number) => {
    if (!st || busy || st.solved) return
    setBusy(true)
    try {
      const s = await api.sessionChoice(st.session_id, i)
      if (s.last_result === 'wrong') {
        setWrongChoices((w) => [...w, i])
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else {
        setPickedChoice(i)
        sounds.success()
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const goNext = async () => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionNext(st.session_id)
      if (s.finished) sounds.fanfare()
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const restart = async (bot?: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      apply(await api.restartPlay(st.session_id, bot))
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  // ---------------- 加载/错误 ----------------
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface px-4">
        <div className="bg-surface-container rounded-3xl elev-1 p-8 text-center max-w-sm">
          <p className="font-bold text-[var(--board-check)] mb-4">{error}</p>
          <button onClick={() => void start()}
            className="state-layer px-6 py-3 rounded-full bg-primary text-on-primary font-bold transition">
            重试
          </button>
        </div>
      </div>
    )
  }
  if (!st) {
    return <div className="min-h-screen bg-surface text-on-surface flex items-center justify-center font-display text-2xl">加载中……</div>
  }

  const step = st.step
  const accent = st.chapter_color
  const isPuzzle = step.type === 'mate' || step.type === 'move' || step.type === 'line'
  // 有对手回应且动画未播时,棋盘锁定并展示中间局面
  const awaitingReply = st.reply !== null && !replyShown
  const boardFen = awaitingReply ? st.fen : (st.reply?.fen ?? st.fen)
  const boardLastMove: [string, string] | null = awaitingReply ? st.last_move : (st.reply?.move ?? st.last_move)

  // ---------------- 通关结算 ----------------
  if (st.finished) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-10 bg-surface">
        <Confetti />
        <div className="w-full max-w-md bg-surface-container rounded-3xl elev-2 p-6 text-center">
          <div className="text-5xl mb-1">🏆</div>
          <h2 className="font-display text-2xl mb-1">闯关成功!</h2>
          <p className="text-on-surface-variant mb-3">{st.chapter_title} · {st.level_title}</p>
          <div className="inline-block px-4 py-1.5 rounded-full text-sm font-bold text-white mb-4" style={{ backgroundColor: accent }}>
            获得技能:{st.level_skill}
          </div>
          <div className="flex justify-center gap-2 mb-5">
            {[1, 2, 3].map((n) => (
              <Star key={n} size={44} strokeWidth={1.5}
                className={n <= st.stars ? 'fill-star text-star' : 'fill-outline-variant/30 text-outline-variant'} />
            ))}
          </div>
          <p className="text-sm text-on-surface-variant mb-6">
            {st.mistakes === 0 ? '完美通关,一次都没错!菲舍尔也会为你鼓掌。' : `错了 ${st.mistakes} 次,复习一下还能拿更多星星哦!`}
          </p>
          <div className="flex flex-col gap-3">
            {onNext && (
              <button onClick={onNext} className="state-layer w-full py-3.5 rounded-full bg-primary text-on-primary font-bold text-lg flex items-center justify-center gap-2 transition elev-1">
                下一关 <ArrowRight size={20} />
              </button>
            )}
            <div className="flex gap-3">
              <button onClick={() => void start()}
                className="flex-1 py-3 rounded-full border border-outline-variant text-primary font-bold flex items-center justify-center gap-2 hover:bg-primary/10 transition">
                <RotateCcw size={18} /> 再玩一次
              </button>
              <button onClick={onExit}
                className="flex-1 py-3 rounded-full border border-outline-variant text-primary font-bold flex items-center justify-center gap-2 hover:bg-primary/10 transition">
                <MapIcon size={18} /> 回地图
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* 顶栏 */}
      <div className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-4xl mx-auto px-4 py-2 flex items-center gap-3">
          <button onClick={onExit} className="p-2 rounded-full hover:bg-on-surface/10 transition" aria-label="返回">
            <ArrowLeft size={22} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-bold" style={{ color: accent }}>{st.chapter_badge} · {st.chapter_title}</div>
            <div className="font-display text-base leading-tight truncate">{st.level_title}</div>
          </div>
          <div className="flex items-center gap-1.5">
            {Array.from({ length: st.step_count }).map((_, i) => (
              <span key={i} className="w-2.5 h-2.5 rounded-full transition"
                style={{ backgroundColor: i < st.step_index ? accent : i === st.step_index ? 'var(--star)' : 'var(--outline-variant)' }} />
            ))}
          </div>
          <ThemeToggle />
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-4 pb-6">
        <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:items-center">
          {/* 棋盘 */}
          {boardFen && (
            <div key={`${st.step_index}-${wrongFlash}`} className="w-full max-w-[min(100%,400px)] md:max-w-[min(100%,56vh)] mx-auto">
              <ChessBoard
                fen={boardFen}
                interactive={((isPuzzle && !st.solved) || (step.type === 'play' && st.play_status === 'playing')) && !awaitingReply && !busy}
                onMove={(uci) => void handleMove(uci)}
                orientation={step.orientation || 'white'}
                highlight={step.type === 'teach' ? step.highlight : undefined}
                arrows={step.type === 'teach' ? step.arrows : undefined}
                lastMove={boardLastMove}
                shake={wrongFlash > 0}
                legalMoves={awaitingReply ? [] : st.legal_moves}
                checkSquare={awaitingReply ? null : st.check_square}
              />
              {step.sideLabel && (
                <div className="mt-3 text-center text-sm font-bold text-on-surface-variant">{step.sideLabel}</div>
              )}
              {step.type === 'play' && (
                <div className="mt-3 text-center text-sm font-bold text-on-surface-variant">
                  {awaitingReply ? '🤖 对方思考中……' : `你已走 ${st.my_moves} 步`}
                </div>
              )}
            </div>
          )}

          {/* 文字区 */}
          <div>
            {step.type === 'teach' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <h3 className="font-display text-xl mb-2" style={{ color: accent }}>{step.title}</h3>
                {(step.text ?? []).map((t, i) => (
                  <p key={i} className="text-[15px] leading-relaxed text-on-surface mb-2">{t}</p>
                ))}
                <button onClick={() => void goNext()} disabled={busy}
                  className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                  style={{ backgroundColor: accent }}>
                  我明白了 <ArrowRight size={18} />
                </button>
              </div>
            )}

            {isPuzzle && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  {step.type === 'mate' ? '⚡ 一步杀' : step.type === 'line' ? '🔥 连续杀' : '🎯 找到这步棋'}
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface">
                  {step.type === 'line' ? st.line_prompt : step.prompt}
                </p>

                {!st.solved && (
                  <div className="mt-4 flex items-center gap-3">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border border-outline-variant text-primary font-bold text-sm hover:bg-primary/10 transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    <span className="text-sm text-on-surface-variant">点棋子 → 点目标格</span>
                  </div>
                )}
                {showHint && !st.solved && step.hint && (
                  <div className="mt-3 p-3 rounded-2xl bg-hint-container text-on-hint-container text-[15px] leading-relaxed">
                    💡 {step.hint}
                  </div>
                )}

                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      🎉 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {wrongFlash > 0 && !st.solved && (
                  <p className="mt-3 text-[var(--board-check)] font-bold text-sm">这一步不对,再想想,你可以的!</p>
                )}
              </div>
            )}

            {step.type === 'choice' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  🤔 想一想
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface mb-4">{step.question}</p>
                <div className="flex flex-col gap-2.5">
                  {(step.options ?? []).map((opt, i) => {
                    const isRight = pickedChoice === i
                    const isWrong = wrongChoices.includes(i)
                    return (
                      <button key={i} onClick={() => void handleChoice(i)}
                        disabled={st.solved || busy}
                        className={`text-left px-5 py-3.5 rounded-2xl border font-bold text-[16px] transition ${
                          isRight
                            ? 'bg-success-container border-transparent text-on-success-container'
                            : isWrong
                              ? 'bg-error-container border-transparent text-on-error-container line-through opacity-70'
                              : 'bg-surface border-outline-variant hover:bg-primary/10 text-on-surface'
                        }`}>
                        {opt}
                      </button>
                    )
                  })}
                </div>
                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      ✅ {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
              </div>
            )}

            {step.type === 'play' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  <Swords size={12} className="inline -mt-0.5 mr-1" /> 实战对弈
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface">{step.prompt}</p>

                {/* 开局前可选对手档位 */}
                {st.play_status === 'playing' && st.my_moves === 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(['random', 'greedy', 'smart'] as const).map((b) => (
                      <button key={b} onClick={() => void restart(b)} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold transition ${
                          st.bot_style === b
                            ? 'bg-primary text-on-primary'
                            : 'border border-outline-variant text-on-surface-variant hover:bg-primary/10'
                        }`}>
                        {BOT_LABELS[b]}
                      </button>
                    ))}
                    {stockfishAvailable && (
                      <button onClick={() => void restart('master')} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold transition ${
                          st.bot_style === 'master'
                            ? 'bg-primary text-on-primary'
                            : 'border border-outline-variant text-on-surface-variant hover:bg-primary/10'
                        }`}>
                        {BOT_LABELS.master}
                      </button>
                    )}
                  </div>
                )}

                {st.play_status === 'playing' && (
                  <div className="mt-4">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border border-outline-variant text-primary font-bold text-sm hover:bg-primary/10 transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    {showHint && (
                      <div className="mt-3 p-3 rounded-2xl bg-hint-container text-on-hint-container text-[15px] leading-relaxed">
                        💡 {step.hint}
                      </div>
                    )}
                  </div>
                )}

                {st.play_status === 'won' && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      🏆 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {(st.play_status === 'lost' || st.play_status === 'draw') && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-error-container text-on-error-container font-bold leading-relaxed">
                      {st.end_text}
                    </div>
                    <button onClick={() => void restart()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      <RotateCcw size={18} /> 再来一盘
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证构建**

Run: `npm run build`
Expected: 构建成功,无 TS 错误。

- [ ] **Step 3: Commit**

```bash
git add src/pages/Lesson.tsx
git commit -m "feat: restyle lesson page to Material You"
```

### Task 7: 视觉验证(Playwright,浅色/深色 × 4 页)

**Files:**
- Create(临时,不进仓库): `/tmp/deb-shots/material-check.mjs`

- [ ] **Step 1: 起服务并准备 Playwright**

```bash
pkill -f uvicorn 2>/dev/null; rm -f backend/data/progress.db
(./start.sh > /tmp/md-check.log 2>&1 &)
sleep 4
curl -s localhost:8642/api/health   # Expected: {"ok":true}
# Playwright 复用 /tmp/deb-shots(若不存在则:mkdir -p /tmp/deb-shots && cd /tmp/deb-shots && npm init -y && npm install playwright --registry=https://registry.npmmirror.com && npx playwright install chromium)
```

- [ ] **Step 2: 截图脚本**

`/tmp/deb-shots/material-check.mjs`:

```js
import { chromium } from 'playwright'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })

const shots = []
async function snap(name) {
  await page.screenshot({ path: `/tmp/md-${name}.png` })
  shots.push(name)
}

// ---- 浅色 ----
await page.goto('http://localhost:8642')
await page.waitForTimeout(1500)
await snap('light-home')

await page.getByRole('button', { name: /闯关/ }).first().click()
await page.waitForTimeout(800)
await snap('light-map')

await page.getByRole('button', { name: /第 1 关/ }).click()
await page.waitForTimeout(800)
await snap('light-lesson-teach')

// 进到 move 步骤
await page.getByRole('button', { name: /我明白了/ }).click()
await page.waitForTimeout(800)
await snap('light-lesson-move')

// ---- 深色 ----
await page.goto('http://localhost:8642')
await page.evaluate(() => { localStorage.setItem('deb-chess-theme', 'dark') })
await page.reload()
await page.waitForTimeout(1500)
await snap('dark-home')

await page.getByRole('button', { name: /闯关/ }).first().click()
await page.waitForTimeout(800)
await snap('dark-map')

await page.getByRole('button', { name: /第 1 关/ }).click()
await page.waitForTimeout(800)
await snap('dark-lesson-teach')

await page.getByRole('button', { name: /我明白了/ }).click()
await page.waitForTimeout(800)
await snap('dark-lesson-move')

await browser.close()
console.log('shots:', shots.join(', '))
```

Run: `cd /tmp/deb-shots && node material-check.mjs`
Expected: `shots: light-home, light-map, light-lesson-teach, light-lesson-move, dark-home, dark-map, dark-lesson-teach, dark-lesson-move`

- [ ] **Step 3: 人工检查 8 张截图**

用 Read 工具逐张查看。检查点:
- 浅色:背景近白蓝(#F9F9FF)、卡片灰白、主按钮蓝色胶囊、无粗黑描边、棋盘蓝灰格;
- 深色:背景 #121318、卡片 #1E1F25、文字浅色可读、棋盘深色格对比清晰、棋子可见;
- 章节徽章/连线圆点仍有彩色;星星为琥珀色。

发现问题就改对应 token/组件,重跑脚本复查,直到 8 张全部合格。

- [ ] **Step 4: 停服务、跑全量测试、Commit**

```bash
pkill -f uvicorn
npm run build
cd backend && ../.venv/bin/pytest tests/ -q   # Expected: 37 passed, 2 skipped
cd .. && git add -A
git commit -m "feat: Material You redesign verified across pages and themes"
git push origin main
```
