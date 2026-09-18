import { useMemo } from 'react'

const COLORS = ['#2E7D52', '#E07B2A', '#2F6FBA', '#f7d354', '#e05252', '#8C6D3F']

export default function Confetti({ count = 90 }: { count?: number }) {
  const pieces = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        left: Math.random() * 100,
        delay: Math.random() * 1.2,
        dur: 2.2 + Math.random() * 1.8,
        color: COLORS[i % COLORS.length],
        size: 8 + Math.random() * 8,
        rot: Math.random() * 360,
      })),
    [count],
  )
  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      {pieces.map((p, i) => (
        <span
          key={i}
          className="absolute top-[-5%] rounded-[2px] animate-[confetti-fall_linear_forwards]"
          style={{
            left: `${p.left}%`,
            width: p.size,
            height: p.size * 0.6,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.dur}s`,
            transform: `rotate(${p.rot}deg)`,
          }}
        />
      ))}
    </div>
  )
}
