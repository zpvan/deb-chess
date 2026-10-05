# deb-chess 开源准备设计文档

日期:2026-10-06
状态:已批准

## 背景与目标

deb-chess 已推送到公开仓库 github.com/zpvan/deb-chess,但尚不具备正式开源条件。
**目标:完成开源所需的全部合规、文档、社区与 CI 配套工作,并消除版权风险。**

## 已确认的决策

| 决策点 | 结论 |
|---|---|
| 书页扫描件(29MB,在 git 历史中) | 彻底清除(filter-repo 重写全历史 + force push) |
| 许可证 | GPL-3.0(与依赖 python-chess、Stockfish 的 GPL-3.0 保持一致) |
| 配套范围 | 完整社区套件(LICENSE/双 README/CONTRIBUTING/CoC/模板/CI/截图) |
| README 语言 | 英文主(README.md)+ 中文副(README_ZH.md) |
| 清史方案 | git filter-repo(保留其余完整提交史) |

## 工作分解

### ① data/ 历史清除(核心风险操作)

- 本地把 `data/` 移到仓库外备份(`~/deb-chess-book-data-backup/`),从工作区删除;
- `brew install git-filter-repo`(若无),执行 `git filter-repo --path data --invert-paths --force`;
- 提交 `data/README.md` 占位说明:书页数据非必需、应用不引用、由使用者自备;
- `git push origin main --force-with-lease` 覆盖远端;
- **验收**:`git log --all --oneline -- data` 无输出;`git count-objects -vH` 仓库体积从 ~30MB 降到 <2MB;全新 clone 后 `./start.sh` 可跑。

### ② LICENSE 与版权处理

- 添加 `LICENSE`:GPL-3.0 全文;
- README 增加 License & Copyright 节:代码 GPL-3.0;声明依赖 python-chess/Stockfish 为 GPL-3.0;声明《Bobby Fischer Teaches Chess》书籍内容与书页图像版权归原出版方所有,本仓库不含、不分发书页,课程文字为原创中文编写、棋题为经典杀王模式;
- `package.json`:`name` 改为 `deb-chess`,加 `license: "GPL-3.0"`;
- `backend/pyproject.toml`:加 `license = {text = "GPL-3.0"}`。

### ③ 文档套件

| 文件 | 内容 |
|---|---|
| `README.md`(英文主) | 简介 + 截图、特性、架构简述、Quickstart(./start.sh / Docker / dev)、测试、数据说明、License 节 |
| `README_ZH.md`(中文副) | 同结构中文版,两文件顶部互链 |
| `CONTRIBUTING.md`(英文) | dev/测试流程、课程数据修改须过 validate_curriculum.py、commit 规范、PR 流程 |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 标准文本 |
| `.github/ISSUE_TEMPLATE/bug_report.md`、`feature_request.md` | GitHub 标准模板精简版 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 变更说明 + 测试勾选清单 |
| `docs/screenshots/` | 首页/地图/关卡 3 张截图(本地起服务无头浏览器截取;工具不可用则由用户后补,README 先留位) |

### ④ CI(GitHub Actions)

`.github/workflows/ci.yml`,push/PR 触发,两个 job:

1. **backend**:Python 3.12 + `apt install stockfish` → `pip install -e 'backend[dev]'` → `pytest tests/ -v`(含课程校验,stockfish 用例在 CI 中真正运行);
2. **frontend**:Node 20 → `npm ci` → `npm run build`。

README 顶部加 CI badge。

### ⑤ 杂项清理与发布

- 删除 `info.md`(脚手架遗留);
- `docs/superpowers/`(spec + plan)保留;
- `gh repo edit` 设置英文 description + topics(chess、education、fastapi、react、python、kids);
- 打 `v1.0.0` tag + GitHub Release;
- 最终验收:fresh clone → `./start.sh` → 页面可用 → CI 绿 → 历史无 data/。

## 执行顺序

① 必须先完成且一次做对(force push 不可逆);②③④⑤ 随后分批提交。

## 非目标(YAGNI)

- 不做多语言界面(应用本身只有中文 UI);
- 不发布 pip/npm 包(这是应用,不是库);
- 不改应用功能代码;
- 不做 CHANGELOG 自动化(v1.0.0 手写 release notes 即可)。
