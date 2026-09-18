import { Chess, type Move } from 'chess.js'

const VAL: Record<string, number> = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 }

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

/** 电脑对手：random 随便走 / greedy 贪吃+爱将军 / smart 还会避免送子 */
export function pickBotMove(game: Chess, style: 'random' | 'greedy' | 'smart'): Move | null {
  const moves = game.moves({ verbose: true })
  if (moves.length === 0) return null
  if (style === 'random') return pick(moves)

  const scored = moves.map((m) => {
    let s = Math.random() * 2
    const g = new Chess(game.fen())
    g.move(m)
    if (g.isCheckmate()) s += 10000
    if (m.captured) s += VAL[m.captured] * 20
    if (g.inCheck()) s += 8
    if (style === 'smart') {
      // 走完若会被对方白白吃掉，扣分（粗略：对方能吃到这格且该格无人保护）
      const enemy = g.turn()
      const attackers = g.attackers(m.to, enemy)
      const defenders = g.attackers(m.to, enemy === 'w' ? 'b' : 'w')
      if (attackers.length > defenders.length && VAL[m.piece] > 1) s -= VAL[m.piece] * 15
    }
    return { m, s }
  })
  scored.sort((a, b) => b.s - a.s)
  // 在前 30% 里随机，保留一点变化
  const topN = Math.max(1, Math.floor(scored.length * 0.3))
  return pick(scored.slice(0, topN)).m
}

/** 判断黑方是否还有皇后（用于“吃掉皇后也算赢”） */
export function blackQueenGone(game: Chess): boolean {
  return !game.board().flat().some((p) => p && p.type === 'q' && p.color === 'b')
}
