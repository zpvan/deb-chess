import ThemeToggle from '@/components/ThemeToggle'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, ChevronLeft } from 'lucide-react'

interface Props {
  onOpen: (levelId: string) => void
  onHome: () => void
}

export default function MapPage({ onOpen, onHome }: Props) {
  const { starsOf, totalStars, xp, rank } = useProgress()
  const { chapters, flatLevels } = useCurriculum()

  return (
    <div className="min-h-screen bg-surface text-on-surface pb-24">
      {/* 顶部状态栏 */}
      <div className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onHome} className="p-2 rounded-full hover:bg-on-surface/10 transition" aria-label="首页">
            <ChevronLeft size={22} />
          </button>
          <div className="font-display text-xl flex-1">闯关地图</div>
          <div className="flex items-center gap-1 text-sm font-bold bg-primary-container text-on-primary-container px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-star text-star" /> {totalStars}
          </div>
          <div className="text-sm font-bold bg-surface-container px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {xp}分
          </div>
          <ThemeToggle />
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-8">
        {chapters.map((ch) => (
          <section key={ch.id} className="mb-12">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-display text-lg shrink-0 elev-1"
                style={{ backgroundColor: ch.color }}>
                {ch.badge.slice(0, 2)}
              </div>
              <div>
                <h2 className="font-display text-2xl" style={{ color: ch.color }}>{ch.title}</h2>
                <p className="text-on-surface-variant text-[15px] leading-relaxed">{ch.intro}</p>
              </div>
            </div>

            <div className="relative ml-6 border-l-4 border-dashed border-outline-variant pl-8 flex flex-col gap-4">
              {ch.levels.map((lv) => {
                const stars = starsOf(lv.id)
                const idx = flatLevels.findIndex((f) => f.level.id === lv.id)
                return (
                  <button
                    key={lv.id}
                    onClick={() => onOpen(lv.id)}
                    className="relative text-left rounded-3xl p-5 transition group bg-surface-container elev-1 hover:elev-2 hover:-translate-y-0.5"
                  >
                    <span className="absolute -left-[47px] top-1/2 -translate-y-1/2 w-6 h-6 rounded-full border-4 border-[var(--surface)]"
                      style={{ backgroundColor: stars > 0 ? ch.color : 'var(--star)' }} />
                    <div className="flex items-center gap-4">
                      <div className="w-11 h-11 rounded-full flex items-center justify-center font-display text-lg shrink-0"
                        style={{ backgroundColor: `${ch.color}22`, color: ch.color }}>
                        {stars > 0 ? <Star size={20} className="fill-current" /> : <Play size={18} className="fill-current" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-display text-lg leading-tight">
                          第 {idx + 1} 关 · {lv.title}
                        </div>
                        <div className="text-sm text-on-surface-variant">{lv.goal}</div>
                      </div>
                      {stars > 0 && (
                        <div className="flex gap-0.5 shrink-0">
                          {[1, 2, 3].map((n) => (
                            <Star key={n} size={18} strokeWidth={1.5}
                              className={n <= stars ? 'fill-star text-star' : 'fill-outline-variant/30 text-outline-variant'} />
                          ))}
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </section>
        ))}

        <p className="text-center text-sm text-on-surface-variant mt-4">
          先把终局的“杀王”练熟,再学中局战术,最后学开局。循序渐进,每关都能拿星星!
        </p>
      </div>
    </div>
  )
}
