import { useCallback, useEffect, useRef, useState } from 'react'
import { motion, useMotionValue, useTransform, useDragControls, animate } from 'motion/react'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { getDownloadUrls, deletePhoto } from '../../lib/galleryApi'
import { removePhotosFromCache } from '../../lib/galleryCache'
import { useAuth } from '../../context/AuthContext'
import ConfirmDialog from '../common/ConfirmDialog'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function PhotoViewer({ eventId, photo, onClose, onPrev, onNext, hasPrev, hasNext, isOrganizer }) {
  const dragControls = useDragControls()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [downloading, setDownloading] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const canDelete = isOrganizer || photo.uploaderID === user?.sub

  const requestDelete = () => {
    if (!canDelete) {
      toast.error(
        <div>
          <div className="font-semibold">Not your photo to delete</div>
          <div className="mt-0.5 text-[13px] text-black/60">
            You didn't upload this one — ask {photo.uploaderDisplayName || 'the uploader'} or your event organizer to remove it.
          </div>
        </div>,
        { duration: 5000 },
      )
      return
    }
    setConfirmingDelete(true)
  }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await deletePhoto(eventId, photo.photoID)
      removePhotosFromCache(queryClient, eventId, [photo.photoID])
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

  const MIN_ZOOM = 1
  const MAX_ZOOM = 4
  const DOUBLE_TAP_ZOOM = 2.5
  const SWIPE_THRESHOLD = 60

  const imgScale = useMotionValue(1)
  const imgX = useMotionValue(0)
  const imgY = useMotionValue(0)
  const gestureRef = useRef({})
  const imgRef = useRef(null)

  useEffect(() => {
    imgScale.set(1)
    imgX.set(0)
    imgY.set(0)
  }, [photo.photoID, imgScale, imgX, imgY])

  const touchDistance = (touches) => {
    const [a, b] = touches
    return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY)
  }

  const handleImageTouchStart = useCallback((e) => {
    if (e.touches.length === 2) {
      gestureRef.current = {
        mode: 'pinch',
        startDistance: touchDistance(e.touches),
        startScale: imgScale.get(),
      }
      return
    }
    if (e.touches.length !== 1) return

    const touch = e.touches[0]
    const now = Date.now()
    const lastTap = gestureRef.current.lastTap
    const isDoubleTap =
      lastTap && now - lastTap.time < 300 && Math.abs(touch.clientX - lastTap.x) < 30 && Math.abs(touch.clientY - lastTap.y) < 30

    if (isDoubleTap) {
      const next = imgScale.get() > 1 ? 1 : DOUBLE_TAP_ZOOM
      animate(imgScale, next, { type: 'spring', stiffness: 300, damping: 30 })
      if (next === 1) {
        animate(imgX, 0, { type: 'spring', stiffness: 300, damping: 30 })
        animate(imgY, 0, { type: 'spring', stiffness: 300, damping: 30 })
      }
      gestureRef.current = { mode: null }
      return
    }

    gestureRef.current = {
      mode: imgScale.get() > 1 ? 'pan' : 'swipe',
      startX: touch.clientX,
      startY: touch.clientY,
      startOffsetX: imgX.get(),
      startOffsetY: imgY.get(),
      lastTap: { time: now, x: touch.clientX, y: touch.clientY },
    }
  }, [imgScale, imgX, imgY])

  const handleImageTouchMove = useCallback((e) => {
    const state = gestureRef.current
    if (state.mode === 'pinch' && e.touches.length === 2) {
      e.preventDefault()
      const newDistance = touchDistance(e.touches)
      imgScale.set(Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, state.startScale * (newDistance / state.startDistance))))
    } else if (state.mode === 'pan' && e.touches.length === 1) {
      e.preventDefault()
      const touch = e.touches[0]
      imgX.set(state.startOffsetX + (touch.clientX - state.startX))
      imgY.set(state.startOffsetY + (touch.clientY - state.startY))
    } else if (state.mode === 'swipe' && e.touches.length === 1) {
      const touch = e.touches[0]
      const deltaX = touch.clientX - state.startX
      const deltaY = touch.clientY - state.startY
      if (Math.abs(deltaX) > Math.abs(deltaY)) e.stopPropagation()
    }
  }, [imgScale, imgX, imgY])

  const handleImageTouchEnd = useCallback((e) => {
    const state = gestureRef.current
    if (state.mode === 'swipe') {
      const touch = e.changedTouches[0]
      const deltaX = touch.clientX - state.startX
      const deltaY = touch.clientY - state.startY
      if (Math.abs(deltaX) > SWIPE_THRESHOLD && Math.abs(deltaX) > Math.abs(deltaY) * 1.5) {
        if (deltaX > 0 && hasPrev) onPrev()
        else if (deltaX < 0 && hasNext) onNext()
      }
    }
    if (imgScale.get() <= 1) {
      imgX.set(0)
      imgY.set(0)
    }
    gestureRef.current = { lastTap: state.lastTap }
  }, [hasPrev, hasNext, onPrev, onNext, imgScale, imgX, imgY])

  useEffect(() => {
    const el = imgRef.current
    if (!el) return
    el.addEventListener('touchstart', handleImageTouchStart, { passive: true })
    el.addEventListener('touchmove', handleImageTouchMove, { passive: false })
    el.addEventListener('touchend', handleImageTouchEnd, { passive: true })
    return () => {
      el.removeEventListener('touchstart', handleImageTouchStart)
      el.removeEventListener('touchmove', handleImageTouchMove)
      el.removeEventListener('touchend', handleImageTouchEnd)
    }
  }, [handleImageTouchStart, handleImageTouchMove, handleImageTouchEnd])

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
              onClick={requestDelete}
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
          <motion.img
            ref={imgRef}
            src={photo.photoUrl}
            alt={photo.filename}
            onPointerDown={(e) => e.stopPropagation()}
            style={{ x: imgX, y: imgY, scale: imgScale, touchAction: 'none' }}
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
