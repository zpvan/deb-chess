import { useLang, type Lang } from '@/i18n'

const OPTIONS: { value: Lang; label: string }[] = [
  { value: 'en', label: 'EN' },
  { value: 'zh', label: '中' },
]

export default function LangToggle() {
  const { lang, setLang } = useLang()
  return (
    <div className="flex items-center rounded-full border border-outline-variant p-0.5" role="group" aria-label="Language">
      {OPTIONS.map((o) => (
        <button
          key={o.value}
          onClick={() => setLang(o.value)}
          className={`px-2.5 py-1 rounded-full text-xs font-bold transition ${
            lang === o.value
              ? 'bg-primary-container text-on-primary-container'
              : 'text-on-surface-variant hover:bg-on-surface/10'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}
