import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from '@/lib/api'

interface ProgressCtx {
  xp: number
  totalStars: number
  rank: { name: string; icon: string }
  starsOf: (levelId: string) => number
  refresh: () => Promise<void>
  // 兼容 shim:旧 Lesson.tsx 仍调用 completeLevel,Task 13 重写后于 Task 14 删除
  completeLevel: (levelId: string, stars: number) => void
}

const Ctx = createContext<ProgressCtx | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [levels, setLevels] = useState<Record<string, number>>({})
  const [xp, setXp] = useState(0)
  const [totalStars, setTotalStars] = useState(0)
  const [rank, setRank] = useState({ name: '小士兵', icon: '♟' })

  const refresh = useCallback(async () => {
    const p = await api.getProgress()
    setLevels(p.levels)
    setXp(p.xp)
    setTotalStars(p.total_stars)
    setRank({ name: p.rank_name, icon: p.rank_icon })
  }, [])

  useEffect(() => {
    refresh().catch(() => undefined)
  }, [refresh])

  const value = useMemo<ProgressCtx>(
    () => ({
      xp,
      totalStars,
      rank,
      refresh,
      starsOf: (id) => levels[id] ?? 0,
      // 兼容 shim:进度由后端在通关时自动记录,这里只需刷新;Task 14 删除
      completeLevel: () => void refresh().catch(() => undefined),
    }),
    [xp, totalStars, rank, levels, refresh],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useProgress(): ProgressCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useProgress must be used within ProgressProvider')
  return ctx
}
