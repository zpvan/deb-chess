import { useState } from 'react'
import { Routes, Route } from 'react-router'
import Home from './pages/Home'
import MapPage from './pages/Map'
import Lesson from './pages/Lesson'
import { findLevel, flatLevels } from './data/curriculum'
import { ProgressProvider } from './state/progress'

type Page = { name: 'home' } | { name: 'map' } | { name: 'lesson'; levelId: string }

function Shell() {
  const [page, setPage] = useState<Page>({ name: 'home' })

  // 所有页面都在 / 下渲染，站内用状态切换，保证静态预览可用
  if (page.name === 'lesson') {
    const flat = findLevel(page.levelId)
    if (flat) {
      const next = flatLevels[flat.index + 1]
      return (
        <Lesson
          key={page.levelId}
          flat={flat}
          onExit={() => setPage({ name: 'map' })}
          onNext={next ? () => setPage({ name: 'lesson', levelId: next.level.id }) : null}
        />
      )
    }
  }
  if (page.name === 'map') {
    return <MapPage onOpen={(levelId) => setPage({ name: 'lesson', levelId })} onHome={() => setPage({ name: 'home' })} />
  }
  return <Home onStart={() => setPage({ name: 'map' })} />
}

export default function App() {
  return (
    <ProgressProvider>
      <Routes>
        <Route path="/" element={<Shell />} />
        <Route path="*" element={<Shell />} />
      </Routes>
    </ProgressProvider>
  )
}
