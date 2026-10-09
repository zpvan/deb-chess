import { Moon, Sun } from 'lucide-react'
import { useDarkMode } from '@/hooks/useDarkMode'

export default function ThemeToggle() {
  const [dark, toggle] = useDarkMode()
  return (
    <button
      onClick={toggle}
      aria-label={dark ? '切换到浅色模式' : '切换到深色模式'}
      className="p-2 rounded-full text-on-surface-variant hover:bg-on-surface/10 transition"
    >
      {dark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
