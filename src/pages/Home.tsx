import ChessBoard from '@/components/ChessBoard'
import ThemeToggle from '@/components/ThemeToggle'
import LangToggle from '@/components/LangToggle'
import { useLang } from '@/i18n'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, BookOpen, Crown, Swords, Flag, Gamepad2 } from 'lucide-react'

interface Props {
  onStart: () => void
}

export default function Home({ onStart }: Props) {
  const { t } = useLang()
  const { xp, totalStars, rank, starsOf } = useProgress()
  const { flatLevels, totalPuzzles } = useCurriculum()
  const nextLevel = flatLevels.find((f) => starsOf(f.level.id) === 0)

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* 顶栏 */}
      <header className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <span className="text-3xl" style={{ fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif' }}>♞</span>
          <span className="font-display text-xl flex-1">{t('app.title')}</span>
          <div className="flex items-center gap-1 text-sm font-bold bg-primary-container text-on-primary-container px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-star text-star" /> {totalStars}
          </div>
          <div className="hidden sm:block text-sm font-bold bg-surface-container px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {t('common.xpSuffix', { xp })}
          </div>
          <LangToggle />
          <ThemeToggle />
        </div>
      </header>

      {/* 主视觉 */}
      <section className="max-w-5xl mx-auto px-4 pt-10 pb-14 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary-container text-on-primary-container text-sm font-bold mb-5">
            {t('home.badge')}
          </div>
          <h1 className="font-display text-4xl sm:text-5xl leading-tight mb-5">
            {t('home.hero.pre')}<span className="text-primary">{t('home.hero.accent')}</span>{t('home.hero.post')}
            <br />
            {t('home.hero.line2')}
          </h1>
          <p className="text-lg text-on-surface-variant leading-relaxed mb-8">
            {t('home.intro')}
          </p>
          <div className="flex flex-wrap gap-4">
            <button onClick={onStart}
              className="state-layer px-8 py-4 rounded-full bg-primary text-on-primary font-display text-xl flex items-center gap-2 transition elev-2 hover:-translate-y-0.5">
              <Play size={22} className="fill-current" />
              {nextLevel && nextLevel.index > 0 ? t('home.continue') : t('home.start')}
            </button>
          </div>
          <div className="mt-6 flex items-center gap-4 text-sm text-on-surface-variant">
            <span>{t('home.stats.levels', { n: flatLevels.length })}</span>
            <span>{t('home.stats.puzzles', { n: totalPuzzles })}</span>
            <span>{t('home.stats.play')}</span>
            <span>{t('home.stats.stars')}</span>
          </div>
        </div>
        <div className="max-w-[420px] w-full mx-auto">
          <ChessBoard
            fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"
            arrows={[['a1', 'a8']]}
            highlight={['f7', 'g7', 'h7']}
          />
          <p className="text-center text-sm text-on-surface-variant mt-3 font-bold">
            {t('home.boardCaption')}
          </p>
        </div>
      </section>

      {/* 学习路径 */}
      <section className="max-w-5xl mx-auto px-4 pb-16">
        <h2 className="font-display text-3xl mb-2 text-center">{t('home.pathTitle')}</h2>
        <p className="text-center text-on-surface-variant mb-10 max-w-xl mx-auto">
          {t('home.pathDesc')}
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { icon: <Crown size={26} />, color: '#2E7D52', title: t('home.path1.title'), desc: t('home.path1.desc') },
            { icon: <Swords size={26} />, color: '#E07B2A', title: t('home.path2.title'), desc: t('home.path2.desc') },
            { icon: <Flag size={26} />, color: '#2F6FBA', title: t('home.path3.title'), desc: t('home.path3.desc') },
            { icon: <Gamepad2 size={26} />, color: '#7C4DA0', title: t('home.path4.title'), desc: t('home.path4.desc') },
          ].map((c) => (
            <div key={c.title} className="rounded-3xl p-6 bg-surface-container hover:-translate-y-1 transition elev-1 hover:elev-2">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white mb-4" style={{ backgroundColor: c.color }}>
                {c.icon}
              </div>
              <h3 className="font-display text-xl mb-2" style={{ color: c.color }}>{c.title}</h3>
              <p className="text-on-surface-variant leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 练习方法 */}
      <section className="bg-primary-container text-on-primary-container py-14">
        <div className="max-w-5xl mx-auto px-4 grid md:grid-cols-[auto_1fr] gap-8 items-center">
          <div className="text-7xl text-center" style={{ fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif' }}>♚</div>
          <div>
            <div className="flex items-center gap-2 mb-3 font-bold">
              <BookOpen size={18} /> {t('home.methodTitle')}
            </div>
            <blockquote className="text-lg leading-relaxed">
              {t('home.methodQuote')}
            </blockquote>
            <p className="mt-3 opacity-75">{t('home.methodBy')}</p>
          </div>
        </div>
      </section>

      <footer className="max-w-5xl mx-auto px-4 py-8 text-center text-sm text-on-surface-variant">
        <p>{t('home.footer')}</p>
      </footer>
    </div>
  )
}
