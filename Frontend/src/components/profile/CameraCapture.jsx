import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { cameraErrorMessage } from '../../lib/camera'

function CameraCapture({ open, onCancel, onCapture }) {
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!open) return

    let cancelled = false

    async function startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        toast.error('This device does not support camera capture.')
        onCancel()
        return
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 960 }, aspectRatio: { ideal: 3 / 4 } },
        })
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        streamRef.current = stream
        const video = videoRef.current
        if (video) {
          video.srcObject = stream
          // ready only once a real frame is available, so the shutter never fires on a black frame
          video.onloadedmetadata = () => {
            video.play().catch(() => {})
            if (!cancelled) setReady(true)
          }
        }
      } catch (err) {
        toast.error(cameraErrorMessage(err))
        onCancel()
      }
    }

    startCamera()

    return () => {
      cancelled = true
      if (videoRef.current) videoRef.current.onloadedmetadata = null
      streamRef.current?.getTracks().forEach((track) => track.stop())
      streamRef.current = null
      setReady(false)
    }
  }, [open, onCancel])

  if (!open) return null

  const capture = () => {
    const video = videoRef.current
    if (!video) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (!blob) return
      onCapture(new File([blob], `selfie-${Date.now()}.jpg`, { type: 'image/jpeg' }))
    }, 'image/jpeg')
  }

  return (
    <div className="fixed inset-0 z-[95] flex flex-col bg-black">
      <div className="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden bg-black">
        {/* Fixed 3:4 frame, capped to a normal size regardless of viewport - width drives
            the size (up to max-w), height follows from the aspect-ratio, max-h is only a
            safety cap for short viewports. Setting both h-full and w-full here previously
            made width AND height simultaneously explicit, which overrides aspect-ratio
            entirely (it only computes a dimension when one side is auto) - that's what let
            the frame balloon to fill the whole screen on desktop. */}
        <div
          className="relative w-full max-w-[380px] max-h-[70dvh] overflow-hidden"
          style={{ aspectRatio: '3 / 4' }}
        >
          <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-cover" />
          <div
            className="pointer-events-none absolute left-1/2 top-[42%] w-[68%] -translate-x-1/2 -translate-y-1/2 rounded-[50%] border-2 border-[#FF7A59]"
            style={{ aspectRatio: '3 / 4', boxShadow: '0 0 0 9999px rgba(0,0,0,0.55)' }}
          />
        </div>
        <div className="pointer-events-none absolute left-0 right-0 bottom-4 text-center text-[13.5px] font-medium text-white/80">
          Fit your face inside the outline
        </div>
      </div>
      <div className="flex items-center justify-between gap-4 bg-black px-6 py-6">
        <button
          onClick={onCancel}
          className="rounded-xl border border-white/10 bg-white/[0.07] px-5 py-3.5 text-[15px] font-medium text-[#F5F5F7]"
        >
          Cancel
        </button>
        <button
          onClick={capture}
          disabled={!ready}
          className="rounded-full bg-[#FF7A59] p-1 disabled:opacity-40"
        >
          <span className="block h-[62px] w-[62px] rounded-full border-4 border-[#200C05]" />
        </button>
        <div className="w-[73px]" />
      </div>
    </div>
  )
}

export default CameraCapture
