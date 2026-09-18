import { useEffect, useMemo, useState } from 'react'
import { Chess, type Square } from 'chess.js'

const GLYPH: Record<string, string> = {
  wk: '♔', wq: '♕', wr: '♖', wb: '♗', wn: '♘', wp: '♙',
  bk: '♚', bq: '♛', br: '♜', bb: '♝', bn: '♞', bp: '♟',
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

interface Props {
  fen: string
  interactive?: boolean
  onMove?: (uci: string) => void
  orientation?: 'white' | 'black'
  highlight?: string[]
  arrows?: [string, string][]
  lastMove?: [string, string] | null
  shake?: boolean
  size?: number
}

function sqToXY(sq: string): { x: number; y: number } {
  const f = FILES.indexOf(sq[0])
  const r = 8 - parseInt(sq[1])
  return { x: f * 12.5 + 6.25, y: r * 12.5 + 6.25 }
}

export default function ChessBoard({
  fen,
  interactive = false,
  onMove,
  orientation = 'white',
  highlight = [],
  arrows = [],
  lastMove = null,
  shake = false,
}: Props) {
  const chess = useMemo(() => new Chess(fen), [fen])
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    setSelected(null)
  }, [fen])

  const board = chess.board() // [rank0=8 ... rank7=1][file a..h]
  const turn = chess.turn()

  const targets = useMemo(() => {
    if (!selected) return new Set<string>()
    return new Set(
      chess.moves({ square: selected as Square, verbose: true }).map((m) => m.to),
    )
  }, [chess, selected])

  // 被将军一方的王所在格
  const checkSquare = useMemo(() => {
    if (!chess.inCheck()) return null
    const kingGlyph = turn === 'w' ? 'k' : 'K'
    for (let r = 0; r < 8; r++)
      for (let f = 0; f < 8; f++) {
        const p = board[r][f]
        if (p && p.type === 'k' && p.color === turn) {
          void kingGlyph
          return p.square
        }
      }
    return null
  }, [chess, board, turn])

  const ranks = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0]
  const files = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0]

  const handleTap = (sq: string) => {
    if (!interactive) return
    const piece = chess.get(sq as Square)
    if (selected && targets.has(sq)) {
      onMove?.(selected + sq + 'q') // 升变默认皇后；chess.js 会忽略多余的 promotion
      setSelected(null)
      return
    }
    if (piece && piece.color === turn) {
      setSelected(selected === sq ? null : sq)
    } else {
      setSelected(null)
    }
  }

  return (
    <div
      className={`relative select-none ${shake ? 'animate-[boardshake_0.4s_ease-in-out]' : ''}`}
      style={{ containerType: 'inline-size' }}
    >
      <div className="grid w-full aspect-square rounded-2xl overflow-hidden shadow-[0_18px_40px_-18px_rgba(80,50,10,0.45)] ring-4 ring-[#7a5a33]"
        style={{ gridTemplateColumns: 'repeat(8, 1fr)', gridTemplateRows: 'repeat(8, 1fr)' }}>
        {ranks.map((r) =>
          files.map((f) => {
            const sq = `${FILES[f]}${8 - r}`
            const piece = board[r][f]
            const dark = (r + f) % 2 === 1
            const isSel = selected === sq
            const isTarget = targets.has(sq)
            const isLast = lastMove && (lastMove[0] === sq || lastMove[1] === sq)
            const isHi = highlight.includes(sq)
            const isCheck = checkSquare === sq
            return (
              <button
                key={sq}
                onClick={() => handleTap(sq)}
                className="relative flex items-center justify-center p-0 border-0 min-w-0 min-h-0 overflow-hidden"
                style={{
                  backgroundColor: isCheck
                    ? '#e05252'
                    : isSel
                      ? '#f7d354'
                      : isHi
                        ? '#b9d97a'
                        : isLast
                          ? dark
                            ? '#d4b26a'
                            : '#f0dcaa'
                          : dark
                            ? '#b07848'
                            : '#f3e3c3',
                }}
              >
                {isTarget && !piece && (
                  <span className="absolute w-[26%] h-[26%] rounded-full bg-[#2e7d52]/60" />
                )}
                {isTarget && piece && (
                  <span className="absolute inset-[6%] rounded-full ring-4 ring-[#e05252]/80" />
                )}
                {piece && (
                  <span
                    className="relative leading-none"
                    style={{
                      fontSize: 'clamp(20px, 6.4cqw, 52px)',
                      containerType: 'normal',
                      color: piece.color === 'w' ? '#ffffff' : '#2b2118',
                      textShadow:
                        piece.color === 'w'
                          ? '0 0 2px #2b2118, 0 2px 3px rgba(43,33,24,0.55)'
                          : '0 1px 2px rgba(255,255,255,0.25)',
                      fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2","DejaVu Sans",sans-serif',
                    }}
                  >
                    {GLYPH[piece.color + piece.type]}
                  </span>
                )}
                {f === (orientation === 'white' ? 0 : 7) && (
                  <span className={`absolute left-[4%] top-[2%] text-[10px] font-bold ${dark ? 'text-[#f3e3c3]' : 'text-[#b07848]'}`}>
                    {8 - r}
                  </span>
                )}
                {r === (orientation === 'white' ? 7 : 0) && (
                  <span className={`absolute right-[5%] bottom-[2%] text-[10px] font-bold ${dark ? 'text-[#f3e3c3]' : 'text-[#b07848]'}`}>
                    {FILES[f]}
                  </span>
                )}
              </button>
            )
          }),
        )}
      </div>

      {arrows.length > 0 && (
        <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="#2e7d52" />
            </marker>
          </defs>
          {arrows.map(([from, to], i) => {
            const a = sqToXY(from)
            const b = sqToXY(to)
            // 缩短箭头，避免压到棋子中心
            const dx = b.x - a.x
            const dy = b.y - a.y
            const len = Math.hypot(dx, dy) || 1
            const sx = a.x + (dx / len) * 4
            const sy = a.y + (dy / len) * 4
            const ex = b.x - (dx / len) * 5
            const ey = b.y - (dy / len) * 5
            return (
              <line key={i} x1={sx} y1={sy} x2={ex} y2={ey} stroke="#2e7d52" strokeWidth="2.6"
                strokeLinecap="round" markerEnd="url(#arr)" opacity="0.9" />
            )
          })}
        </svg>
      )}
    </div>
  )
}
