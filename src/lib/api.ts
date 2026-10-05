const BASE = '/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let msg = `请求失败(${res.status})`
    try {
      const d = await res.json()
      if (typeof d.detail === 'string') msg = d.detail
    } catch { /* ignore */ }
    throw new ApiError(msg, res.status)
  }
  return res.json()
}

export interface PublicStep {
  type: 'teach' | 'mate' | 'move' | 'line' | 'choice' | 'play'
  fen?: string
  title?: string
  text?: string[]
  highlight?: string[]
  arrows?: [string, string][]
  prompt?: string
  prompts?: string[]
  hint?: string
  sideLabel?: string
  question?: string
  options?: string[]
  bot?: 'random' | 'greedy' | 'smart'
  win?: 'mate' | 'mateOrQueen'
  orientation?: 'white' | 'black'
}

export interface SessionState {
  session_id: string
  level_id: string
  level_title: string
  level_skill: string
  chapter_title: string
  chapter_badge: string
  chapter_color: string
  chapter_soft: string
  step_index: number
  step_count: number
  step: PublicStep
  fen: string | null
  legal_moves: string[]
  check_square: string | null
  last_move: [string, string] | null
  solved: boolean
  fast_mate: boolean
  line_prompt: string | null
  play_status: 'playing' | 'won' | 'lost' | 'draw' | null
  my_moves: number
  bot_style: string | null
  mistakes: number
  finished: boolean
  stars: number
  success_text: string | null
  end_text: string | null
  last_result: 'correct' | 'wrong' | null
  reply: { move: [string, string]; fen: string } | null
}

export interface LevelData {
  id: string
  title: string
  goal: string
  skill: string
  steps: PublicStep[]
}

export interface ChapterData {
  id: string
  badge: string
  title: string
  intro: string
  color: string
  soft: string
  levels: LevelData[]
}

export interface CurriculumResponse {
  chapters: ChapterData[]
  total_levels: number
  total_puzzles: number
  stockfish_available: boolean
  bot_styles: string[]
}

export interface ProgressResponse {
  levels: Record<string, number>
  xp: number
  total_stars: number
  rank_name: string
  rank_icon: string
}

export const api = {
  getCurriculum: () => req<CurriculumResponse>('/curriculum'),
  getProgress: () => req<ProgressResponse>('/progress'),
  createSession: (levelId: string) =>
    req<SessionState>('/sessions', { method: 'POST', body: JSON.stringify({ level_id: levelId }) }),
  getSession: (id: string) => req<SessionState>(`/sessions/${id}`),
  sessionMove: (id: string, move: string) =>
    req<SessionState>(`/sessions/${id}/move`, { method: 'POST', body: JSON.stringify({ move }) }),
  sessionChoice: (id: string, index: number) =>
    req<SessionState>(`/sessions/${id}/choice`, { method: 'POST', body: JSON.stringify({ index }) }),
  sessionNext: (id: string) =>
    req<SessionState>(`/sessions/${id}/next`, { method: 'POST', body: '{}' }),
  restartPlay: (id: string, bot?: string) =>
    req<SessionState>(`/sessions/${id}/restart-play`, {
      method: 'POST',
      body: JSON.stringify({ bot: bot ?? null }),
    }),
}
