import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getJobStatus, importDriveFolder } from '../../lib/uploadApi'

const LABELS = {
  CHECKING: 'Checking public access', DOWNLOADING: 'Downloading photos',
  EXTRACTING: 'Processing photos', INDEXING: 'Indexing faces', MATCHING: 'Matching attendees',
  SUCCESS: 'Import complete', FAILED: 'Import could not finish',
}

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
    refetchInterval: (state) => ['SUCCESS', 'FAILED'].includes(state.state.data?.status) ? false : 5000,
  })
  const job = query.data
  const finished = ['SUCCESS', 'FAILED'].includes(job?.status)
  const busy = starting || (!!jobId && !finished)

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
        <h1 className="text-3xl font-bold tracking-tight">Import your photos</h1>
        <p className="mt-3 text-white/60">Paste a public Google Drive folder link. Only photos directly inside that folder are imported.</p>
        <ol className="my-6 list-decimal space-y-2 rounded-2xl border border-white/10 bg-white/5 py-5 pl-10 pr-5 text-sm leading-relaxed text-white/75">
          <li>Open the folder in Google Drive and select Share.</li>
          <li>Set General access to <strong>Anyone with the link</strong>.</li>
          <li>Keep Viewer access, allow downloads, and select Copy link.</li>
        </ol>
        <p className="mb-5 text-sm text-white/50">Private folders, individual file links, and ZIP links are not supported. Subfolders, shortcuts, and non-photo files are skipped. Keep the folder publicly accessible until the import finishes.</p>
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
          <section aria-live="polite" className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5">
            <h2 className="font-semibold">{LABELS[job?.status] || 'Starting import'}</h2>
            {job?.folderName && <p className="mt-2 break-words text-sm text-white/60">{job.folderName}</p>}
            {job?.status === 'FAILED' && <p role="alert" className="mt-3 text-sm text-[#FF8A8A]">{job.errorMessage || 'The import could not finish. Please try again.'}</p>}
            {job?.status === 'DOWNLOADING' && <p className="mt-3 text-sm">{job.downloadedCount} downloaded, {job.downloadFailedCount} failed. {job.totalCount} photos found so far.</p>}
            {finished && <p className="mt-3 text-sm">{job.succeededCount} photos added, {job.failedCount} failed, {job.duplicateCount || 0} duplicates skipped.</p>}
            {!!job && <p className="mt-3 text-sm text-white/55">{job.skippedFolders || 0} subfolders and {job.skippedCount || 0} other files skipped.</p>}
            {query.isError && <p className="mt-3 text-sm text-white/60">Waiting for a status update. We will keep checking.</p>}
            {!finished && <p className="mt-4 text-sm text-white/50">You can close this tab. The import continues in the background. Keep this page link to check its progress later.</p>}
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
