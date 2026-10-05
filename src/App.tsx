import { useState } from 'react'
import { Routes, Route } from 'react-router'
import Home from './pages/Home'
import MapPage from './pages/Map'
import Lesson from './pages/Lesson'
import { ProgressProvider } from './state/progress'
import { CurriculumProvider, useCurriculum } from './state/curriculum'

type Page = { name: 'home' } | { name: 'map' } | { name: 'lesson'; levelId: string }

function Shell() {
  const [page, setPage] = useState<Page>({ name: 'home' })
  const { flatLevels, loading } = useCurriculum()

  if (loading) {
    return <div className="min-h-screen bg-[#fff8ea] flex items-center justify-center font-display text-2xl">加载中……</div>
  }

  // 所有页面都在 / 下渲染,站内用状态切换,保证静态预览可用
  if (page.name === 'lesson') {
    const idx = flatLevels.findIndex((f) => f.level.id === page.levelId)
    const next = idx >= 0 ? flatLevels[idx + 1] : undefined
    return (
      <Lesson
        key={page.levelId}
        levelId={page.levelId}
        onExit={() => setPage({ name: 'map' })}
        onNext={next ? () => setPage({ name: 'lesson', levelId: next.level.id }) : null}
      />
    )
  }
  if (page.name === 'map') {
    return <MapPage onOpen={(levelId) => setPage({ name: 'lesson', levelId })} onHome={() => setPage({ name: 'home' })} />
  }
  return <Home onStart={() => setPage({ name: 'map' })} />
}

export default function App() {
  return (
    <CurriculumProvider>
      <ProgressProvider>
        <Routes>
          <Route path="/" element={<Shell />} />
          <Route path="*" element={<Shell />} />
        </Routes>
      </ProgressProvider>
    </CurriculumProvider>
  )
}
