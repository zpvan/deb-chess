// 轻量音效：无需音频文件，用 WebAudio 合成
let ctx: AudioContext | null = null

function ac(): AudioContext | null {
  try {
    if (!ctx) ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)()
    if (ctx.state === 'suspended') void ctx.resume()
    return ctx
  } catch {
    return null
  }
}

function tone(freq: number, start: number, dur: number, type: OscillatorType = 'sine', gain = 0.12) {
  const a = ac()
  if (!a) return
  const osc = a.createOscillator()
  const g = a.createGain()
  osc.type = type
  osc.frequency.value = freq
  const t0 = a.currentTime + start
  g.gain.setValueAtTime(0.0001, t0)
  g.gain.exponentialRampToValueAtTime(gain, t0 + 0.02)
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur)
  osc.connect(g).connect(a.destination)
  osc.start(t0)
  osc.stop(t0 + dur + 0.05)
}

export const sounds = {
  move() {
    tone(440, 0, 0.12, 'triangle', 0.08)
  },
  success() {
    tone(523, 0, 0.15, 'triangle')
    tone(659, 0.12, 0.15, 'triangle')
    tone(784, 0.24, 0.25, 'triangle')
  },
  error() {
    tone(220, 0, 0.2, 'sawtooth', 0.06)
  },
  fanfare() {
    ;[523, 659, 784, 1047].forEach((f, i) => tone(f, i * 0.14, 0.3, 'triangle', 0.14))
    tone(1319, 0.6, 0.5, 'triangle', 0.12)
  },
  checkmate() {
    ;[392, 523, 659, 784, 1047].forEach((f, i) => tone(f, i * 0.1, 0.28, 'square', 0.05))
  },
}
