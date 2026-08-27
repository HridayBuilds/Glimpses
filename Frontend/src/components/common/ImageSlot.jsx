import { useState } from 'react'

function ImageSlot({ src, label, className = '', objectPosition = '50% 50%' }) {
  const [errored, setErrored] = useState(false)

  if (src && !errored) {
    return (
      <img
        src={src}
        alt={label}
        onError={() => setErrored(true)}
        className={`h-full w-full object-cover ${className}`}
        style={{ objectPosition }}
      />
    )
  }

  return (
    <div
      className={`flex h-full w-full items-center justify-center bg-gradient-to-br from-white/[0.06] to-white/[0.02] px-4 text-center text-[13px] leading-snug text-white/30 ${className}`}
    >
      {label}
    </div>
  )
}

export default ImageSlot
