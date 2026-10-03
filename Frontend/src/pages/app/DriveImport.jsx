import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getJobStatus, importDriveFolder } from '../../lib/uploadApi'

const LABELS = {
  CHECKING: 'Checking public access', DOWNLOADING: 'Downloading photos',
  EXTRACTING: 'Processing photos', INDEXING: 'Indexing faces', MATCHING: 'Matching attendees',
  SUCCESS: 'Import complete', FAILED: 'Import could not finish',
}

const STAGES = [
  { label: 'Access', detail: 'Checking the folder link' },
  { label: 'Transfer', detail: 'Moving photos into Glimpses' },
  { label: 'Prepare', detail: 'Processing and indexing photos' },
  { label: 'Match', detail: 'Finding photos of attendees' },
]

const STAGE_INDEX = { CHECKING: 0, DOWNLOADING: 1, EXTRACTING: 2, INDEXING: 2, MATCHING: 3, SUCCESS: 4 }

export default function DriveImport() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const [search, setSearch] = useSearchParams()
  const jobId = search.get('job')
  const [folderUrl, setFolderUrl] = useState('')
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')
  const request = useRef(null)
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: ['events', eventId, 'jobs', jobId, 'status'],
    queryFn: () => getJobStatus(eventId, jobId),
    enabled: !!jobId,
    refetchInterval: (state) => ['SUCCESS', 'FAILED'].includes(state.state.data?.status) ? false : 8000,
  })
  const job = query.data
  const finished = ['SUCCESS', 'FAILED'].includes(job?.status)
  const busy = starting || (!!jobId && !finished)
  const stageIndex = STAGE_INDEX[job?.status] ?? 0
  const discovered = Math.max(0, job?.totalCount || 0)
  const downloaded = Math.max(0, job?.downloadedCount || 0)
  const downloadFailed = Math.max(0, job?.downloadFailedCount || 0)
  const transferred = Math.min(discovered, downloaded + downloadFailed)
  const transferPercent = discovered ? Math.round((transferred / discovered) * 100) : 0
  const skippedFolders = job?.skippedFolders || 0
  const skippedFiles = job?.skippedCount || 0

  useEffect(() => {
    if (finished) queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
  }, [finished, eventId, queryClient])

  async function start(event) {
    event.preventDefault()
    if (starting) return
    setStarting(true)
    setError('')
    if (!request.current || request.current.url !== folderUrl.trim()) {
      request.current = { url: folderUrl.trim(), id: crypto.randomUUID() }
    }
    try {
      const result = await importDriveFolder(eventId, request.current.url, request.current.id)
      setSearch({ job: result.jobId })
    } catch (failure) {
      setError(failure.response?.data?.message || 'We could not start the import. Please try again.')
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="min-h-svh bg-[#08080A] text-[#F5F5F7]">
      <div className="sticky top-0 flex items-center gap-4 bg-[#0A0A0C]/90 px-5 py-4 backdrop-blur-xl">
        <button onClick={() => navigate(`/app/events/${eventId}/upload`)} className="cursor-pointer text-[#FF7A59]">‹ Add photos</button>
        <span className="font-semibold">From Google Drive</span>
      </div>
      <main className="mx-auto max-w-[520px] px-5 pb-16 pt-7">
        <h1 className="text-3xl font-bold tracking-tight">{jobId ? 'Bringing your photos in' : 'Import your photos'}</h1>
        {!jobId && <>
          <p className="mt-3 text-white/60">Paste a public Google Drive folder link. Only photos directly inside that folder are imported.</p>
          <ol className="my-6 list-decimal space-y-2 rounded-2xl border border-white/10 bg-white/5 py-5 pl-10 pr-5 text-sm leading-relaxed text-white/75">
            <li>Open the folder in Google Drive and select Share.</li>
            <li>Set General access to <strong>Anyone with the link</strong>.</li>
            <li>Keep Viewer access, allow downloads, and select Copy link.</li>
          </ol>
          <p className="mb-5 text-sm text-white/50">Private folders, individual file links, and ZIP links are not supported. Subfolders, shortcuts, and non-photo files are skipped. Keep the folder publicly accessible until the import finishes.</p>
        </>}
        {!jobId && (
          <form onSubmit={start}>
            <label htmlFor="drive-folder" className="mb-2 block text-sm font-medium">Google Drive folder link</label>
            <input id="drive-folder" type="url" required value={folderUrl} disabled={busy}
              onChange={(event) => setFolderUrl(event.target.value)}
              placeholder="https://drive.google.com/drive/folders/..."
              className="w-full rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-base outline-none focus:border-[#FF7A59]" />
            <button type="submit" disabled={busy || !folderUrl.trim()}
              className="mt-4 w-full cursor-pointer rounded-xl bg-[#FF7A59] px-4 py-3 font-semibold text-[#200C05] disabled:opacity-50">
              {starting ? 'Starting import…' : 'Import photos'}
            </button>
          </form>
        )}
        {error && <p role="alert" className="mt-4 text-sm text-[#FF8A8A]">{error}</p>}
        {jobId && (
          <section aria-live="polite" className="mt-7 overflow-hidden rounded-[22px] border border-white/10 bg-[#17171A]">
            <div className="border-b border-white/[0.07] bg-[radial-gradient(ellipse_at_top_right,rgba(255,122,89,0.18),transparent_65%)] px-5 py-6">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#FF9D84]">Google Drive import</p>
              <h2 className="mt-2 text-[21px] font-semibold tracking-tight">{LABELS[job?.status] || 'Starting import'}</h2>
              {job?.folderName && <p className="mt-1 break-words text-sm text-white/55">{job.folderName}</p>}
            </div>

            <div className="p-5">
              {job?.status !== 'FAILED' && (
                <ol aria-label="Import stages" className="grid grid-cols-4 gap-2">
                  {STAGES.map((stage, index) => (
                    <li key={stage.label} className="min-w-0">
                      <div className={`mb-2 h-1.5 rounded-full ${index < stageIndex ? 'bg-[#FF7A59]' : index === stageIndex ? 'bg-[#FF7A59]/60 animate-pulse' : 'bg-white/10'}`} />
                      <p className={`text-[11px] font-semibold ${index <= stageIndex ? 'text-white/85' : 'text-white/35'}`}>{stage.label}</p>
                    </li>
                  ))}
                </ol>
              )}

              {job?.status === 'DOWNLOADING' && (
                <div className="mt-7">
                  <div className="flex items-end justify-between gap-3">
                    <div>
                      <p className="text-3xl font-semibold tabular-nums tracking-tight">{downloaded}<span className="ml-2 text-base font-normal text-white/45">received</span></p>
                      <p className="mt-1 text-sm text-white/55">{discovered} photo{discovered === 1 ? '' : 's'} found so far</p>
                    </div>
                    <span className="text-sm tabular-nums text-white/45">{Math.max(0, discovered - transferred)} remaining from those found</span>
                  </div>
                  <div role="progressbar" aria-label="Transfer of photos found so far" aria-valuemin={0} aria-valuemax={discovered || 1} aria-valuenow={transferred} className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                    <div className="h-full rounded-full bg-[#FF7A59] transition-[width] duration-700" style={{ width: `${transferPercent}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-white/40">More photos may be found as the folder is scanned.</p>
                  {downloadFailed > 0 && <p className="mt-3 text-sm text-[#FFAA92]">{downloadFailed} could not be downloaded</p>}
                </div>
              )}

              {['EXTRACTING', 'INDEXING', 'MATCHING'].includes(job?.status) && (
                <div className="mt-7 rounded-xl border border-white/[0.07] bg-white/[0.04] px-4 py-4">
                  <p className="text-lg font-semibold tabular-nums">{downloaded} photo{downloaded === 1 ? '' : 's'} received</p>
                  <p className="mt-1 text-sm text-white/55">{STAGES[stageIndex].detail}. This stage does not report a per-photo percentage.</p>
                </div>
              )}

              {job?.status === 'SUCCESS' && (
                <div className="mt-7 grid grid-cols-3 gap-2 text-center">
                  {[[job.succeededCount, 'Added'], [job.duplicateCount || 0, 'Duplicates'], [job.failedCount, 'Failed']].map(([count, label]) => (
                    <div key={label} className="rounded-xl bg-white/[0.05] px-2 py-4">
                      <p className="text-2xl font-semibold tabular-nums">{count}</p>
                      <p className="mt-1 text-xs text-white/50">{label}</p>
                    </div>
                  ))}
                </div>
              )}

              {job?.status === 'FAILED' && <p role="alert" className="mt-4 text-sm text-[#FF8A8A]">{job.errorMessage || 'The import could not finish. Please try again.'}</p>}
              {(skippedFolders > 0 || skippedFiles > 0) && <p className="mt-5 text-sm text-white/45">{[skippedFolders > 0 && `${skippedFolders} subfolder${skippedFolders === 1 ? '' : 's'}`, skippedFiles > 0 && `${skippedFiles} other file${skippedFiles === 1 ? '' : 's'}`].filter(Boolean).join(' and ')} skipped.</p>}
              {query.isError && <p className="mt-4 text-sm text-white/60">Waiting for a status update. We will keep checking.</p>}
              {!finished && <p className="mt-7 border-t border-white/[0.07] pt-4 text-sm leading-relaxed text-white/45">You can close this tab. The import continues in the background; return to this page to check progress.</p>}
            </div>
          </section>
        )}
        {finished && <div className="mt-5 flex gap-3">
          <button className="flex-1 cursor-pointer rounded-xl border border-white/15 px-4 py-3" onClick={() => { request.current = null; setSearch({}); setError('') }}>Import another folder</button>
          <button className="flex-1 cursor-pointer rounded-xl bg-[#FF7A59] px-4 py-3 font-semibold text-[#200C05]" onClick={() => navigate(`/app/events/${eventId}`)}>See gallery</button>
        </div>}
      </main>
    </div>
  )
}
