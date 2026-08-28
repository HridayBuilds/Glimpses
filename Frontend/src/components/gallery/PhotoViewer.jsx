import { useEffect, useState } from 'react'
import { motion, useMotionValue, useTransform, useDragControls, animate } from 'motion/react'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { getDownloadUrls, deletePhoto } from '../../lib/galleryApi'
import ConfirmDialog from '../common/ConfirmDialog'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function PhotoViewer({ eventId, photo, onClose, onPrev, onNext, hasPrev, hasNext }) {
  const dragControls = useDragControls()
  const queryClient = useQueryClient()
  const [downloading, setDownloading] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await deletePhoto(eventId, photo.photoID)
      queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
      toast.success('Photo deleted')
      onClose()
    } catch {
      toast.error('Something went wrong. Try again.')
    } finally {
      setDeleting(false)
      setConfirmingDelete(false)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const { downloadUrls } = await getDownloadUrls(eventId, [photo.photoID])
      const url = downloadUrls[0]?.downloadUrl
      if (!url) throw new Error('missing download url')
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = photo.filename || 'photo.jpg'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(blobUrl)
    } catch {
      toast.error('Something went wrong. Try again.')
    } finally {
      setDownloading(false)
    }
  }
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'ArrowLeft' && hasPrev) onPrev()
      else if (e.key === 'ArrowRight' && hasNext) onNext()
      else if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [hasPrev, hasNext, onPrev, onNext, onClose])

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
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="cursor-pointer rounded-[10px] border border-white/[0.12] bg-white/10 px-3 py-2 text-[14px] text-[#F5F5F7] transition-transform duration-[90ms] ease-out active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Download
            </button>
            <button
              onClick={() => setConfirmingDelete(true)}
              className="cursor-pointer rounded-[10px] border border-[rgba(255,89,89,0.28)] bg-[rgba(255,89,89,0.13)] px-3 py-2 text-[14px] text-[#FF8A8A] transition-transform duration-[90ms] ease-out active:scale-95"
            >
              Delete
            </button>
          </div>
        </div>

        <div
          onPointerDown={(e) => dragControls.start(e)}
          className="relative flex min-h-0 flex-1 flex-col items-center justify-center gap-1 overflow-y-auto px-2 pb-[26px] pt-2"
        >
          <img
            src={photo.photoUrl}
            alt={photo.filename}
            className="max-h-[62vh] w-auto max-w-full flex-none rounded-[6px] object-contain"
            draggable={false}
          />

          <div className="w-full px-4 pt-4 text-center">
            <div className="mb-1.5 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/34">
              Uploaded by
            </div>
            <div className="text-[16.5px] font-semibold leading-[1.5] tracking-[-0.012em]">
              {photo.uploaderDisplayName}
            </div>
            <div className="text-[14px] leading-[1.6] text-white/45">{photo.uploaderEmail}</div>
          </div>

          {hasPrev && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onPrev()
              }}
              className="absolute left-2 top-1/2 z-[3] flex h-9 w-9 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full border border-white/[0.12] bg-black/40 text-[17px] text-[#F5F5F7] backdrop-blur-md transition-transform duration-[90ms] ease-out active:scale-90"
            >
              ‹
            </button>
          )}
          {hasNext && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onNext()
              }}
              className="absolute right-2 top-1/2 z-[3] flex h-9 w-9 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full border border-white/[0.12] bg-black/40 text-[17px] text-[#F5F5F7] backdrop-blur-md transition-transform duration-[90ms] ease-out active:scale-90"
            >
              ›
            </button>
          )}
        </div>
      </motion.div>

      <ConfirmDialog
        open={confirmingDelete}
        title="Delete this photo?"
        body="It is removed from the event for everyone. There is no trash to recover it from."
        cta="Delete"
        danger
        onCancel={() => setConfirmingDelete(false)}
        onConfirm={deleting ? undefined : handleDelete}
      />
    </motion.div>
  )
}

export default PhotoViewer
