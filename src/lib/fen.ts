// 轻量 FEN 解析:只提取渲染所需的棋盘数组与行棋方。
// 返回结构与旧版 chess.js board() 兼容:[rank8..rank1][file a..h],格子含 square 字段。
export interface BoardPiece {
  type: string // 'p' | 'n' | 'b' | 'r' | 'q' | 'k'
  color: 'w' | 'b'
  square: string
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

export function parseFen(fen: string): { board: (BoardPiece | null)[][]; turn: 'w' | 'b' } {
  const [placement, turn] = fen.split(' ')
  const board = placement.split('/').map((row, r) => {
    const out: (BoardPiece | null)[] = []
    let f = 0
    for (const ch of row) {
      if (/\d/.test(ch)) {
        for (let i = 0; i < parseInt(ch, 10); i++) {
          out.push(null)
          f++
        }
      } else {
        out.push({
          type: ch.toLowerCase(),
          color: ch === ch.toUpperCase() ? 'w' : 'b',
          square: `${FILES[f]}${8 - r}`,
        })
        f++
      }
    }
    return out
  })
  return { board, turn: turn === 'b' ? 'b' : 'w' }
}
