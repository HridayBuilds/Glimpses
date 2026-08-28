import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import JSZip from 'jszip'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { getUploadUrl, getJobStatus } from '../../lib/uploadApi'

const MAX_PHOTOS = 500

const STAGE_PCT = { CREATED: 10, EXTRACTING: 35, INDEXING: 65, MATCHING: 85, SUCCESS: 100 }
const STAGE_LABEL = { CREATED: 'Starting', EXTRACTING: 'Extracting', INDEXING: 'Indexing faces', MATCHING: 'Matching attendees' }

// Fibonacci-spaced polling: quick checks early (a small batch may finish in
// seconds) backing off as the job runs longer (big batches take minutes), so
// we're not hammering the API with a fixed-interval poll for the whole job.
const POLL_BASE_MS = 1500
const POLL_MAX_MS = 20000

function fibonacciPollDelay(pollCount) {
  let a = 1
  let b = 1
  for (let i = 0; i < pollCount; i++) {
    ;[a, b] = [b, a + b]
  }
  return Math.min(a * POLL_BASE_MS, POLL_MAX_MS)
}

function UploadFlow() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)

  // idle | zipping | uploading | processing | error
  const [phase, setPhase] = useState('idle')
  const [pct, setPct] = useState(0)
  const [pickedLabel, setPickedLabel] = useState(null)
  const [jobId, setJobId] = useState(null)

  const jobQuery = useQuery({
    queryKey: ['events', eventId, 'jobs', jobId, 'status'],
    queryFn: () => getJobStatus(eventId, jobId),
    enabled: phase === 'processing' && !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'SUCCESS' || status === 'FAILED') return false
      return fibonacciPollDelay(query.state.dataUpdateCount)
    },
  })

  const status = jobQuery.data?.status

  // Only a genuine terminal FAILED status ends the job. A transient fetch error
  // (502, brief network blip) must NOT flip this to 'error' - the backend job is
  // still running regardless of whether polling can currently reach it, and killing
  // 'processing' here would disable the query (enabled: phase === 'processing') and
  // stop polling for good, even though the job goes on to succeed on its own.
  useEffect(() => {
    if (phase === 'processing' && status === 'FAILED') {
      setPhase('error')
    }
  }, [phase, status])

  // Matching already finished server-side by the time a job reports SUCCESS — the
  // gallery just needs its cached photo lists invalidated so "Photos of me" reflects
  // the new matches instead of the pre-upload snapshot it had cached.
  useEffect(() => {
    if (phase === 'processing' && status === 'SUCCESS') {
      queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
    }
  }, [phase, status, queryClient, eventId])

  const busy = phase === 'zipping' || phase === 'uploading' || phase === 'processing'

  const reset = () => {
    setPhase('idle')
    setPct(0)
    setPickedLabel(null)
    setJobId(null)
  }

  const runUpload = async (blob, contentType) => {
    setPhase('uploading')
    setPct(0)
    try {
      const { jobId: newJobId, uploadUrl } = await getUploadUrl(eventId)
      await axios.put(uploadUrl, blob, {
        headers: { 'Content-Type': contentType },
        onUploadProgress: (e) => {
          if (e.total) setPct(Math.round((e.loaded / e.total) * 100))
        },
      })
      setJobId(newJobId)
      setPct(STAGE_PCT.CREATED)
      setPhase('processing')
    } catch {
      setPhase('error')
    }
  }

  const handleFiles = async (fileList) => {
    const files = Array.from(fileList)
    if (files.length === 0) return

    if (files.length === 1 && /\.zip$/i.test(files[0].name)) {
      setPickedLabel('1 zip archive selected')
      await runUpload(files[0], 'application/zip')
      return
    }

    if (files.length > MAX_PHOTOS) {
      toast.error(`Pick ${MAX_PHOTOS} photos or fewer, or bring your own ZIP for more.`)
      return
    }

    setPickedLabel(`${files.length} photo${files.length === 1 ? '' : 's'} selected`)
    setPhase('zipping')
    setPct(0)
    try {
      const zip = new JSZip()
      files.forEach((f) => zip.file(f.name, f))
      const blob = await zip.generateAsync({ type: 'blob' }, (meta) => setPct(Math.round(meta.percent)))
      await runUpload(blob, 'application/zip')
    } catch {
      setPhase('error')
    }
  }

  const onInputChange = (e) => {
    handleFiles(e.target.files)
    e.target.value = ''
  }

  const title =
    phase === 'zipping'
      ? 'Packing your photos'
      : phase === 'uploading'
        ? 'Uploading'
        : phase === 'processing'
          ? status === 'SUCCESS'
            ? 'Photos added'
            : 'Adding photos'
          : phase === 'error'
            ? 'Something went wrong'
            : 'Add photos'

  const body =
    phase === 'error'
      ? "Nothing you've already added was lost. You can try again."
      : phase === 'processing' && status === 'SUCCESS'
        ? "Matching runs on the new photos automatically. There's nothing else you need to do."
        : phase === 'idle'
          ? 'Pick photos or a ZIP archive to add to this event.'
          : "Your photos are uploading together. Faces are matched as each one lands, so you'll start seeing results before the upload finishes."

  const statusLabel =
    phase === 'zipping' ? 'Packing' : phase === 'uploading' ? 'Uploading' : phase === 'processing' ? (STAGE_LABEL[status] ?? 'Starting') : ''

  const barPct = phase === 'processing' ? (STAGE_PCT[status] ?? pct) : pct

  const succeededCount = jobQuery.data?.succeededCount ?? 0
  const failedCount = jobQuery.data?.failedCount ?? 0
  const done = phase === 'processing' && status === 'SUCCESS'
  const partial = done && failedCount > 0

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 flex items-center gap-3.5 bg-[rgba(10,10,12,0.72)] px-5 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <button
          onClick={() => navigate(`/app/events/${eventId}`)}
          className="cursor-pointer border-none bg-transparent p-0.5 text-[16px] text-[#FF7A59]"
        >
          ‹ Gallery
        </button>
        <div className="text-[16px] font-semibold tracking-[-0.01em]">Adding photos</div>
      </div>

      <div className="mx-auto max-w-[520px] px-5 pb-[60px] pt-6">
        <h1 className="mb-2 text-[30px] font-bold leading-[1.1] tracking-[-0.024em]">{title}</h1>
        <p className="mb-[26px] text-pretty text-[16px] leading-[1.55] text-white/55">{body}</p>

        {(busy || phase === 'error') && (
          <div className="rounded-[18px] border border-white/[0.08] bg-white/[0.05] p-5">
            {phase === 'error' ? (
              <div className="text-[15px] font-semibold tracking-[-0.008em] text-[#FF8A8A]">Upload failed</div>
            ) : (
              <>
                <div className="mb-3.5 flex items-baseline justify-between">
                  <div className="text-[15px] font-semibold tracking-[-0.008em]">
                    {done ? 'Complete' : statusLabel}
                  </div>
                  <div className="font-mono text-[15px] font-semibold tabular-nums text-[#FF9578]">
                    {Math.min(100, barPct)}%
                  </div>
                </div>
                <div className="h-[7px] overflow-hidden rounded-full bg-white/[0.09]">
                  <div
                    className="h-full rounded-full bg-[#FF7A59] transition-[width] duration-300 ease-out"
                    style={{ width: `${Math.min(100, barPct)}%` }}
                  />
                </div>
                <div className="mt-3 text-pretty text-[13.5px] leading-[1.6] text-white/42">
                  {phase === 'processing'
                    ? "You can close this tab. The upload will finish on its own, and your photos will be in the gallery when you return."
                    : "Keep this tab open until the upload finishes - closing it now will cancel it before it reaches the server."}
                </div>
              </>
            )}
          </div>
        )}

        <div className="mt-3 flex items-center gap-3 rounded-[14px] border border-dashed border-white/[0.14] bg-white/[0.04] p-4">
          <div className="min-w-0 flex-1">
            <div className="text-[14.5px] font-semibold tracking-[-0.008em]">{pickedLabel ?? 'No files chosen yet'}</div>
            <div className="mt-0.5 text-[13px] leading-[1.55] text-white/42">
              Photos or a ZIP archive. Multiple photos are packed into one archive on your device before sending.
            </div>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={busy}
            className="flex-none cursor-pointer rounded-[10px] border border-white/[0.12] bg-white/[0.09] px-[13px] py-2.5 text-[14px] font-medium transition-transform duration-[90ms] ease-out active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Choose files
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.zip,application/zip"
            onChange={onInputChange}
            className="hidden"
          />
        </div>

        {done && (
          <div className="mt-3.5">
            <div
              className="rounded-2xl border p-[18px]"
              style={{
                background: partial ? 'rgba(224,193,92,0.09)' : 'rgba(111,216,176,0.09)',
                borderColor: partial ? 'rgba(224,193,92,0.3)' : 'rgba(111,216,176,0.28)',
              }}
            >
              <div
                className="mb-1.5 text-[16px] font-semibold tracking-[-0.01em]"
                style={{ color: partial ? '#E8CE74' : '#6FD8B0' }}
              >
                {partial ? `${succeededCount} added, ${failedCount} could not be processed` : `${succeededCount} added`}
              </div>
              <p className="text-pretty text-[14.5px] leading-[1.6] text-white/70">
                {partial
                  ? "Nothing else in the batch was affected. You can try uploading those again from the original folder."
                  : "Matching runs on the new photos automatically. There's nothing else you need to do."}
              </p>
            </div>
            <div className="mt-3 flex gap-2.5">
              <button
                onClick={reset}
                className="flex-1 cursor-pointer rounded-xl border border-white/[0.1] bg-white/[0.07] py-[15px] text-[15px] font-medium transition-transform duration-100 ease-out active:scale-[0.975]"
              >
                Add more
              </button>
              <button
                onClick={() => navigate(`/app/events/${eventId}`)}
                className="flex-1 cursor-pointer rounded-xl border-none bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
              >
                See the gallery
              </button>
            </div>
          </div>
        )}

        {phase === 'error' && (
          <button
            onClick={reset}
            className="mt-3.5 w-full cursor-pointer rounded-xl border-none bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  )
}

export default UploadFlow
