# deb-chess 全站双语设计文档

日期:2026-10-09
状态:已批准

## 背景与目标

当前 UI 与课程内容全部为中文。**目标:网站内容默认英文,右上角提供语言切换(EN | 中),全部内容(UI 框架 + 课程正文)双语化。**

## 已确认的决策

| 决策点 | 结论 |
|---|---|
| 翻译范围 | 全部内容双语(UI + 82 步骤课程正文 + 段位名 + 错误消息) |
| 首次默认语言 | 永远英文(不跟随浏览器) |
| 语言切换 | 顶栏右侧「EN \| 中」分段开关,置于 ThemeToggle 左侧 |
| 前端 i18n 方案 | 自研轻量 context(不引入 react-i18next) |

## 设计

### ① 课程内容双语(后端)

- **数据层**:`backend/data/curriculum.py` 所有用户可见文本字段改为 `{"zh": "...", "en": "..."}`:
  章节/关卡的 `title/goal/skill/intro/badge`,步骤的 `title/text/prompt/prompts/hint/successText/failText/drawText/sideLabel/question/options/explain`。
  FEN、`accepted`、`script`、bot 档位等非文本字段不变,校验器不受影响。
- **模型层**:`models.py` 增加 `Loc = dict[str, str]`;`public_step()` 按语言扁平化。
- **API 层**:
  - `GET /api/curriculum?lang=en|zh`(默认 en)
  - `POST /api/sessions` 请求体加 `lang`,会话记住语言,所有响应文案按此语言(success/end 文案)
  - `/api/progress?lang=` 的 `rank_name` 双语(Pawn Rookie/小士兵 等六档)
  - 422 错误改为「错误码 + 双语文案」,前端按当前语言展示

### ② UI 框架双语(前端)

- 新建 `src/i18n/`:LanguageProvider(context)持有 `lang`(默认 'en',localStorage 记忆)+ `t(key)`;`en.ts`/`zh.ts` 词典(约 90 条)。
- Home/Map/Lesson/App 硬编码中文全部替换为 `t('...')`;bot 档位名入词典。

### ③ 语言切换器

- `LangToggle` 组件:分段开关,当前语言高亮(primary-container),顶栏 ThemeToggle 左侧,三页共用。
- 切换时:前端语言立即生效;CurriculumProvider 依赖 lang 重新拉取 `/api/curriculum?lang=`;进行中的会话重建从头开始本关(与 404 恢复逻辑一致)。

### ④ 验证

- 后端测试:双语结构校验、lang 参数、rank 双语、错误码;37 项原有测试同步更新。
- 前端:构建 + Playwright 截图(英/中 × 首页/地图/关卡)人工比对。
- 校验器跑全量课程数据。

## 非目标(YAGNI)

- 不做更多语言、不做 RTL;
- README 不变(已是双语);
- 不引入第三方 i18n 库。
