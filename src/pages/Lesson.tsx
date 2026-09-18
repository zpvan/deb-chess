import { useEffect, useRef, useState } from 'react'
import { Chess, type Square } from 'chess.js'
import ChessBoard from '@/components/ChessBoard'
import Confetti from '@/components/Confetti'
import { sounds } from '@/lib/sound'
import { pickBotMove, blackQueenGone } from '@/lib/bot'
import { useProgress } from '@/state/progress'
import type { FlatLevel, Step, ChoiceStep, PlayStep } from '@/data/curriculum'
import { ArrowLeft, ArrowRight, Lightbulb, RotateCcw, Star, Map, Swords } from 'lucide-react'

interface Props {
  flat: FlatLevel
  onExit: () => void
  onNext: (() => void) | null
}

type PlayStatus = 'playing' | 'won' | 'lost' | 'draw'

export default function Lesson({ flat, onExit, onNext }: Props) {
  const { level, chapter } = flat
  const { completeLevel } = useProgress()

  const [idx, setIdx] = useState(0)
  const [mistakes, setMistakes] = useState(0)
  const [fen, setFen] = useState<string | null>(null)
  const [linePos, setLinePos] = useState(0) // line 题进行到的 script 下标
  const [lastMove, setLastMove] = useState<[string, string] | null>(null)
  const [solved, setSolved] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [wrongFlash, setWrongFlash] = useState(0)
  const [choicePick, setChoicePick] = useState<number | null>(null)
  const [wrongChoices, setWrongChoices] = useState<number[]>([])
  const [finished, setFinished] = useState(false)
  const [stars, setStars] = useState(0)

  // play 模式状态
  const [playStatus, setPlayStatus] = useState<PlayStatus>('playing')
  const [botThinking, setBotThinking] = useState(false)
  const [myMoves, setMyMoves] = useState(0)
  const [fastMate, setFastMate] = useState(false) // 比棋谱更快将死
  const botTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const step: Step = level.steps[idx]
  const boardFen = fen ?? ('fen' in step ? step.fen : undefined)
  const accent = chapter.color

  useEffect(() => {
    return () => {
      if (botTimer.current) clearTimeout(botTimer.current)
    }
  }, [])

  const resetStepState = () => {
    setFen(null)
    setLinePos(0)
    setLastMove(null)
    setSolved(false)
    setShowHint(false)
    setChoicePick(null)
    setWrongChoices([])
    setPlayStatus('playing')
    setBotThinking(false)
    setMyMoves(0)
    setFastMate(false)
  }

  const goNext = () => {
    if (idx + 1 >= level.steps.length) {
      const s = mistakes === 0 ? 3 : mistakes <= 2 ? 2 : 1
      setStars(s)
      completeLevel(level.id, s)
      setFinished(true)
      sounds.fanfare()
    } else {
      setIdx(idx + 1)
      resetStepState()
    }
  }

  const wrong = () => {
    setMistakes((m) => m + 1)
    setWrongFlash((n) => n + 1)
    sounds.error()
  }

  const applyMove = (game: Chess, from: string, to: string) => {
    game.move({ from: from as Square, to: to as Square, promotion: 'q' })
    setFen(game.fen())
    setLastMove([from, to])
  }

  // ---------------- 练习题走子 ----------------
  const handleMove = (uci: string) => {
    if (solved) return
    const game = new Chess(boardFen)
    const from = uci.slice(0, 2)
    const to = uci.slice(2, 4)
    const legal = game.moves({ verbose: true }).some((m) => m.from === from && m.to === to)
    if (!legal) return

    if (step.type === 'play') return handlePlayMove(game, from, to, step)

    if (step.type === 'mate') {
      game.move({ from, to, promotion: 'q' })
      if (game.isCheckmate()) {
        sounds.checkmate()
        setSolved(true)
        setLastMove([from, to])
        setFen(game.fen())
      } else wrong()
      return
    }

    if (step.type === 'move') {
      const bare = from + to
      if (step.accepted.some((a) => a === bare || a === uci)) {
        sounds.success()
        setSolved(true)
        applyMove(game, from, to)
      } else wrong()
      return
    }

    if (step.type === 'line') {
      const script = step.script
      const bare = from + to
      const isLast = linePos === script.length - 1
      game.move({ from, to, promotion: 'q' })
      const mated = game.isCheckmate()
      const hit = script[linePos] === bare || script[linePos] === uci
      // 任何时候直接将军死都算成功（更快杀法同样算挑战成功），否则须按棋谱走
      if (mated || hit) {
        setFen(game.fen())
        setLastMove([from, to])
        if (mated || isLast || linePos + 1 >= script.length) {
          sounds.checkmate()
          if (mated && !isLast) setFastMate(true)
          setSolved(true)
        } else {
          sounds.move()
          const nextPos = linePos + 1
          setLinePos(nextPos)
          // 自动走出对手的应对
          setTimeout(() => {
            const g2 = new Chess(game.fen())
            const r = script[nextPos]
            g2.move({ from: r.slice(0, 2), to: r.slice(2, 4), promotion: 'q' })
            setFen(g2.fen())
            setLastMove([r.slice(0, 2), r.slice(2, 4)])
            setLinePos(nextPos + 1)
            sounds.move()
          }, 700)
        }
      } else wrong()
    }
  }

  // ---------------- 实战对弈 ----------------
  const handlePlayMove = (game: Chess, from: string, to: string, s: PlayStep) => {
    if (playStatus !== 'playing' || botThinking) return
    game.move({ from, to, promotion: 'q' })
    setFen(game.fen())
    setLastMove([from, to])
    setMyMoves((n) => n + 1)
    sounds.move()

    if (game.isCheckmate()) {
      setPlayStatus('won')
      sounds.checkmate()
      return
    }
    if (s.win === 'mateOrQueen' && blackQueenGone(game)) {
      setPlayStatus('won')
      sounds.checkmate()
      return
    }
    if (game.isStalemate() || game.isDraw()) {
      setPlayStatus('draw')
      return
    }

    // 电脑应对
    setBotThinking(true)
    botTimer.current = setTimeout(() => {
      const g2 = new Chess(game.fen())
      const bm = pickBotMove(g2, s.bot)
      if (bm) {
        g2.move(bm)
        setFen(g2.fen())
        setLastMove([bm.from, bm.to])
        sounds.move()
        if (g2.isCheckmate()) setPlayStatus('lost')
        else if (g2.isStalemate() || g2.isDraw()) setPlayStatus('draw')
      }
      setBotThinking(false)
    }, 600)
  }

  const restartPlay = () => {
    if (botTimer.current) clearTimeout(botTimer.current)
    setFen(null)
    setLastMove(null)
    setPlayStatus('playing')
    setBotThinking(false)
    setMyMoves(0)
    setMistakes((m) => m + 1) // 重开算一次小失误，影响星级
  }

  // ---------------- 通关结算 ----------------
  if (finished) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-10" style={{ backgroundColor: chapter.soft }}>
        <Confetti />
        <div className="w-full max-w-md bg-[#fffdf6] rounded-3xl shadow-xl p-8 text-center border-4 border-[#1f1a17]">
          <div className="text-6xl mb-2">🏆</div>
          <h2 className="font-display text-3xl mb-1">闯关成功！</h2>
          <p className="text-[#6b5d4f] mb-3">{chapter.title} · {level.title}</p>
          <div className="inline-block px-4 py-1.5 rounded-full text-sm font-bold text-white mb-4" style={{ backgroundColor: accent }}>
            获得技能：{level.skill}
          </div>
          <div className="flex justify-center gap-2 mb-5">
            {[1, 2, 3].map((n) => (
              <Star key={n} size={44} strokeWidth={1.5}
                className={n <= stars ? 'fill-[#f7c948] text-[#b8860b]' : 'fill-[#ece5d8] text-[#cfc4b0]'} />
            ))}
          </div>
          <p className="text-sm text-[#6b5d4f] mb-6">
            {mistakes === 0 ? '完美通关，一次都没错！菲舍尔也会为你鼓掌。' : `错了 ${mistakes} 次，复习一下还能拿更多星星哦！`}
          </p>
          <div className="flex flex-col gap-3">
            {onNext && (
              <button onClick={onNext} className="w-full py-3.5 rounded-full bg-[#1f1a17] text-white font-bold text-lg flex items-center justify-center gap-2 hover:bg-[#3a322c] transition">
                下一关 <ArrowRight size={20} />
              </button>
            )}
            <div className="flex gap-3">
              <button onClick={() => { setIdx(0); setMistakes(0); resetStepState(); setFinished(false) }}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <RotateCcw size={18} /> 再玩一次
              </button>
              <button onClick={onExit}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <Map size={18} /> 回地图
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const isPuzzle = step.type === 'mate' || step.type === 'move' || step.type === 'line'
  const linePromptIdx = Math.floor(linePos / 2)

  return (
    <div className="min-h-screen" style={{ backgroundColor: chapter.soft }}>
      {/* 顶栏 */}
      <div className="sticky top-0 z-20 bg-[#fffdf6]/95 backdrop-blur border-b-2 border-[#1f1a17]/10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onExit} className="p-2 rounded-full hover:bg-[#f3ead9] transition" aria-label="返回">
            <ArrowLeft size={22} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-bold" style={{ color: accent }}>{chapter.badge} · {chapter.title}</div>
            <div className="font-display text-lg leading-tight truncate">{level.title}</div>
          </div>
          <div className="flex items-center gap-1.5">
            {level.steps.map((_, i) => (
              <span key={i} className="w-2.5 h-2.5 rounded-full transition"
                style={{ backgroundColor: i < idx ? accent : i === idx ? '#f7c948' : '#ddd2bd' }} />
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 pb-24">
        <div className={`grid gap-6 ${step.type === 'choice' || step.type === 'teach' ? 'md:grid-cols-[1fr_1fr] md:items-center' : ''}`}>
          {/* 棋盘 */}
          {boardFen && (
            <div key={`${idx}-${wrongFlash}`} className="w-full max-w-[520px] mx-auto">
              <ChessBoard
                fen={boardFen}
                interactive={(isPuzzle && !solved) || (step.type === 'play' && playStatus === 'playing' && !botThinking)}
                onMove={handleMove}
                orientation={('orientation' in step && step.orientation) || 'white'}
                highlight={step.type === 'teach' ? step.highlight : undefined}
                arrows={step.type === 'teach' ? step.arrows : undefined}
                lastMove={lastMove}
                shake={wrongFlash > 0}
              />
              {'sideLabel' in step && step.sideLabel && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">{step.sideLabel}</div>
              )}
              {step.type === 'play' && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">
                  {botThinking ? '🤖 对方思考中……' : `你已走 ${myMoves} 步`}
                </div>
              )}
            </div>
          )}

          {/* 文字区 */}
          <div>
            {step.type === 'teach' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <h3 className="font-display text-2xl mb-3" style={{ color: accent }}>{step.title}</h3>
                {step.text.map((t, i) => (
                  <p key={i} className="text-[17px] leading-relaxed text-[#3a322c] mb-2">{t}</p>
                ))}
                <button onClick={goNext}
                  className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition"
                  style={{ backgroundColor: accent }}>
                  我明白了 <ArrowRight size={18} />
                </button>
              </div>
            )}

            {isPuzzle && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  {step.type === 'mate' ? '⚡ 一步杀' : step.type === 'line' ? '🔥 连续杀' : '🎯 找到这步棋'}
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c]">
                  {step.type === 'line' ? step.prompts[Math.min(linePromptIdx, step.prompts.length - 1)] : step.prompt}
                </p>

                {!solved && (
                  <div className="mt-4 flex items-center gap-3">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-[#b8860b] text-[#b8860b] font-bold text-sm hover:bg-[#fdf3d7] transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    <span className="text-sm text-[#a3927c]">点棋子 → 点目标格</span>
                  </div>
                )}
                {showHint && !solved && step.hint && (
                  <div className="mt-3 p-3 rounded-2xl bg-[#fdf3d7] text-[#7a5c10] text-[15px] leading-relaxed">
                    💡 {step.hint}
                  </div>
                )}

                {solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🎉 {fastMate ? '更快将死！比参考答案还少用了步数，太厉害了！' : step.successText}
                    </div>
                    <button onClick={goNext}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {wrongFlash > 0 && !solved && (
                  <p className="mt-3 text-[#c0392b] font-bold text-sm">这一步不对，再想想，你可以的！</p>
                )}
              </div>
            )}

            {step.type === 'choice' && (
              <ChoicePanel step={step} accent={accent} choicePick={choicePick} wrongChoices={wrongChoices}
                onPick={(i) => {
                  if (choicePick === step.answer) return
                  if (i === step.answer) {
                    sounds.success()
                    setChoicePick(i)
                  } else {
                    setWrongChoices((w) => [...w, i])
                    wrong()
                  }
                }}
                onNext={goNext} />
            )}

            {step.type === 'play' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  <Swords size={12} className="inline -mt-0.5 mr-1" /> 实战对弈
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c]">{step.prompt}</p>

                {playStatus === 'playing' && (
                  <div className="mt-4">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-[#b8860b] text-[#b8860b] font-bold text-sm hover:bg-[#fdf3d7] transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    {showHint && (
                      <div className="mt-3 p-3 rounded-2xl bg-[#fdf3d7] text-[#7a5c10] text-[15px] leading-relaxed">
                        💡 {step.hint}
                      </div>
                    )}
                  </div>
                )}

                {playStatus === 'won' && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🏆 {step.successText}（用了 {myMoves} 步）
                    </div>
                    <button onClick={goNext}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {(playStatus === 'lost' || playStatus === 'draw') && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#fdecea] border-2 border-[#e05252]/30 text-[#8c2f23] font-bold leading-relaxed">
                      {playStatus === 'lost' ? step.failText : step.drawText}
                    </div>
                    <button onClick={restartPlay}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition"
                      style={{ backgroundColor: accent }}>
                      <RotateCcw size={18} /> 再来一盘
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ChoicePanel({
  step, accent, choicePick, wrongChoices, onPick, onNext,
}: {
  step: ChoiceStep
  accent: string
  choicePick: number | null
  wrongChoices: number[]
  onPick: (i: number) => void
  onNext: () => void
}) {
  return (
    <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
      <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
        🤔 想一想
      </div>
      <p className="text-lg font-bold leading-relaxed text-[#3a322c] mb-4">{step.question}</p>
      <div className="flex flex-col gap-2.5">
        {step.options.map((opt, i) => {
          const isRight = choicePick === i
          const isWrong = wrongChoices.includes(i)
          return (
            <button key={i} onClick={() => onPick(i)}
              disabled={choicePick === step.answer}
              className={`text-left px-5 py-3.5 rounded-2xl border-2 font-bold text-[16px] transition ${
                isRight
                  ? 'bg-[#e7f5ec] border-[#2E7D52] text-[#20573b]'
                  : isWrong
                    ? 'bg-[#fdecea] border-[#e05252]/40 text-[#c0392b] line-through opacity-70'
                    : 'bg-white border-[#1f1a17]/15 hover:border-[#1f1a17]/50 text-[#3a322c]'
              }`}>
              {opt}
            </button>
          )
        })}
      </div>
      {choicePick === step.answer && (
        <div className="mt-4">
          <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
            ✅ {step.explain}
          </div>
          <button onClick={onNext}
            className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition"
            style={{ backgroundColor: accent }}>
            继续 <ArrowRight size={18} />
          </button>
        </div>
      )}
    </div>
  )
}
