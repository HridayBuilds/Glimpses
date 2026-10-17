import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { getUploadUrl, getJobStatus } from '../../lib/uploadApi'
import { getUploadUrlWithRetry } from '../../lib/uploadUrlRetry'
import { planUploadBatches, zipFilesInWorker } from '../../lib/uploadBatches'
import { pollUploadJobs } from '../../lib/uploadJobStatus'

const MAX_PHOTOS = 500

const PROCESS_STAGES = [
  { status: 'EXTRACTING', label: 'Extract' },
  { status: 'INDEXING', label: 'Index faces' },
  { status: 'MATCHING', label: 'Find matches' },
]
const FINISHED_STATES = ['SUCCESS', 'FAILED']

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

function ProgressRow({ label, value, percent, children }) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 text-[14px]">
        <span className="font-semibold text-white/90">{label}</span>
        <span className="shrink-0 font-mono text-[13px] tabular-nums text-[#FF9578]">{value}</span>
      </div>
      <div
        role="progressbar"
        aria-label={label}
        aria-valuenow={Math.round(percent)}
        aria-valuemin={0}
        aria-valuemax={100}
        className="mt-3 h-[8px] overflow-hidden rounded-full bg-white/[0.1]"
      >
        <div className="h-full rounded-full bg-[#FF7A59] transition-[width] duration-300 ease-out" style={{ width: `${percent}%` }} />
      </div>
      {children && <div className="mt-3 text-[13px] leading-[1.45] text-white/50">{children}</div>}
    </div>
  )
}

function UploadFlow() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)

  // idle | preparing | uploading | processing | error
  const [phase, setPhase] = useState('idle')
  const [pct, setPct] = useState(0)
  const [pickedLabel, setPickedLabel] = useState(null)
  const [jobIds, setJobIds] = useState([])
  const [uploadSession, setUploadSession] = useState(0)
  const [batchTotal, setBatchTotal] = useState(0)
  const [uploadedBatches, setUploadedBatches] = useState(0)
  const [currentBatchPct, setCurrentBatchPct] = useState(null)
  const [currentBatchStep, setCurrentBatchStep] = useState('preparing')
  const [errorDetail, setErrorDetail] = useState('')
  const [retryPending, setRetryPending] = useState(false)
  const resumeRef = useRef(null)
  const knownJobsRef = useRef({})

  const statusQueryKey = ['events', eventId, 'upload-session', uploadSession, 'status']
  const jobQuery = useQuery({
    queryKey: statusQueryKey,
    queryFn: async () => {
      const result = await pollUploadJobs(jobIds, (id) => getJobStatus(eventId, id), knownJobsRef.current)
      knownJobsRef.current = result.jobsById
      return result
    },
    enabled: phase !== 'idle' && jobIds.length > 0,
    refetchInterval: (query) => {
      const jobs = query.state.data?.jobsById ?? {}
      if (jobIds.every((id) => FINISHED_STATES.includes(jobs[id]?.status))) return false
      return fibonacciPollDelay(query.state.dataUpdateCount)
    },
  })

  const jobs = jobIds.map((id) => jobQuery.data?.jobsById[id]).filter(Boolean)
  const unreachableCount = jobQuery.data?.unreachableCount ?? 0
  const finishedJobs = jobs.filter((job) => FINISHED_STATES.includes(job.status))
  const allFinished = finishedJobs.length === jobIds.length && jobIds.length > 0
  const runningJobs = jobs.filter((job) => !FINISHED_STATES.includes(job.status))
  const status = allFinished
    ? jobs.every((job) => job.status === 'FAILED') ? 'FAILED' : 'SUCCESS'
    : runningJobs[0]?.status ?? 'CREATED'

  useEffect(() => {
    if (jobIds.length > 0) {
      queryClient.invalidateQueries({ queryKey: ['events', eventId, 'upload-session', uploadSession, 'status'] })
    }
  // A new uploaded batch has its own job ID; check it without discarding known results.
  }, [jobIds.length, uploadSession, eventId, queryClient])

  // A failed status request for one batch must not hide the other batch results.
  // Keep polling that batch while retaining successful responses and terminal jobs.
  // Matching is complete when a batch reports SUCCESS. Refresh gallery caches
  // as each batch finishes, even if later batches are still uploading.
  useEffect(() => {
    if (finishedJobs.length > 0) {
      queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
    }
  }, [finishedJobs.length, queryClient, eventId])

  const busy = phase === 'preparing' || phase === 'uploading' || phase === 'processing'

  const reset = () => {
    setPhase('idle')
    setPct(0)
    setPickedLabel(null)
    setJobIds([])
    setUploadSession((session) => session + 1)
    setBatchTotal(0)
    setUploadedBatches(0)
    setCurrentBatchPct(null)
    knownJobsRef.current = {}
    setCurrentBatchStep('preparing')
    setErrorDetail('')
    setRetryPending(false)
    resumeRef.current = null
  }

  const retryUpload = () => {
    const pending = resumeRef.current
    if (!pending) return reset()
    setErrorDetail('')
    setRetryPending(false)
    uploadBatches(pending.batches, pending.nextIndex, pending.ids)
  }

  const uploadOne = async (blob, progress) => {
    let jobId
    let uploadUrl
    try {
      ({ jobId, uploadUrl } = await getUploadUrlWithRetry(eventId, getUploadUrl))
    } catch (error) {
      if (!error.response || [408, 429, 500, 502, 503, 504].includes(error.response.status)) {
        throw new Error('UPLOAD_URL_UNAVAILABLE', { cause: error })
      }
      throw error
    }
    for (let attempt = 0; attempt < 3; attempt++) {
      const controller = new AbortController()
      let stalled = setTimeout(() => controller.abort(), 75000)
      let allBytesSent = false
      try {
        await axios.put(uploadUrl, blob, {
          headers: { 'Content-Type': 'application/zip' },
          signal: controller.signal,
          timeout: 600000,
          onUploadProgress: (event) => {
            clearTimeout(stalled)
            stalled = setTimeout(() => controller.abort(), 75000)
            if (event.total) {
              allBytesSent = event.loaded >= event.total
              progress(event.loaded / event.total)
            }
          },
        })
        return jobId
      } catch (error) {
        // A mobile connection can lose the response after S3 accepted the ZIP.
        // Check the exact job before repeating a PUT that would trigger ingestion twice.
        for (let check = 0; check < 3; check++) {
          try {
            await getJobStatus(eventId, jobId)
            return jobId
          } catch {
            if (check < 2) await new Promise((resolve) => setTimeout(resolve, 1500 * 2 ** check))
          }
        }
        if (!error.response && allBytesSent) {
          throw new Error('UPLOAD_UNCERTAIN')
        }
        if (attempt === 2 || (error.response && ![408, 429, 500, 502, 503, 504].includes(error.response.status))) throw error
        await new Promise((resolve) => setTimeout(resolve, 2000 * (attempt + 1)))
      } finally {
        clearTimeout(stalled)
      }
    }
  }

  const uploadBatches = async (batches, startAt = 0, completedIds = []) => {
    const ids = [...completedIds]
    let preparedNext = null
    setBatchTotal(batches.length)
    setUploadedBatches(ids.length)
    for (let index = startAt; index < batches.length; index++) {
      try {
        setPhase('preparing')
        setCurrentBatchStep('preparing')
        setCurrentBatchPct(0)
        const blob = preparedNext
          ? await preparedNext
          : await zipFilesInWorker(batches[index], setCurrentBatchPct)
        preparedNext = null
        setCurrentBatchStep('uploading')
        setCurrentBatchPct(0)
        // Prepare only one batch ahead. The network uploads remain sequential,
        // while ZIP work can use otherwise idle time during the current PUT.
        if (index + 1 < batches.length) {
          preparedNext = zipFilesInWorker(batches[index + 1], () => {})
          // Attach a handler immediately so a preparation failure cannot become
          // an unhandled rejection while the current PUT is still in flight.
          preparedNext.catch(() => {})
        }
        const id = await uploadOne(blob, (fraction) => {
          setCurrentBatchPct(Math.round(fraction * 100))
        })
        ids.push(id)
        setUploadedBatches(ids.length)
        setCurrentBatchPct(null)
        setJobIds([...ids])
        resumeRef.current = { batches, nextIndex: index + 1, ids }
      } catch (error) {
        preparedNext = null
        resumeRef.current = { batches, nextIndex: index, ids }
        setRetryPending(true)
        setErrorDetail(error.message === 'UPLOAD_UNCERTAIN'
          ? `${ids.length} of ${batches.length} batches confirmed. The next batch may have reached the server. Check the gallery before retrying it.`
          : error.message === 'UPLOAD_URL_UNAVAILABLE'
            ? `The upload service is temporarily unavailable. ${ids.length} of ${batches.length} batches uploaded; retry the remaining batches.`
          : `${ids.length} of ${batches.length} batches uploaded. The connection or photo preparation failed; retry the remaining photos.`)
        if (ids.length) queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
        setPhase('error')
        return
      }
    }
    resumeRef.current = null
    setCurrentBatchPct(null)
    setRetryPending(false)
    setPhase('processing')
  }

  const uploadZip = async (file) => {
    setPhase('uploading')
    setPct(0)
    try {
      const id = await uploadOne(file, (fraction) => setPct(Math.round(fraction * 100)))
      setJobIds([id])
      setPct(100)
      setPhase('processing')
    } catch {
      setErrorDetail('The ZIP upload did not finish. Check your connection and try again.')
      setPhase('error')
    }
  }

  const handleFiles = async (fileList) => {
    const files = Array.from(fileList)
    if (files.length === 0) return

    if (files.length > 1 && files.some((file) => /\.zip$/i.test(file.name))) {
      toast.error('Choose one ZIP archive or select photos, not both together.')
      return
    }

    if (files.length === 1 && /\.zip$/i.test(files[0].name)) {
      knownJobsRef.current = {}
      setUploadSession((session) => session + 1)
      setBatchTotal(0)
      setPickedLabel('1 zip archive selected')
      await uploadZip(files[0])
      return
    }

    if (files.length > MAX_PHOTOS) {
      toast.error(`Pick ${MAX_PHOTOS} photos or fewer, or bring your own ZIP for more.`)
      return
    }

    setPickedLabel(`${files.length} photo${files.length === 1 ? '' : 's'} selected`)
    knownJobsRef.current = {}
    setUploadSession((session) => session + 1)
    setJobIds([])
    setUploadedBatches(0)
    setPhase('preparing')
    setPct(0)
    setErrorDetail('')
    await uploadBatches(planUploadBatches(files))
  }

  const onInputChange = (e) => {
    handleFiles(e.target.files)
    e.target.value = ''
  }

  const title =
    phase === 'preparing'
      ? 'Adding your photos'
      : phase === 'uploading'
        ? 'Uploading'
        : phase === 'processing'
          ? status === 'SUCCESS'
            ? 'Photos added'
            : status === 'FAILED'
              ? 'Photos could not be processed'
            : 'Processing your photos'
          : phase === 'error'
            ? 'Something went wrong'
            : 'Add photos'

  const body =
    phase === 'error'
      ? errorDetail || "Nothing you've already added was lost. You can try again."
      : phase === 'processing' && status === 'SUCCESS'
        ? 'Your photos are ready in the gallery.'
        : phase === 'processing' && status === 'FAILED'
          ? 'The upload reached the server, but photo processing failed. Please try a smaller selection.'
        : phase === 'idle'
          ? 'Pick photos or a ZIP archive to add to this event.'
          : phase === 'processing'
            ? 'Upload complete. Processing continues if you leave this page.'
            : batchTotal
              ? 'Small batches make large uploads more reliable. Keep this page open until they finish uploading.'
              : 'Keep this page open until the ZIP finishes uploading.'

  const processingPct = batchTotal ? (finishedJobs.length / batchTotal) * 100 : jobIds.length ? (finishedJobs.length / jobIds.length) * 100 : 0
  const uploadPct = batchTotal ? phase === 'processing' ? 100 : currentBatchPct ?? 0 : phase === 'processing' ? 100 : pct
  const currentBatchNumber = Math.min(uploadedBatches + 1, batchTotal)
  const succeededCount = finishedJobs.reduce((total, job) => total + (job.succeededCount ?? 0), 0)
  const failedCount = finishedJobs.reduce((total, job) => total + (job.failedCount ?? 0), 0)
  const duplicateCount = finishedJobs.reduce((total, job) => total + (job.duplicateCount ?? 0), 0)
  const failedJobs = finishedJobs.filter((job) => job.status === 'FAILED').length
  const done = phase === 'processing' && allFinished
  const partial = done && (failedCount > 0 || failedJobs > 0)
  const stageCounts = Object.fromEntries(PROCESS_STAGES.map(({ status }) => [status, runningJobs.filter((job) => job.status === status).length]))

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

        {phase === 'idle' && (
          <button
            onClick={() => navigate(`/app/events/${eventId}/upload/drive`)}
            className="mb-4 w-full cursor-pointer rounded-2xl border border-white/15 bg-white/5 p-4 text-left transition-colors hover:bg-white/10"
          >
            <span className="block font-semibold">From Google Drive</span>
            <span className="mt-1 block text-sm text-white/55">Import photos from a public folder.</span>
          </button>
        )}

        {(busy || phase === 'error') && (
          <div className="overflow-hidden rounded-[26px] border border-white/[0.11] bg-[linear-gradient(145deg,rgba(255,255,255,0.085),rgba(255,255,255,0.025)_65%)] p-5 shadow-[0_20px_60px_rgba(0,0,0,0.18)] sm:p-6">
            {phase === 'error' ? (
              <div className="text-[15px] font-semibold tracking-[-0.008em] text-[#FF8A8A]">Upload failed</div>
            ) : (
              <div>
                <div className="mb-6 flex items-center justify-between gap-3 border-b border-white/[0.08] pb-5">
                  <div className="min-w-0">
                    <p className="text-[12px] font-semibold uppercase tracking-[0.1em] text-white/40">Photo transfer</p>
                    <p className="mt-1 truncate text-[18px] font-semibold tracking-[-0.02em]">{pickedLabel}</p>
                  </div>
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#FF7A59]/12 text-[#FF9578]" aria-hidden="true">↗</div>
                </div>

                <div className="relative pl-10">
                  <div className={`absolute left-0 top-0 flex h-7 w-7 items-center justify-center rounded-full text-[12px] font-bold ${phase === 'processing' ? 'bg-[#6FD8B0]/15 text-[#6FD8B0]' : 'bg-[#FF7A59] text-[#200C05]'}`} aria-hidden="true">
                    {phase === 'processing' ? '✓' : '1'}
                  </div>
                  <ProgressRow
                    label={phase === 'processing' ? 'Upload complete' : batchTotal ? `${currentBatchStep === 'preparing' ? 'Preparing' : 'Uploading'} batch ${currentBatchNumber} of ${batchTotal}` : 'Uploading ZIP'}
                    value={phase === 'processing' ? '100%' : `${Math.round(uploadPct)}%`}
                    percent={uploadPct}
                  >
                    {batchTotal
                      ? `${uploadedBatches} of ${batchTotal} batches uploaded`
                      : phase === 'processing' ? 'ZIP uploaded' : 'Sending your ZIP to storage'}
                  </ProgressRow>
                </div>

                <div className="relative mt-6 border-t border-white/[0.08] pt-6 pl-10">
                  <div className={`absolute left-0 top-6 flex h-7 w-7 items-center justify-center rounded-full text-[12px] font-bold ${jobIds.length ? 'bg-[#FF7A59]/15 text-[#FF9578]' : 'bg-white/[0.08] text-white/40'}`} aria-hidden="true">2</div>
                  <ProgressRow
                    label="Processing photos"
                    value={`${finishedJobs.length} of ${batchTotal || 1} finished`}
                    percent={processingPct}
                  >
                    {jobIds.length === 0
                      ? 'Starts as soon as a batch finishes uploading.'
                      : done
                        ? `${succeededCount} photos added${duplicateCount ? ` · ${duplicateCount} already in event` : ''}${failedCount ? ` · ${failedCount} failed` : ''}`
                        : <>
                            <div className="grid grid-cols-3 gap-1.5" aria-label="Processing stages">
                              {PROCESS_STAGES.map(({ status: stage, label }) => (
                                <div key={stage} className={`rounded-[10px] border px-2 py-2 text-center text-[11px] font-medium leading-tight ${stageCounts[stage] ? 'border-[#FF7A59]/30 bg-[#FF7A59]/10 text-[#FFAC96]' : 'border-white/[0.07] bg-white/[0.035] text-white/40'}`}>
                                  {label}
                                </div>
                              ))}
                            </div>
                            {runningJobs.some((job) => job.status === 'CREATED') && <p className="mt-2">Starting newly uploaded batches</p>}
                            {unreachableCount > 0 && <p className="mt-2">Retrying {unreachableCount} status {unreachableCount === 1 ? 'check' : 'checks'}</p>}
                            {succeededCount > 0 && <p className="mt-2">{succeededCount} photos added so far</p>}
                          </>}
                  </ProgressRow>
                </div>
              </div>
            )}
          </div>
        )}

        {!busy && <div className="mt-3 flex items-center gap-3 rounded-[14px] border border-dashed border-white/[0.14] bg-white/[0.04] p-4">
          <div className="min-w-0 flex-1">
            <div className="text-[14.5px] font-semibold tracking-[-0.008em]">{pickedLabel ?? 'No files chosen yet'}</div>
            <div className="mt-0.5 text-[13px] leading-[1.55] text-white/42">
              Photos or one ZIP archive.
            </div>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex-none cursor-pointer rounded-[10px] border border-white/[0.12] bg-white/[0.09] px-[13px] py-2.5 text-[14px] font-medium transition-transform duration-[90ms] ease-out active:scale-95"
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
        </div>}

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
                {partial
                  ? `${succeededCount} added · ${failedCount} failed${duplicateCount ? ` · ${duplicateCount} already in event` : ''}${failedJobs ? ` · ${failedJobs} batch${failedJobs === 1 ? '' : 'es'} did not complete` : ''}`
                  : `${succeededCount} added${duplicateCount ? ` · ${duplicateCount} already in event` : ''}`}
              </div>
              <p className="text-pretty text-[14.5px] leading-[1.6] text-white/70">
                {partial
                  ? "Nothing else in the batch was affected. You can try uploading those again from the original folder."
                  : duplicateCount
                    ? 'Photos already in this event were skipped, not counted as failures.'
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
            onClick={retryUpload}
            className="mt-3.5 w-full cursor-pointer rounded-xl border-none bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            {retryPending ? 'Retry remaining photos' : 'Try again'}
          </button>
        )}
      </div>
    </div>
  )
}

export default UploadFlow
