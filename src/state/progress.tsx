import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { totalLevels } from '@/data/curriculum'

const STORAGE_KEY = 'fischer-chess-progress-v1'

export interface ProgressData {
  levels: Record<string, { stars: number }>
  xp: number
}

interface ProgressCtx {
  data: ProgressData
  xp: number
  completeLevel: (levelId: string, stars: number) => void
  isUnlocked: (levelId: string) => boolean
  starsOf: (levelId: string) => number
  totalStars: number
  rank: { name: string; icon: string }
}

const empty: ProgressData = { levels: {}, xp: 0 }

const Ctx = createContext<ProgressCtx | null>(null)

const RANKS: { min: number; name: string; icon: string }[] = [
  { min: 0, name: '小士兵', icon: '♟' },
  { min: 100, name: '小骑士', icon: '♞' },
  { min: 250, name: '小主教', icon: '♝' },
  { min: 450, name: '小城堡', icon: '♜' },
  { min: 700, name: '小皇后', icon: '♛' },
  { min: 1000, name: '小棋王', icon: '♚' },
]

function load(): ProgressData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return { ...empty, ...JSON.parse(raw) }
  } catch {
    /* ignore */
  }
  return empty
}

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<ProgressData>(load)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch {
      /* ignore */
    }
  }, [data])

  const value = useMemo<ProgressCtx>(() => {
    const starsOf = (levelId: string) => data.levels[levelId]?.stars ?? 0
    // 全部关卡不上锁：孩子可以自由选择任何一关，按自己的节奏学习
    const isUnlocked = (_levelId: string) => true
    const completeLevel = (levelId: string, stars: number) => {
      setData((d) => {
        const prev = d.levels[levelId]?.stars ?? 0
        const best = Math.max(prev, stars)
        const gained = prev === 0 ? 60 + stars * 20 : Math.max(0, (best - prev) * 20)
        return { levels: { ...d.levels, [levelId]: { stars: best } }, xp: d.xp + gained }
      })
    }
    const totalStars = Object.values(data.levels).reduce((n, l) => n + l.stars, 0)
    const rank = [...RANKS].reverse().find((r) => data.xp >= r.min) ?? RANKS[0]
    return { data, xp: data.xp, completeLevel, isUnlocked, starsOf, totalStars, rank }
  }, [data])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useProgress(): ProgressCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useProgress must be used within ProgressProvider')
  return ctx
}

export { totalLevels }
