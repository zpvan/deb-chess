import ChessBoard from '@/components/ChessBoard'
import ThemeToggle from '@/components/ThemeToggle'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, BookOpen, Crown, Swords, Flag, Gamepad2 } from 'lucide-react'

interface Props {
  onStart: () => void
}

export default function Home({ onStart }: Props) {
  const { xp, totalStars, rank, starsOf } = useProgress()
  const { flatLevels, totalPuzzles } = useCurriculum()
  const nextLevel = flatLevels.find((f) => starsOf(f.level.id) === 0)

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* 顶栏 */}
      <header className="sticky top-0 z-20 bg-surface/95 backdrop-blur border-b border-outline-variant">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <span className="text-3xl" style={{ fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif' }}>♞</span>
          <span className="font-display text-xl flex-1">deb-chess 练级营</span>
          <div className="flex items-center gap-1 text-sm font-bold bg-primary-container text-on-primary-container px-3 py-1.5 rounded-full">
            <Star size={15} className="fill-star text-star" /> {totalStars}
          </div>
          <div className="hidden sm:block text-sm font-bold bg-surface-container px-3 py-1.5 rounded-full">
            {rank.icon} {rank.name} · {xp}分
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* 主视觉 */}
      <section className="max-w-5xl mx-auto px-4 pt-10 pb-14 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary-container text-on-primary-container text-sm font-bold mb-5">
            世界冠军的学棋方法
          </div>
          <h1 className="font-display text-4xl sm:text-5xl leading-tight mb-5">
            从<span className="text-primary">终局</span>开始,
            <br />
            一步步成为小棋王!
          </h1>
          <p className="text-lg text-on-surface-variant leading-relaxed mb-8">
            专为一年级小棋士设计:先看图想一想,再动手走棋,答对就能赢星星。
            从最简单的“底线杀”练起,直到学会完整的开局!
          </p>
          <div className="flex flex-wrap gap-4">
            <button onClick={onStart}
              className="state-layer px-8 py-4 rounded-full bg-primary text-on-primary font-display text-xl flex items-center gap-2 transition elev-2 hover:-translate-y-0.5">
              <Play size={22} className="fill-current" />
              {nextLevel && nextLevel.index > 0 ? '继续闯关' : '开始闯关'}
            </button>
          </div>
          <div className="mt-6 flex items-center gap-4 text-sm text-on-surface-variant">
            <span>♟ 共 {flatLevels.length} 关</span>
            <span>⭐ {totalPuzzles} 道互动棋题</span>
            <span>⚔️ 实战对弈</span>
            <span>🏆 星星奖励</span>
          </div>
        </div>
        <div className="max-w-[420px] w-full mx-auto">
          <ChessBoard
            fen="6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"
            arrows={[['a1', 'a8']]}
            highlight={['f7', 'g7', 'h7']}
          />
          <p className="text-center text-sm text-on-surface-variant mt-3 font-bold">
            经典的“底线杀”:车冲 a8,黑王被自己的小兵困住!
          </p>
        </div>
      </section>

      {/* 学习路径 */}
      <section className="max-w-5xl mx-auto px-4 pb-16">
        <h2 className="font-display text-3xl mb-2 text-center">为什么是“倒着学”?</h2>
        <p className="text-center text-on-surface-variant mb-10 max-w-xl mx-auto">
          先学杀王,棋越下越有目标。本站按这个思路设计了三段旅程。
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              icon: <Crown size={26} />,
              color: '#2E7D52',
              title: '第一章 · 终局',
              desc: '单车、单后、单马、单象、单兵——谁能杀光杆王?怎么杀?',
            },
            {
              icon: <Swords size={26} />,
              color: '#E07B2A',
              title: '第二章 · 中局',
              desc: '击双、牵制、闪将、得子四大武器,挑战“连续杀”。',
            },
            {
              icon: <Flag size={26} />,
              color: '#2F6FBA',
              title: '第三章 · 开局',
              desc: '意大利、西班牙、后翼弃兵、西西里、古印度——经典开局套路一网打尽。',
            },
            {
              icon: <Gamepad2 size={26} />,
              color: '#7C4DA0',
              title: '实战篇 · 对弈',
              desc: '和电脑真刀真枪下棋,再用“车王杀王”实操检验真本事。',
            },
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
              <BookOpen size={18} /> 程序化练习法
            </div>
            <blockquote className="text-lg leading-relaxed">
              “这本书会教你更快地分析棋题,找到要记住的关键模式。
              只要从头开始一题一题做下去,几秒钟之内你就能认出杀棋。”
            </blockquote>
            <p className="mt-3 opacity-75">—— 世界冠军的练棋秘诀:反复识别杀王模式,直到形成直觉</p>
          </div>
        </div>
      </section>

      <footer className="max-w-5xl mx-auto px-4 py-8 text-center text-sm text-on-surface-variant">
        <p>学习进度保存在本机服务器的数据库里,换浏览器也不丢哦。</p>
      </footer>
    </div>
  )
}
