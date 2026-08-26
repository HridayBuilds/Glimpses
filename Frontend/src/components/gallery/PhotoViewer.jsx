import { motion, useMotionValue, useTransform, useDragControls, animate } from 'motion/react'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function PhotoViewer({ photo, onClose }) {
  const dragControls = useDragControls()
  const y = useMotionValue(0)
  const scale = useTransform(y, (v) => Math.max(0.86, 1 - Math.abs(v) / 2600))
  const radius = useTransform(y, (v) => Math.min(28, Math.abs(v) / 6))
  const backdropOpacity = useTransform(y, (v) => Math.max(0.4, 1 - Math.abs(v) / 700))

  const handleDragEnd = (_, info) => {
    const projected = info.offset.y + info.velocity.y * 0.35
    if (projected > 150) {
      animate(y, window.innerHeight, {
        type: 'spring',
        velocity: Math.max(info.velocity.y, 600),
        stiffness: 300,
        damping: 30,
        onComplete: onClose,
      })
      return
    }
    animate(y, 0, { type: 'spring', velocity: info.velocity.y, stiffness: 350, damping: 32 })
  }

  return (
    <motion.div
      style={{ background: `rgba(4,4,6,${backdropOpacity})` }}
      className="fixed inset-0 z-[90] flex items-stretch justify-center"
    >
      <motion.div
        drag="y"
        dragListener={false}
        dragControls={dragControls}
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={{ top: 0.55, bottom: 1 }}
        onDragEnd={handleDragEnd}
        style={{ y, scale, borderRadius: radius }}
        className="flex w-full max-w-[820px] touch-none flex-col overflow-hidden bg-[#08080A] will-change-transform"
      >
        <div className="relative z-[2] flex items-center justify-between bg-[rgba(10,10,12,0.6)] px-4 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
          <button
            onClick={onClose}
            className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/[0.12] bg-white/10 text-[15px] text-[#F5F5F7] transition-transform duration-[90ms] ease-out active:scale-90"
          >
            ✕
          </button>
          <div className="text-[13.5px] tabular-nums text-white/50">{formatDate(photo.uploadedAt)}</div>
          <div className="w-8" />
        </div>

        <div
          onPointerDown={(e) => dragControls.start(e)}
          className="flex min-h-0 flex-1 items-center justify-center overflow-hidden px-2 pt-2"
        >
          <img
            src={photo.photoUrl}
            alt={photo.filename}
            className="h-full w-auto max-w-full rounded-[6px] object-contain"
            draggable={false}
          />
        </div>

        <div
          onPointerDown={(e) => dragControls.start(e)}
          className="px-[18px] pb-[26px] pt-4 text-center"
        >
          <div className="mb-1.5 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/34">
            Uploaded by
          </div>
          <div className="text-[16.5px] font-semibold leading-[1.5] tracking-[-0.012em]">
            {photo.uploaderDisplayName}
          </div>
          <div className="text-[14px] leading-[1.6] text-white/45">{photo.uploaderEmail}</div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default PhotoViewer
