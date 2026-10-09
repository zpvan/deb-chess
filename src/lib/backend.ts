// 统一后端出口:static 构建走 Pyodide(浏览器内 Python),否则走 HTTP API。
import { api } from './api'
import { pyodideApi } from './pyodide-api'

export const backend: typeof api =
  import.meta.env.MODE === 'static' ? pyodideApi : api
