# deb-chess Material You 改版设计文档

日期:2026-10-09
状态:已批准

## 背景与目标

当前 UI 是暖纸色"绘本风"(#fff8ea 背景、#1f1a17 粗描边、木质棋盘、章节多色)。
**目标:全面改为 Google Material 3(Material You)风格,浅色 + 深色双主题。**

## 已确认的决策

| 决策点 | 结论 |
|---|---|
| Material 版本 | Material 3 / Material You |
| 主题色 | 单主色:蓝 `#0B57D0` |
| 棋盘配色 | 随主题换 Material 配色(不留木色) |
| 字体 | Roboto(英文/数字)+ 系统中文字体 |
| 深色模式 | 浅色 + 深色切换(手动 + 系统偏好初值) |
| 组件 | 全面 Material You 化(胶囊按钮、elevation 卡片、去粗描边) |

## 视觉系统

### 设计 token(src/index.css 双套 CSS 变量)

| 角色 | 浅色 | 深色 |
|---|---|---|
| primary | `#0B57D0` | `#A8C7FA` |
| on-primary | `#FFFFFF` | `#062E6F` |
| primary-container | `#D3E3FD` | `#004A77` |
| surface | `#F9F9FF` | `#121318` |
| surface-container | `#EDEDF4`(卡片) | `#1E1F25` |
| on-surface | `#191C20` | `#E2E2E9` |
| outline-variant | `#C4C6D0` | `#44474E` |
| error-container | `#F9DEDC` | `#8C1D18` |
| 棋盘浅格 | `#E8EEF9` | `#3D4351` |
| 棋盘深格 | `#769CDF` | `#5A6B8C` |

- 章节色(`chapter.color`)只做小面积点缀:章节徽章、地图连线圆点、步骤圆点。
- `chapter.soft` 前端弃用,页面背景统一 surface。

### 组件改造

- **按钮**:胶囊形 rounded-full;主按钮 primary 填充、次按钮 outline 细边;hover state-layer(8% 透明遮罩);删除所有 border-2 粗描边。
- **卡片**:无描边,surface-container 底 + elevation 阴影;rounded-3xl 保留。
- **顶栏**:surface 底 + 1px outline-variant 分割线。
- **棋盘**:格子换新配色;选中态 primary-container;目标点 primary 60%;将军格 error 色。
- **字体**:index.html 引入 Roboto(latin, 400/500/700);中文用系统黑体;font-display 类保留但换字体栈。

### 深色模式

- `<html class="dark">` 切换,CSS 变量双套。
- 新增 `useDarkMode` hook:localStorage 记忆 + prefers-color-scheme 初值。
- 顶栏右侧 ThemeToggle(日/月图标),Home/Map/Lesson 三页共用。
- index.html 内联脚本防闪烁(渲染前设置 dark class)。

## 文件级改动

| 文件 | 改动 |
|---|---|
| `src/index.css` | 双套 CSS 变量、body 底色、font-display 字体栈 |
| `index.html` | 引入 Roboto、深色模式防闪烁脚本 |
| `tailwind.config.js` | CSS 变量映射为 Tailwind 色名 |
| `src/hooks/useDarkMode.ts` | 新建 |
| `src/components/ThemeToggle.tsx` | 新建 |
| `src/components/ChessBoard.tsx` | 硬编码色 → CSS 变量 |
| `src/pages/Home.tsx` | 全量换 token + ThemeToggle |
| `src/pages/Map.tsx` | 同上(章节徽章保留 chapter.color 小面积) |
| `src/pages/Lesson.tsx` | 同上(chapter.soft 弃用) |

后端零改动;curriculum.py 的 color/soft 字段保留不动。

## 难点与处理

- **章节多色 → 单主色落差**:徽章、连线圆点、步骤圆点保留章节色,地图页仍有色彩层次。
- **棋盘深色模式**:棋子 glyph 对比度需微调,以截图验证为准。
- **防闪烁**:inline 脚本在渲染前设置 dark class。

## 验证

- `npm run build` 通过;
- Playwright 截图:首页/地图/关卡(teach + play)× 浅色/深色 共 8 张,人工比对;
- 后端 37 项测试跑一遍确认无回归。

## 非目标(YAGNI)

- 不引入 MUI 等 Material 组件库;
- 不改交互逻辑、路由、API;
- 深色模式不做定时切换。
