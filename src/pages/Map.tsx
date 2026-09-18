import { chapters, flatLevels } from '@/data/curriculum'
import { useProgress } from '@/state/progress'
import { Star, Play, ChevronLeft } from 'lucide-react'

interface Props {
  onOpen: (levelId: string) => void
  onHome: () => void
}

export default function MapPage({ onOpen, onHome }: Props) {
  const { starsOf, totalStars, xp, rank } = useProgress()

  return (
    <div className="min-h-screen bg-[#fff8ea] pb-24">
      {/* 顶部状态栏 */}
      <div className="sticky top-0 z-20 bg-[#fffdf6]/95 backdrop-blur border-b-2 border-[#1f1a17]/10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onHome} className="p-2 rounded-full hover:bg-[#f3ead9] transition" aria-label="首页">
            <ChevronLeft size={22} />
          </button>
          <div className="font-display text-xl flex-1">闯关地图</div>
          <div className="flex items-center gap-1 text-sm font-bold bg-[#fdf3d7] px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-[#f7c948] text-[#b8860b]" /> {totalStars}
          </div>
          <div className="text-sm font-bold bg-[#e7f0fb] px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {xp}分
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-8">
        {chapters.map((ch) => (
          <section key={ch.id} className="mb-12">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-display text-lg shrink-0 shadow-md"
                style={{ backgroundColor: ch.color }}>
                {ch.badge.slice(0, 2)}
              </div>
              <div>
                <h2 className="font-display text-2xl" style={{ color: ch.color }}>{ch.title}</h2>
                <p className="text-[#6b5d4f] text-[15px] leading-relaxed">{ch.intro}</p>
              </div>
            </div>

            <div className="relative ml-6 border-l-4 border-dashed border-[#1f1a17]/15 pl-8 flex flex-col gap-4">
              {ch.levels.map((lv) => {
                const stars = starsOf(lv.id)
                const idx = flatLevels.findIndex((f) => f.level.id === lv.id)
                return (
                  <button
                    key={lv.id}
                    onClick={() => onOpen(lv.id)}
                    className="relative text-left rounded-3xl border-2 p-5 transition group bg-[#fffdf6] border-[#1f1a17]/15 hover:border-[#1f1a17]/60 hover:-translate-y-0.5 shadow-sm hover:shadow-md"
                  >
                    <span className="absolute -left-[47px] top-1/2 -translate-y-1/2 w-6 h-6 rounded-full border-4 border-[#fff8ea]"
                      style={{ backgroundColor: stars > 0 ? ch.color : '#f7c948' }} />
                    <div className="flex items-center gap-4">
                      <div className="w-11 h-11 rounded-full flex items-center justify-center font-display text-lg shrink-0"
                        style={{ backgroundColor: ch.soft, color: ch.color }}>
                        {stars > 0 ? <Star size={20} className="fill-current" /> : <Play size={18} className="fill-current" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-display text-lg leading-tight">
                          第 {idx + 1} 关 · {lv.title}
                        </div>
                        <div className="text-sm text-[#6b5d4f]">{lv.goal}</div>
                      </div>
                      {stars > 0 && (
                        <div className="flex gap-0.5 shrink-0">
                          {[1, 2, 3].map((n) => (
                            <Star key={n} size={18} strokeWidth={1.5}
                              className={n <= stars ? 'fill-[#f7c948] text-[#b8860b]' : 'fill-[#ece5d8] text-[#cfc4b0]'} />
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

        <p className="text-center text-sm text-[#a3927c] mt-4">
          跟着菲舍尔的方法：先把终局的“杀王”练熟，再学中局战术，最后学开局。循序渐进，每关都能拿星星！
        </p>
      </div>
    </div>
  )
}
