import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { ChapterData, LevelData } from '@/lib/api'
import { backend as api } from '@/lib/backend'
import { useLang } from '@/i18n'

export interface FlatLevel {
  chapter: ChapterData
  level: LevelData
  index: number
}

interface CurriculumCtx {
  chapters: ChapterData[]
  flatLevels: FlatLevel[]
  totalLevels: number
  totalPuzzles: number
  stockfishAvailable: boolean
  loading: boolean
  /** 上次加载是否失败(网络/后端不可达) */
  error: boolean
  /** 失败后重试 */
  retry: () => void
}

const Ctx = createContext<CurriculumCtx | null>(null)

export function CurriculumProvider({ children }: { children: ReactNode }) {
  const { lang } = useLang()
  const [data, setData] = useState<Omit<CurriculumCtx, 'retry'>>({
    chapters: [],
    flatLevels: [],
    totalLevels: 0,
    totalPuzzles: 0,
    stockfishAvailable: false,
    loading: true,
    error: false,
  })
  // 自增 nonce 触发重新加载(retry 与语言切换共用同一条 effect)
  const [nonce, setNonce] = useState(0)
  const retry = useCallback(() => setNonce((n) => n + 1), [])

  useEffect(() => {
    setData((d) => ({ ...d, loading: true, error: false }))
    api
      .getCurriculum(lang)
      .then((res) => {
        const flatLevels: FlatLevel[] = res.chapters.flatMap((chapter) =>
          chapter.levels.map((level) => ({ chapter, level, index: -1 })),
        )
        flatLevels.forEach((f, i) => (f.index = i))
        setData({
          chapters: res.chapters,
          flatLevels,
          totalLevels: res.total_levels,
          totalPuzzles: res.total_puzzles,
          stockfishAvailable: res.stockfish_available,
          loading: false,
          error: false,
        })
      })
      .catch(() =>
        setData((d) => ({ ...d, chapters: [], flatLevels: [], loading: false, error: true })),
      )
  }, [lang, nonce])

  const value = useMemo<CurriculumCtx>(() => ({ ...data, retry }), [data, retry])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useCurriculum(): CurriculumCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useCurriculum must be used within CurriculumProvider')
  return ctx
}
