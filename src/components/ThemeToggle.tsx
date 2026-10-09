import { Moon, Sun } from 'lucide-react'
import { useDarkMode } from '@/hooks/useDarkMode'
import { useLang } from '@/i18n'

export default function ThemeToggle() {
  const [dark, toggle] = useDarkMode()
  const { t } = useLang()
  return (
    <button
      onClick={toggle}
      aria-label={dark ? t('theme.toLight') : t('theme.toDark')}
      className="p-2 rounded-full text-on-surface-variant hover:bg-on-surface/10 transition"
    >
      {dark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
