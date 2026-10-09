import { useCallback, useEffect, useState } from 'react'

const KEY = 'deb-chess-theme'

function initial(): boolean {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'dark') return true
    if (saved === 'light') return false
  } catch { /* ignore */ }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

export function useDarkMode(): [boolean, () => void] {
  const [dark, setDark] = useState<boolean>(initial)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try {
      localStorage.setItem(KEY, dark ? 'dark' : 'light')
    } catch { /* ignore */ }
  }, [dark])

  const toggle = useCallback(() => setDark((d) => !d), [])
  return [dark, toggle]
}
