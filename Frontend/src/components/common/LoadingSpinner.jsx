import { useEffect, useState } from 'react'

const DEFAULT_MESSAGES = ['Loading…', 'Fetching the details…', 'Almost there…']

function LoadingSpinner({ messages = DEFAULT_MESSAGES, compact = false, className = '' }) {
  const [i, setI] = useState(0)

  useEffect(() => {
    if (messages.length <= 1) return
    const id = setInterval(() => setI((n) => (n + 1) % messages.length), 1700)
    return () => clearInterval(id)
  }, [messages])

  if (compact) {
    return (
      <div className={`flex items-center gap-2.5 py-2 ${className}`}>
        <div className="relative h-4 w-4 flex-none">
          <div className="absolute inset-0 rounded-full border-2 border-white/10" />
          <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-[#FF7A59] border-r-[#FF7A59]" />
        </div>
        <div key={i} className="animate-fade-in text-[14px] text-white/45">
          {messages[i]}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex flex-col items-center justify-center gap-3.5 py-14 ${className}`}>
      <div className="relative h-9 w-9">
        <div className="absolute inset-0 rounded-full border-2 border-white/10" />
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-[#FF7A59] border-r-[#FF7A59]" />
      </div>
      <div key={i} className="animate-fade-in text-[14px] font-medium tracking-[-0.005em] text-white/45">
        {messages[i]}
      </div>
    </div>
  )
}

export default LoadingSpinner
