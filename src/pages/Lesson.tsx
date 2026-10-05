import { useCallback, useEffect, useRef, useState } from 'react'
import ChessBoard from '@/components/ChessBoard'
import Confetti from '@/components/Confetti'
import { sounds } from '@/lib/sound'
import { api, ApiError, type SessionState } from '@/lib/api'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { ArrowLeft, ArrowRight, Lightbulb, RotateCcw, Star, Map as MapIcon, Swords } from 'lucide-react'

interface Props {
  levelId: string
  onExit: () => void
  onNext: (() => void) | null
}

const BOT_LABELS: Record<string, string> = {
  random: '随便走',
  greedy: '贪吃鬼',
  smart: '小聪明',
  master: '大师 Stockfish',
}

export default function Lesson({ levelId, onExit, onNext }: Props) {
  const { refresh } = useProgress()
  const { stockfishAvailable } = useCurriculum()

  const [st, setSt] = useState<SessionState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [wrongFlash, setWrongFlash] = useState(0)
  const [showHint, setShowHint] = useState(false)
  const [wrongChoices, setWrongChoices] = useState<number[]>([])
  const [pickedChoice, setPickedChoice] = useState<number | null>(null)
  // 对手回应延迟动画:后端已推进局面,前端先展示自己走完的局面,700ms 后再展示回应
  const [replyShown, setReplyShown] = useState(false)
  const replyTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const start = useCallback(async () => {
    try {
      const s = await api.createSession(levelId)
      setSt(s)
      setError(null)
      setReplyShown(false)
      setPickedChoice(null)
      setWrongChoices([])
      setShowHint(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载失败,请检查后端是否启动')
    }
  }, [levelId])

  useEffect(() => {
    void start()
    return () => {
      if (replyTimer.current) clearTimeout(replyTimer.current)
    }
  }, [start])

  const apply = (s: SessionState) => {
    if (s.step_index !== st?.step_index) {
      setShowHint(false)
      setWrongChoices([])
      setPickedChoice(null)
    }
    setSt(s)
    setReplyShown(false)
    if (replyTimer.current) clearTimeout(replyTimer.current)
    if (s.reply) {
      replyTimer.current = setTimeout(() => {
        setReplyShown(true)
        sounds.move()
      }, 700)
    }
    if (s.finished) void refresh().catch(() => undefined)
  }

  /** 会话过期(404)时重建会话从头开始本关,返回 true 表示已处理 */
  const recover404 = async (e: unknown): Promise<boolean> => {
    if (e instanceof ApiError && e.status === 404) {
      await start()
      return true
    }
    return false
  }

  const handleMove = async (uci: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionMove(st.session_id, uci)
      if (s.last_result === 'wrong') {
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else if (st.step.type === 'play') {
        sounds.move()
        if (s.play_status === 'won') sounds.checkmate()
        else if (s.play_status === 'lost' || s.play_status === 'draw') sounds.error()
      } else if (s.solved) {
        if (st.step.type === 'move') sounds.success()
        else sounds.checkmate() // mate / line 完成
      } else {
        sounds.move() // line 剧本中段
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const handleChoice = async (i: number) => {
    if (!st || busy || st.solved) return
    setBusy(true)
    try {
      const s = await api.sessionChoice(st.session_id, i)
      if (s.last_result === 'wrong') {
        setWrongChoices((w) => [...w, i])
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else {
        setPickedChoice(i)
        sounds.success()
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const goNext = async () => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionNext(st.session_id)
      if (s.finished) sounds.fanfare()
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const restart = async (bot?: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      apply(await api.restartPlay(st.session_id, bot))
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  // ---------------- 加载/错误 ----------------
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#fff8ea] px-4">
        <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-8 text-center max-w-sm">
          <p className="font-bold text-[#c0392b] mb-4">{error}</p>
          <button onClick={() => void start()}
            className="px-6 py-3 rounded-full bg-[#1f1a17] text-white font-bold hover:bg-[#3a322c] transition">
            重试
          </button>
        </div>
      </div>
    )
  }
  if (!st) {
    return <div className="min-h-screen bg-[#fff8ea] flex items-center justify-center font-display text-2xl">加载中……</div>
  }

  const step = st.step
  const accent = st.chapter_color
  const isPuzzle = step.type === 'mate' || step.type === 'move' || step.type === 'line'
  // 有对手回应且动画未播时,棋盘锁定并展示中间局面
  const awaitingReply = st.reply !== null && !replyShown
  const boardFen = awaitingReply ? st.fen : (st.reply?.fen ?? st.fen)
  const boardLastMove: [string, string] | null = awaitingReply ? st.last_move : (st.reply?.move ?? st.last_move)

  // ---------------- 通关结算 ----------------
  if (st.finished) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-10" style={{ backgroundColor: st.chapter_soft }}>
        <Confetti />
        <div className="w-full max-w-md bg-[#fffdf6] rounded-3xl shadow-xl p-8 text-center border-4 border-[#1f1a17]">
          <div className="text-6xl mb-2">🏆</div>
          <h2 className="font-display text-3xl mb-1">闯关成功!</h2>
          <p className="text-[#6b5d4f] mb-3">{st.chapter_title} · {st.level_title}</p>
          <div className="inline-block px-4 py-1.5 rounded-full text-sm font-bold text-white mb-4" style={{ backgroundColor: accent }}>
            获得技能:{st.level_skill}
          </div>
          <div className="flex justify-center gap-2 mb-5">
            {[1, 2, 3].map((n) => (
              <Star key={n} size={44} strokeWidth={1.5}
                className={n <= st.stars ? 'fill-[#f7c948] text-[#b8860b]' : 'fill-[#ece5d8] text-[#cfc4b0]'} />
            ))}
          </div>
          <p className="text-sm text-[#6b5d4f] mb-6">
            {st.mistakes === 0 ? '完美通关,一次都没错!菲舍尔也会为你鼓掌。' : `错了 ${st.mistakes} 次,复习一下还能拿更多星星哦!`}
          </p>
          <div className="flex flex-col gap-3">
            {onNext && (
              <button onClick={onNext} className="w-full py-3.5 rounded-full bg-[#1f1a17] text-white font-bold text-lg flex items-center justify-center gap-2 hover:bg-[#3a322c] transition">
                下一关 <ArrowRight size={20} />
              </button>
            )}
            <div className="flex gap-3">
              <button onClick={() => void start()}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <RotateCcw size={18} /> 再玩一次
              </button>
              <button onClick={onExit}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <MapIcon size={18} /> 回地图
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: st.chapter_soft }}>
      {/* 顶栏 */}
      <div className="sticky top-0 z-20 bg-[#fffdf6]/95 backdrop-blur border-b-2 border-[#1f1a17]/10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onExit} className="p-2 rounded-full hover:bg-[#f3ead9] transition" aria-label="返回">
            <ArrowLeft size={22} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-bold" style={{ color: accent }}>{st.chapter_badge} · {st.chapter_title}</div>
            <div className="font-display text-lg leading-tight truncate">{st.level_title}</div>
          </div>
          <div className="flex items-center gap-1.5">
            {Array.from({ length: st.step_count }).map((_, i) => (
              <span key={i} className="w-2.5 h-2.5 rounded-full transition"
                style={{ backgroundColor: i < st.step_index ? accent : i === st.step_index ? '#f7c948' : '#ddd2bd' }} />
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 pb-24">
        <div className={`grid gap-6 ${step.type === 'choice' || step.type === 'teach' ? 'md:grid-cols-[1fr_1fr] md:items-center' : ''}`}>
          {/* 棋盘 */}
          {boardFen && (
            <div key={`${st.step_index}-${wrongFlash}`} className="w-full max-w-[520px] mx-auto">
              <ChessBoard
                fen={boardFen}
                interactive={((isPuzzle && !st.solved) || (step.type === 'play' && st.play_status === 'playing')) && !awaitingReply && !busy}
                onMove={(uci) => void handleMove(uci)}
                orientation={step.orientation || 'white'}
                highlight={step.type === 'teach' ? step.highlight : undefined}
                arrows={step.type === 'teach' ? step.arrows : undefined}
                lastMove={boardLastMove}
                shake={wrongFlash > 0}
                legalMoves={awaitingReply ? [] : st.legal_moves}
                checkSquare={awaitingReply ? null : st.check_square}
              />
              {step.sideLabel && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">{step.sideLabel}</div>
              )}
              {step.type === 'play' && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">
                  {awaitingReply ? '🤖 对方思考中……' : `你已走 ${st.my_moves} 步`}
                </div>
              )}
            </div>
          )}

          {/* 文字区 */}
          <div>
            {step.type === 'teach' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <h3 className="font-display text-2xl mb-3" style={{ color: accent }}>{step.title}</h3>
                {(step.text ?? []).map((t, i) => (
                  <p key={i} className="text-[17px] leading-relaxed text-[#3a322c] mb-2">{t}</p>
                ))}
                <button onClick={() => void goNext()} disabled={busy}
                  className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
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
                  {step.type === 'line' ? st.line_prompt : step.prompt}
                </p>

                {!st.solved && (
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
                {showHint && !st.solved && step.hint && (
                  <div className="mt-3 p-3 rounded-2xl bg-[#fdf3d7] text-[#7a5c10] text-[15px] leading-relaxed">
                    💡 {step.hint}
                  </div>
                )}

                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🎉 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {wrongFlash > 0 && !st.solved && (
                  <p className="mt-3 text-[#c0392b] font-bold text-sm">这一步不对,再想想,你可以的!</p>
                )}
              </div>
            )}

            {step.type === 'choice' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  🤔 想一想
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c] mb-4">{step.question}</p>
                <div className="flex flex-col gap-2.5">
                  {(step.options ?? []).map((opt, i) => {
                    const isRight = pickedChoice === i
                    const isWrong = wrongChoices.includes(i)
                    return (
                      <button key={i} onClick={() => void handleChoice(i)}
                        disabled={st.solved || busy}
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
                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      ✅ {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
              </div>
            )}

            {step.type === 'play' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  <Swords size={12} className="inline -mt-0.5 mr-1" /> 实战对弈
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c]">{step.prompt}</p>

                {/* 开局前可选对手档位 */}
                {st.play_status === 'playing' && st.my_moves === 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(['random', 'greedy', 'smart'] as const).map((b) => (
                      <button key={b} onClick={() => void restart(b)} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${
                          st.bot_style === b
                            ? 'bg-[#1f1a17] text-white border-[#1f1a17]'
                            : 'border-[#1f1a17]/20 text-[#6b5d4f] hover:border-[#1f1a17]/60'
                        }`}>
                        {BOT_LABELS[b]}
                      </button>
                    ))}
                    {stockfishAvailable && (
                      <button onClick={() => void restart('master')} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${
                          st.bot_style === 'master'
                            ? 'bg-[#7C4DA0] text-white border-[#7C4DA0]'
                            : 'border-[#7C4DA0]/40 text-[#7C4DA0] hover:border-[#7C4DA0]'
                        }`}>
                        {BOT_LABELS.master}
                      </button>
                    )}
                  </div>
                )}

                {st.play_status === 'playing' && (
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

                {st.play_status === 'won' && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🏆 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {(st.play_status === 'lost' || st.play_status === 'draw') && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#fdecea] border-2 border-[#e05252]/30 text-[#8c2f23] font-bold leading-relaxed">
                      {st.end_text}
                    </div>
                    <button onClick={() => void restart()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
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
