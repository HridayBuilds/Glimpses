import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useInfiniteQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { listPhotos, bulkDeletePhotos } from '../../lib/galleryApi'
import { requestDownload, getDownloadStatus } from '../../lib/downloadApi'
import PhotoViewer from './PhotoViewer'
import ConfirmDialog from '../common/ConfirmDialog'

function Gallery({ eventId, eventName, isOrganizer, onSettings }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [mode, setMode] = useState('mine')
  const [selecting, setSelecting] = useState(false)
  const [selected, setSelected] = useState([])
  const [openPhotoId, setOpenPhotoId] = useState(null)
  const [confirmingBulkDelete, setConfirmingBulkDelete] = useState(false)
  const [bulkDeleting, setBulkDeleting] = useState(false)

  // null | 'building' | 'ready'
  const [zip, setZip] = useState(null)
  const [downloadId, setDownloadId] = useState(null)
  const [zipUrl, setZipUrl] = useState(null)

  const downloadQuery = useQuery({
    queryKey: ['events', eventId, 'downloads', downloadId, 'status'],
    queryFn: () => getDownloadStatus(eventId, downloadId),
    enabled: zip === 'building' && !!downloadId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'READY' || status === 'FAILED' ? false : 2500
    },
  })

  const downloadStatus = downloadQuery.data?.status

  useEffect(() => {
    if (zip !== 'building') return
    if (downloadStatus === 'READY') {
      setZip('ready')
      setZipUrl(downloadQuery.data.downloadUrl)
    } else if (downloadStatus === 'FAILED' || (downloadQuery.isError && !downloadQuery.isFetching)) {
      setZip(null)
      setDownloadId(null)
      toast.error('Something went wrong. Try again.')
    }
  }, [zip, downloadStatus, downloadQuery.data, downloadQuery.isError, downloadQuery.isFetching])

  const startZip = async () => {
    setZip('building')
    setZipUrl(null)
    try {
      const { downloadId: newDownloadId } = await requestDownload(eventId, selected.length ? selected : undefined)
      setDownloadId(newDownloadId)
    } catch {
      setZip(null)
      toast.error('Something went wrong. Try again.')
    }
  }

  const dismissZip = () => {
    setZip(null)
    setDownloadId(null)
    setZipUrl(null)
  }

  const downloadZip = () => {
    if (zipUrl) window.open(zipUrl, '_blank')
    dismissZip()
    setSelecting(false)
    setSelected([])
  }

  const zipSelected = zip === 'building' ? undefined : zip === 'ready' ? downloadZip : startZip

  const mineQuery = useQuery({
    queryKey: ['events', eventId, 'photos', 'mine'],
    queryFn: () => listPhotos(eventId, { mine: true }),
    enabled: mode === 'mine',
  })

  const allQuery = useInfiniteQuery({
    queryKey: ['events', eventId, 'photos', 'all'],
    queryFn: ({ pageParam }) => listPhotos(eventId, { cursor: pageParam }),
    initialPageParam: null,
    getNextPageParam: (lastPage) => lastPage.cursor,
    enabled: mode === 'all',
  })

  const photos = mode === 'mine' ? mineQuery.data?.photos ?? [] : (allQuery.data?.pages ?? []).flatMap((p) => p.photos)
  const isLoading = mode === 'mine' ? mineQuery.isLoading : allQuery.isLoading
  const isError = mode === 'mine' ? mineQuery.isError : allQuery.isError

  const sentinelRef = useRef(null)
  const observerRef = useRef(null)
  const sentinelCallback = useCallback(
    (node) => {
      if (observerRef.current) observerRef.current.disconnect()
      if (!node || mode !== 'all') return
      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && allQuery.hasNextPage && !allQuery.isFetchingNextPage) {
          allQuery.fetchNextPage()
        }
      })
      observerRef.current.observe(node)
      sentinelRef.current = node
    },
    [mode, allQuery.hasNextPage, allQuery.isFetchingNextPage, allQuery.fetchNextPage],
  )

  const toggleSelecting = () => {
    setSelecting((s) => !s)
    setSelected([])
  }

  const toggleSelected = (photoId) => {
    setSelected((s) => (s.includes(photoId) ? s.filter((id) => id !== photoId) : [...s, photoId]))
  }

  const selectAll = () => setSelected(photos.map((p) => p.photoID))

  const handleBulkDelete = async () => {
    setBulkDeleting(true)
    try {
      const { deletedPhotoIDs } = await bulkDeletePhotos(eventId, selected)
      queryClient.invalidateQueries({ queryKey: ['events', eventId, 'photos'] })
      if (deletedPhotoIDs.length === selected.length) {
        toast.success(`Deleted ${deletedPhotoIDs.length} ${deletedPhotoIDs.length === 1 ? 'photo' : 'photos'}`)
      } else {
        toast.error(`Deleted ${deletedPhotoIDs.length} of ${selected.length} photos — some couldn't be deleted`)
      }
      setSelecting(false)
      setSelected([])
    } catch {
      toast.error('Something went wrong. Try again.')
    } finally {
      setBulkDeleting(false)
      setConfirmingBulkDelete(false)
    }
  }

  const openPhoto = photos.find((p) => p.photoID === openPhotoId) ?? null

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 bg-[rgba(10,10,12,0.66)] px-4 pb-3 pt-3 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <div className="mx-auto mb-3 flex max-w-[1080px] items-center justify-between gap-3">
          <button
            onClick={() => navigate('/app')}
            className="flex-none cursor-pointer border-none bg-transparent p-0.5 text-[16px] text-[#FF7A59]"
          >
            ‹ Events
          </button>
          <div className="overflow-hidden text-ellipsis whitespace-nowrap text-[15.5px] font-semibold tracking-[-0.012em]">
            {eventName}
          </div>
          <div className="flex flex-none gap-1.5">
            <button
              onClick={toggleSelecting}
              className="cursor-pointer border-none bg-transparent px-1 py-1 text-[15px] text-[#FF7A59]"
            >
              {selecting ? 'Done' : 'Select'}
            </button>
            {isOrganizer && (
              <button
                onClick={onSettings}
                className="cursor-pointer rounded-[9px] border border-white/10 bg-white/[0.09] px-2.5 py-1.5 text-[14px] text-[#F5F5F7] transition-transform duration-[90ms] ease-out active:scale-95"
              >
                •••
              </button>
            )}
          </div>
        </div>
        <div className="mx-auto flex max-w-[1080px] items-center gap-2">
          <div className="flex flex-1 gap-[3px] rounded-[11px] border border-white/[0.08] bg-white/[0.07] p-[3px]">
            <button
              onClick={() => setMode('mine')}
              className="flex-1 cursor-pointer rounded-[8px] border-none px-2 py-2.5 text-[14.5px] font-semibold tracking-[-0.005em] transition-colors duration-[180ms] ease-out"
              style={{
                background: mode === 'mine' ? 'rgba(255,255,255,0.14)' : 'transparent',
                color: mode === 'mine' ? '#F5F5F7' : 'rgba(245,245,247,0.5)',
              }}
            >
              Photos of me
            </button>
            <button
              onClick={() => setMode('all')}
              className="flex-1 cursor-pointer rounded-[8px] border-none px-2 py-2.5 text-[14.5px] font-semibold tracking-[-0.005em] transition-colors duration-[180ms] ease-out"
              style={{
                background: mode === 'all' ? 'rgba(255,255,255,0.14)' : 'transparent',
                color: mode === 'all' ? '#F5F5F7' : 'rgba(245,245,247,0.5)',
              }}
            >
              Everything
            </button>
          </div>
          <button
            onClick={() => navigate(`/app/events/${eventId}/upload`)}
            className="flex-none cursor-pointer rounded-[11px] border-none bg-[#FF7A59] px-[15px] py-2.5 text-[14.5px] font-semibold text-[#200C05] transition-transform duration-[90ms] ease-out active:scale-95"
          >
            Add
          </button>
        </div>
      </div>

      {isLoading && <p className="px-5 pt-6 text-[15px] text-white/45">Loading…</p>}
      {isError && <p className="px-5 pt-6 text-[15px] text-white/45">Couldn't load photos. Try again shortly.</p>}

      {!isLoading && !isError && photos.length === 0 && mode === 'all' && (
        <div className="mx-auto max-w-[420px] px-[30px] py-[70px] text-center">
          <div className="mb-2 text-[20px] font-semibold tracking-[-0.016em]">No photos yet</div>
          <p className="mb-[22px] text-pretty text-[15.5px] leading-[1.6] text-white/50">
            The gallery's empty until someone uploads the first photo. That could be you.
          </p>
          <button
            onClick={() => navigate(`/app/events/${eventId}/upload`)}
            className="cursor-pointer rounded-xl border-none bg-[#FF7A59] px-[22px] py-[14px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-95"
          >
            Add photos
          </button>
        </div>
      )}

      {!isLoading && !isError && photos.length === 0 && mode === 'mine' && (
        <div className="mx-auto max-w-[420px] px-[30px] py-[70px] text-center">
          <div className="mb-2 text-[20px] font-semibold tracking-[-0.016em]">You are not in any of these photos</div>
          <p className="mb-[22px] text-pretty text-[15.5px] leading-[1.6] text-white/50">
            You're viewing "Photos of me". Matching keeps running as new photos arrive.
          </p>
          <button
            onClick={() => setMode('all')}
            className="cursor-pointer rounded-xl border border-white/[0.12] bg-white/[0.08] px-[22px] py-[14px] text-[15px] font-medium transition-transform duration-100 ease-out active:scale-95"
          >
            Show everything
          </button>
        </div>
      )}

      {zip && (
        <div className="mx-auto mt-3 max-w-[1080px] px-4">
          <div className="rounded-[14px] border border-white/10 bg-white/[0.05] p-[15px]">
            <div className="mb-2.5 flex items-center justify-between gap-2.5">
              <div className="flex min-w-0 items-center gap-2.5">
                {zip === 'building' && (
                  <div className="h-3.5 w-3.5 flex-none animate-spin rounded-full border-2 border-white/20 border-t-[#FF7A59]" />
                )}
                <div className="text-[14.5px] font-semibold tracking-[-0.008em]">
                  {zip === 'ready' ? 'Download ready' : 'Preparing download…'}
                </div>
              </div>
            </div>
            {zip === 'building' && (
              <p className="text-pretty text-[13px] leading-[1.55] text-white/42">
                Nothing is packed until you ask for it, so this takes a moment. You can keep browsing.
              </p>
            )}
            {zip === 'ready' && (
              <div className="flex gap-2.5">
                <button
                  onClick={dismissZip}
                  className="flex-none cursor-pointer rounded-[10px] border border-white/10 bg-white/[0.07] px-3.5 py-2.5 text-[14px] text-[#F5F5F7]"
                >
                  Dismiss
                </button>
                <button
                  onClick={downloadZip}
                  className="flex-1 cursor-pointer rounded-[10px] border-none bg-[#FF7A59] py-2.5 text-[14.5px] font-semibold text-[#200C05] transition-transform duration-[90ms] ease-out active:scale-[0.97]"
                >
                  Download ZIP
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {photos.length > 0 && (
        <div className="mx-auto max-w-[1080px] px-4 pb-[140px] pt-3">
          <div className="grid grid-cols-[repeat(auto-fill,minmax(104px,1fr))] gap-1 sm:grid-cols-[repeat(auto-fill,minmax(150px,1fr))]">
            {photos.map((p) => {
              const isSelected = selected.includes(p.photoID)
              return (
                <div
                  key={p.photoID}
                  onClick={() => (selecting ? toggleSelected(p.photoID) : setOpenPhotoId(p.photoID))}
                  className="relative aspect-square cursor-pointer overflow-hidden rounded-[10px] bg-white/[0.06] transition-transform duration-[220ms] ease-out"
                  style={{ transform: isSelected ? 'scale(0.9)' : 'scale(1)' }}
                >
                  <img
                    src={p.thumbnailUrl}
                    alt={p.filename}
                    loading="lazy"
                    className="h-full w-full object-cover"
                    draggable={false}
                  />
                  {selecting && (
                    <div
                      className="absolute right-1.5 top-1.5 flex h-[22px] w-[22px] items-center justify-center rounded-full border-[1.5px] border-white/80 text-[13px] font-bold"
                      style={{
                        background: isSelected ? '#FF7A59' : 'rgba(0,0,0,0.35)',
                        color: isSelected ? '#200C05' : 'transparent',
                      }}
                    >
                      {isSelected ? '✓' : ''}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
          {mode === 'all' && (
            <div ref={sentinelCallback} className="flex flex-col items-center gap-2.5 pt-[30px]">
              {allQuery.isFetchingNextPage && (
                <div className="text-[13.5px] tracking-[0.01em] text-white/38">Loading more</div>
              )}
            </div>
          )}
        </div>
      )}

      {selecting && (
        <div className="fixed inset-x-0 bottom-0 z-[60] border-t border-white/[0.12] bg-[rgba(20,20,24,0.74)] px-4 pb-[18px] pt-3.5 shadow-[0_-16px_44px_rgba(0,0,0,0.45)] backdrop-blur-[28px] backdrop-saturate-[1.8]">
            <div className="mx-auto flex max-w-[1080px] items-center gap-2.5">
              <div className="min-w-0 flex-1 text-[15px] font-semibold tracking-[-0.005em] tabular-nums">
                {selected.length === 0 ? 'Select photos' : `${selected.length} ${selected.length === 1 ? 'photo' : 'photos'}`}
              </div>
              <button
                onClick={selectAll}
                className="cursor-pointer rounded-[10px] border border-white/[0.12] bg-white/10 px-[13px] py-2.5 text-[14px] transition-transform duration-[90ms] ease-out active:scale-95"
              >
                Select all
              </button>
              <button
                onClick={() => setConfirmingBulkDelete(true)}
                disabled={selected.length === 0}
                className="flex-none cursor-pointer rounded-[10px] border border-[rgba(255,89,89,0.3)] bg-[rgba(255,89,89,0.14)] px-3.5 py-2.5 text-[14px] text-[#FF8A8A] transition-transform duration-[90ms] ease-out active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Delete
              </button>
              <button
                onClick={zipSelected}
                disabled={zip === 'building'}
                className="flex flex-none cursor-pointer items-center gap-2 whitespace-nowrap rounded-[10px] border-none px-3.5 py-2.5 text-[14px] font-semibold transition-transform duration-[90ms] ease-out active:scale-95 disabled:cursor-not-allowed"
                style={{
                  background: zip === 'building' ? 'rgba(255,255,255,0.1)' : '#FF7A59',
                  color: zip === 'building' ? 'rgba(245,245,247,0.75)' : '#200C05',
                }}
              >
                {zip === 'building' && (
                  <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-[rgba(245,245,247,0.25)] border-t-[rgba(245,245,247,0.85)]" />
                )}
                {zip === 'building' ? 'Preparing download…' : zip === 'ready' ? 'Save ZIP' : 'Download ZIP'}
              </button>
            </div>
        </div>
      )}

      {openPhoto && <PhotoViewer eventId={eventId} photo={openPhoto} onClose={() => setOpenPhotoId(null)} />}

      <ConfirmDialog
        open={confirmingBulkDelete}
        title={`Delete ${selected.length} ${selected.length === 1 ? 'photo' : 'photos'}?`}
        body="They are removed from the event for everyone. There is no trash to recover them from."
        cta="Delete"
        danger
        onCancel={() => setConfirmingBulkDelete(false)}
        onConfirm={bulkDeleting ? undefined : handleBulkDelete}
      />
    </div>
  )
}

export default Gallery
