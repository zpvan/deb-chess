// 静态版后端:Pyodide 在浏览器里跑 Python 后端核心。
// 与 api.ts 暴露完全相同的函数签名,由 backend.ts 按构建模式选择。
import { ApiError, type CurriculumResponse, type ProgressResponse, type SessionState } from './api'
import { PY_FILES } from './pybundle'

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js'
const PYODIDE_INDEX = 'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/'
const PROGRESS_KEY = 'deb-chess-progress'

declare global {
  interface Window {
    loadPyodide?: (opts: { indexURL: string }) => Promise<PyodideInstance>
  }
}

interface PyodideInstance {
  runPython(code: string): unknown
  runPythonAsync(code: string): Promise<unknown>
  FS: { writeFile(path: string, data: string): void; mkdirTree(path: string): void }
  loadPackage(names: string[]): Promise<void>
  pyimport(name: string): PyProxy
}

interface PyProxy {
  [key: string]: (...args: unknown[]) => unknown
}

let facadePromise: Promise<PyProxy> | null = null

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const el = document.createElement('script')
    el.src = src
    el.onload = () => resolve()
    el.onerror = () => reject(new Error(`failed to load ${src}`))
    document.head.appendChild(el)
  })
}

async function init(): Promise<PyProxy> {
  if (facadePromise) return facadePromise
  facadePromise = (async () => {
    await loadScript(PYODIDE_URL)
    const pyodide = await window.loadPyodide!({ indexURL: PYODIDE_INDEX })
    await pyodide.loadPackage(['micropip'])
    // micropip.install 是异步的,必须用 runPythonAsync 支持顶层 await
    await pyodide.runPythonAsync(`
import micropip
await micropip.install(['python-chess', 'pydantic'])
`)
    // 写入 Python 源码并保持包结构
    for (const [path, source] of Object.entries(PY_FILES)) {
      const dir = path.split('/').slice(0, -1).join('/')
      if (dir) pyodide.FS.mkdirTree(`/${dir}`)
      pyodide.FS.writeFile(`/${path}`, source)
    }
    await pyodide.runPython('import sys\nsys.path.insert(0, "/")')
    const facade = pyodide.pyimport('app.static_facade')
    // 恢复持久化进度
    try {
      const saved = localStorage.getItem(PROGRESS_KEY)
      if (saved) facade.set_progress_json(saved)
    } catch { /* ignore */ }
    return facade
  })()
  facadePromise.catch((e) => console.error('[pyodide-api] init failed:', e))
  return facadePromise
}

type Envelope<T> = { ok: true; data: T } | { ok: false; status: number; detail: unknown }

function currentLang(): 'en' | 'zh' {
  try {
    if (localStorage.getItem('deb-chess-lang') === 'zh') return 'zh'
  } catch { /* ignore */ }
  return 'en'
}

async function call<T>(fn: string, ...args: unknown[]): Promise<T> {
  const facade = await init()
  const raw = (facade[fn] as (...a: unknown[]) => string)(...args)
  const env = JSON.parse(raw) as Envelope<T>
  if (!env.ok) {
    const lang = currentLang()
    let msg = `Request failed (${env.status})`
    if (typeof env.detail === 'string') msg = env.detail
    else if (env.detail && typeof env.detail === 'object') {
      const d = env.detail as Record<string, string>
      msg = d[lang] ?? d.en ?? msg
    }
    throw new ApiError(msg, env.status)
  }
  // 通关后回写进度到 localStorage
  if (fn === 'session_move' || fn === 'session_next' || fn === 'session_choice') {
    const data = env.data as { finished?: boolean }
    if (data.finished) {
      try {
        localStorage.setItem(PROGRESS_KEY, (facade.get_progress_json as () => string)())
      } catch { /* ignore */ }
    }
  }
  return env.data
}

export const pyodideApi = {
  getCurriculum: (lang: string) => call<CurriculumResponse>('get_curriculum', lang),
  getProgress: (lang: string) => call<ProgressResponse>('get_progress', lang),
  createSession: (levelId: string, lang: string) => call<SessionState>('create_session', levelId, lang),
  getSession: (id: string) => call<SessionState>('get_session', id),
  sessionMove: (id: string, move: string) => call<SessionState>('session_move', id, move),
  sessionChoice: (id: string, index: number) => call<SessionState>('session_choice', id, index),
  sessionNext: (id: string) => call<SessionState>('session_next', id),
  restartPlay: (id: string, bot?: string) => call<SessionState>('restart_play', id, bot ?? null),
}
