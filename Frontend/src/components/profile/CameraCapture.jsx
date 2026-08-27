import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'

function cameraErrorMessage(err) {
  if (err?.name === 'NotFoundError' || err?.name === 'OverconstrainedError') {
    return 'No camera found on this device.'
  }
  if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
    return 'Camera access was denied.'
  }
  return 'Could not access your camera.'
}

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
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
        setReady(true)
      } catch (err) {
        toast.error(cameraErrorMessage(err))
        onCancel()
      }
    }

    startCamera()

    return () => {
      cancelled = true
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
      <video ref={videoRef} autoPlay playsInline muted className="flex-1 w-full object-cover" />
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
