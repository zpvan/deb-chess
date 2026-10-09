import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
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
}

const Ctx = createContext<CurriculumCtx | null>(null)

const EMPTY: CurriculumCtx = {
  chapters: [],
  flatLevels: [],
  totalLevels: 0,
  totalPuzzles: 0,
  stockfishAvailable: false,
  loading: true,
}

export function CurriculumProvider({ children }: { children: ReactNode }) {
  const { lang } = useLang()
  const [data, setData] = useState<CurriculumCtx>(EMPTY)

  useEffect(() => {
    setData((d) => ({ ...d, loading: true }))
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
        })
      })
      .catch(() => setData({ ...EMPTY, loading: false }))
  }, [lang])

  return <Ctx.Provider value={data}>{children}</Ctx.Provider>
}

export function useCurriculum(): CurriculumCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useCurriculum must be used within CurriculumProvider')
  return ctx
}
