import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { cameraErrorMessage } from '../../lib/camera'
import { decodeQRFromImageData } from '../../lib/qr'

function QRScanner({ open, onCancel, onDecode }) {
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const canvasRef = useRef(null)
  const rafRef = useRef(null)
  const [ready, setReady] = useState(false)

  if (!canvasRef.current) canvasRef.current = document.createElement('canvas')

  useEffect(() => {
    if (!open) return

    let cancelled = false

    function scanLoop() {
      const video = videoRef.current
      if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        rafRef.current = requestAnimationFrame(scanLoop)
        return
      }
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      const text = decodeQRFromImageData(ctx.getImageData(0, 0, canvas.width, canvas.height))
      if (text) {
        onDecode(text)
        return
      }
      rafRef.current = requestAnimationFrame(scanLoop)
    }

    async function startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        toast.error('This device does not support camera capture.')
        onCancel()
        return
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
        setReady(true)
        rafRef.current = requestAnimationFrame(scanLoop)
      } catch (err) {
        toast.error(cameraErrorMessage(err))
        onCancel()
      }
    }

    startCamera()

    return () => {
      cancelled = true
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      streamRef.current?.getTracks().forEach((track) => track.stop())
      streamRef.current = null
      setReady(false)
    }
  }, [open, onCancel, onDecode])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[95] flex flex-col bg-black">
      <div className="relative min-h-0 flex-1 overflow-hidden">
        <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-cover" />
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="h-[220px] w-[220px] rounded-2xl border-2 border-[#FF7A59]" />
        </div>
        <div className="pointer-events-none absolute inset-x-0 bottom-4 text-center text-[13.5px] font-medium text-white/80">
          {ready ? 'Point your camera at the QR code' : 'Starting camera…'}
        </div>
      </div>
      <div className="flex items-center justify-center bg-black px-6 py-6">
        <button
          onClick={onCancel}
          className="rounded-xl border border-white/10 bg-white/[0.07] px-6 py-3.5 text-[15px] font-medium text-[#F5F5F7]"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

export default QRScanner
