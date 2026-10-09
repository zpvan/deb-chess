import { useCallback, useEffect, useRef, useState } from 'react'
import ChessBoard from '@/components/ChessBoard'
import Confetti from '@/components/Confetti'
import ThemeToggle from '@/components/ThemeToggle'
import LangToggle from '@/components/LangToggle'
import { useLang } from '@/i18n'
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

export default function Lesson({ levelId, onExit, onNext }: Props) {
  const { t, lang } = useLang()
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
      const s = await api.createSession(levelId, lang)
      setSt(s)
      setError(null)
      setReplyShown(false)
      setPickedChoice(null)
      setWrongChoices([])
      setShowHint(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : t('lesson.loadError'))
    }
  }, [levelId, lang, t])

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
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : t('common.error'))
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
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : t('common.error'))
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
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : t('common.error'))
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
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  // ---------------- 加载/错误 ----------------
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface px-4">
        <div className="bg-surface-container rounded-3xl elev-1 p-8 text-center max-w-sm">
          <p className="font-bold text-[var(--board-check)] mb-4">{error}</p>
          <button onClick={() => void start()}
            className="state-layer px-6 py-3 rounded-full bg-primary text-on-primary font-bold transition">
            {t('common.retry')}
          </button>
        </div>
      </div>
    )
  }
  if (!st) {
    return <div className="min-h-screen bg-surface text-on-surface flex items-center justify-center font-display text-2xl">{t('app.loading')}</div>
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
      <div className="min-h-screen flex items-center justify-center px-4 py-10 bg-surface">
        <Confetti />
        <div className="w-full max-w-md bg-surface-container rounded-3xl elev-2 p-6 text-center">
          <div className="text-5xl mb-1">🏆</div>
          <h2 className="font-display text-2xl mb-1">{t('lesson.finished.title')}</h2>
          <p className="text-on-surface-variant mb-3">{st.chapter_title} · {st.level_title}</p>
          <div className="inline-block px-4 py-1.5 rounded-full text-sm font-bold text-white mb-4" style={{ backgroundColor: accent }}>
            {t('lesson.finished.skill')}{st.level_skill}
          </div>
          <div className="flex justify-center gap-2 mb-5">
            {[1, 2, 3].map((n) => (
              <Star key={n} size={44} strokeWidth={1.5}
                className={n <= st.stars ? 'fill-star text-star' : 'fill-outline-variant/30 text-outline-variant'} />
            ))}
          </div>
          <p className="text-sm text-on-surface-variant mb-6">
            {st.mistakes === 0 ? t('lesson.finished.perfect') : t('lesson.finished.mistakes', { n: st.mistakes })}
          </p>
          <div className="flex flex-col gap-3">
            {onNext && (
              <button onClick={onNext} className="state-layer w-full py-3.5 rounded-full bg-primary text-on-primary font-bold text-lg flex items-center justify-center gap-2 transition elev-1">
                {t('common.next')} <ArrowRight size={20} />
              </button>
            )}
            <div className="flex gap-3">
              <button onClick={() => void start()}
                className="flex-1 py-3 rounded-full border border-outline-variant text-primary font-bold flex items-center justify-center gap-2 hover:bg-primary/10 transition">
                <RotateCcw size={18} /> {t('common.playAgain')}
              </button>
              <button onClick={onExit}
                className="flex-1 py-3 rounded-full border border-outline-variant text-primary font-bold flex items-center justify-center gap-2 hover:bg-primary/10 transition">
                <MapIcon size={18} /> {t('common.backToMap')}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* 顶栏 */}
      <div className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-4xl mx-auto px-4 py-2 flex items-center gap-3">
          <button onClick={onExit} className="p-2 rounded-full hover:bg-on-surface/10 transition" aria-label={t('nav.back')}>
            <ArrowLeft size={22} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-bold" style={{ color: accent }}>{st.chapter_badge} · {st.chapter_title}</div>
            <div className="font-display text-base leading-tight truncate">{st.level_title}</div>
          </div>
          <div className="flex items-center gap-1.5">
            {Array.from({ length: st.step_count }).map((_, i) => (
              <span key={i} className="w-2.5 h-2.5 rounded-full transition"
                style={{ backgroundColor: i < st.step_index ? accent : i === st.step_index ? 'var(--star)' : 'var(--outline-variant)' }} />
            ))}
          </div>
          <LangToggle />
          <ThemeToggle />
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-4 pb-6">
        <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:items-center">
          {/* 棋盘 */}
          {boardFen && (
            <div key={`${st.step_index}-${wrongFlash}`} className="w-full max-w-[min(100%,400px)] md:max-w-[min(100%,56vh)] mx-auto">
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
                <div className="mt-3 text-center text-sm font-bold text-on-surface-variant">{step.sideLabel}</div>
              )}
              {step.type === 'play' && (
                <div className="mt-3 text-center text-sm font-bold text-on-surface-variant">
                  {awaitingReply ? t('lesson.thinking') : t('lesson.myMoves', { n: st.my_moves })}
                </div>
              )}
            </div>
          )}

          {/* 文字区 */}
          <div>
            {step.type === 'teach' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <h3 className="font-display text-xl mb-2" style={{ color: accent }}>{step.title}</h3>
                {(step.text ?? []).map((t, i) => (
                  <p key={i} className="text-[15px] leading-relaxed text-on-surface mb-2">{t}</p>
                ))}
                <button onClick={() => void goNext()} disabled={busy}
                  className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                  style={{ backgroundColor: accent }}>
                  {t('common.iUnderstand')} <ArrowRight size={18} />
                </button>
              </div>
            )}

            {isPuzzle && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  {step.type === 'mate' ? t('lesson.badge.mate') : step.type === 'line' ? t('lesson.badge.line') : t('lesson.badge.move')}
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface">
                  {step.type === 'line' ? st.line_prompt : step.prompt}
                </p>

                {!st.solved && (
                  <div className="mt-4 flex items-center gap-3">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border border-outline-variant text-primary font-bold text-sm hover:bg-primary/10 transition">
                        <Lightbulb size={16} /> {t('lesson.hint')}
                      </button>
                    )}
                    <span className="text-sm text-on-surface-variant">{t('lesson.tapGuide')}</span>
                  </div>
                )}
                {showHint && !st.solved && step.hint && (
                  <div className="mt-3 p-3 rounded-2xl bg-hint-container text-on-hint-container text-[15px] leading-relaxed">
                    💡 {step.hint}
                  </div>
                )}

                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      🎉 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      {t('common.continue')} <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {wrongFlash > 0 && !st.solved && (
                  <p className="mt-3 text-[var(--board-check)] font-bold text-sm">{t('lesson.wrong')}</p>
                )}
              </div>
            )}

            {step.type === 'choice' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  {t('lesson.badge.choice')}
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface mb-4">{step.question}</p>
                <div className="flex flex-col gap-2.5">
                  {(step.options ?? []).map((opt, i) => {
                    const isRight = pickedChoice === i
                    const isWrong = wrongChoices.includes(i)
                    return (
                      <button key={i} onClick={() => void handleChoice(i)}
                        disabled={st.solved || busy}
                        className={`text-left px-5 py-3.5 rounded-2xl border font-bold text-[16px] transition ${
                          isRight
                            ? 'bg-success-container border-transparent text-on-success-container'
                            : isWrong
                              ? 'bg-error-container border-transparent text-on-error-container line-through opacity-70'
                              : 'bg-surface border-outline-variant hover:bg-primary/10 text-on-surface'
                        }`}>
                        {opt}
                      </button>
                    )
                  })}
                </div>
                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      ✅ {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      {t('common.continue')} <ArrowRight size={18} />
                    </button>
                  </div>
                )}
              </div>
            )}

            {step.type === 'play' && (
              <div className="bg-surface-container rounded-3xl p-5 elev-1">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  <Swords size={12} className="inline -mt-0.5 mr-1" /> {t('lesson.badge.play')}
                </div>
                <p className="text-base font-bold leading-relaxed text-on-surface">{step.prompt}</p>

                {/* 开局前可选对手档位 */}
                {st.play_status === 'playing' && st.my_moves === 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(['random', 'greedy', 'smart'] as const).map((b) => (
                      <button key={b} onClick={() => void restart(b)} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold transition ${
                          st.bot_style === b
                            ? 'bg-primary text-on-primary'
                            : 'border border-outline-variant text-on-surface-variant hover:bg-primary/10'
                        }`}>
                        {t(`lesson.bot.${b}`)}
                      </button>
                    ))}
                    {stockfishAvailable && (
                      <button onClick={() => void restart('master')} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold transition ${
                          st.bot_style === 'master'
                            ? 'bg-primary text-on-primary'
                            : 'border border-outline-variant text-on-surface-variant hover:bg-primary/10'
                        }`}>
                        {t('lesson.bot.master')}
                      </button>
                    )}
                  </div>
                )}

                {st.play_status === 'playing' && (
                  <div className="mt-4">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border border-outline-variant text-primary font-bold text-sm hover:bg-primary/10 transition">
                        <Lightbulb size={16} /> {t('lesson.hint')}
                      </button>
                    )}
                    {showHint && (
                      <div className="mt-3 p-3 rounded-2xl bg-hint-container text-on-hint-container text-[15px] leading-relaxed">
                        💡 {step.hint}
                      </div>
                    )}
                  </div>
                )}

                {st.play_status === 'won' && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-success-container text-on-success-container font-bold leading-relaxed">
                      🏆 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      {t('common.continue')} <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {(st.play_status === 'lost' || st.play_status === 'draw') && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-error-container text-on-error-container font-bold leading-relaxed">
                      {st.end_text}
                    </div>
                    <button onClick={() => void restart()} disabled={busy}
                      className="state-layer mt-4 px-6 py-2.5 rounded-full text-white font-bold flex items-center gap-2 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      <RotateCcw size={18} /> {t('common.playAgain')}
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
