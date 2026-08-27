import { useEffect, useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import AppHeader from '../../components/app/AppHeader'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import { getEventDetail, updateEventDetail, archiveEvent, deleteEvent } from '../../lib/eventsApi'

const JOIN_POLICIES = [
  { value: 'OPEN', label: 'Open', body: 'Anyone with the code or QR joins instantly.' },
  { value: 'APPROVAL', label: 'Approval required', body: 'You admit each person from the Event Lobby.' },
]

const CONTRIBUTION_POLICIES = [
  { value: 'ATTENDEES_CAN_ADD', label: 'Attendees can add photos', body: 'Anyone admitted can upload.' },
  { value: 'ORGANIZER_ONLY', label: 'Organizer only', body: 'Only you can upload photos.' },
]

function EventSettings() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const isSetup = !!location.state?.setup
  const [confirming, setConfirming] = useState(null) // null | 'archive' | 'delete'

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [joinPolicy, setJoinPolicy] = useState('OPEN')
  const [contributionPolicy, setContributionPolicy] = useState('ATTENDEES_CAN_ADD')

  const { data: event, isLoading, isError } = useQuery({
    queryKey: ['events', eventId, 'detail'],
    queryFn: () => getEventDetail(eventId),
  })

  useEffect(() => {
    if (!event) return
    setName(event.name)
    setDescription(event.description || '')
    setJoinPolicy(event.joinPolicy)
    setContributionPolicy(event.contributionPolicy)
  }, [event])

  const saveMutation = useMutation({
    mutationFn: (fields) => updateEventDetail(eventId, fields),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      if (isSetup) {
        navigate(`/app/events/${eventId}/share`, { state: { setup: true } })
      } else {
        toast.success('Settings saved')
      }
    },
    onError: () => toast.error('Something went wrong. Try again.'),
  })

  const archiveMutation = useMutation({
    mutationFn: () => archiveEvent(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      toast.success('Event archived')
      navigate(`/app/events/${eventId}`)
    },
    onError: () => toast.error('Something went wrong. Try again.'),
    onSettled: () => setConfirming(null),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteEvent(eventId),
    onSuccess: () => {
      // Cascade teardown (photos, faces, the event row itself) runs async in the
      // backend, so an invalidate+refetch here would still see the event for a
      // few seconds. Strip it from the cached lists immediately instead.
      queryClient.setQueryData(['events', 'organized'], (old) => old?.filter((e) => e.eventID !== eventId))
      queryClient.setQueryData(['events', 'my-events'], (old) => old?.filter((e) => e.eventID !== eventId))
      queryClient.removeQueries({ queryKey: ['events', eventId] })
      toast.success('Event deleted')
      navigate('/app')
    },
    onError: () => toast.error('Something went wrong. Try again.'),
    onSettled: () => setConfirming(null),
  })

  const submit = (e) => {
    e.preventDefault()
    if (!name.trim()) return
    saveMutation.mutate({ name: name.trim(), description: description.trim(), joinPolicy, contributionPolicy })
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="Event Settings" backTo={`/app/events/${eventId}`} />

      {isLoading && <LoadingSpinner messages={['Loading settings…', 'Fetching the details…']} />}
      {isError && <p className="px-5 pt-6 text-[15px] text-white/45">Couldn't load this event. Try again shortly.</p>}

      {event && (
        <form onSubmit={submit} className="mx-auto max-w-[560px] px-5 pb-20 pt-4">
          <div className="mb-5 flex flex-col gap-[7px]">
            <label className="text-[13.5px] font-semibold text-white/82">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-xl border border-white/[0.09] bg-white/[0.06] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
            />
          </div>

          <div className="mb-6 flex flex-col gap-[7px]">
            <label className="text-[13.5px] font-semibold text-white/82">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full resize-none rounded-xl border border-white/[0.09] bg-white/[0.06] px-4 py-[14px] text-[15px] text-[#F5F5F7] outline-none"
            />
          </div>

          <div className="mb-2 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">Who can join</div>
          <div className="mb-6 flex flex-col gap-2">
            {JOIN_POLICIES.map((opt) => (
              <button
                type="button"
                key={opt.value}
                onClick={() => setJoinPolicy(opt.value)}
                className="w-full cursor-pointer rounded-[14px] border px-4 py-3.5 text-left transition-colors duration-150"
                style={{
                  borderColor: joinPolicy === opt.value ? 'rgba(255,122,89,0.55)' : 'rgba(255,255,255,0.09)',
                  background: joinPolicy === opt.value ? 'rgba(255,122,89,0.09)' : 'rgba(255,255,255,0.05)',
                }}
              >
                <div className="text-[15px] font-semibold tracking-[-0.01em]">{opt.label}</div>
                <div className="mt-[3px] text-[13.5px] leading-[1.5] text-white/50">{opt.body}</div>
              </button>
            ))}
          </div>

          <div className="mb-2 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">
            Who can add photos
          </div>
          <div className="mb-7 flex flex-col gap-2">
            {CONTRIBUTION_POLICIES.map((opt) => (
              <button
                type="button"
                key={opt.value}
                onClick={() => setContributionPolicy(opt.value)}
                className="w-full cursor-pointer rounded-[14px] border px-4 py-3.5 text-left transition-colors duration-150"
                style={{
                  borderColor: contributionPolicy === opt.value ? 'rgba(255,122,89,0.55)' : 'rgba(255,255,255,0.09)',
                  background: contributionPolicy === opt.value ? 'rgba(255,122,89,0.09)' : 'rgba(255,255,255,0.05)',
                }}
              >
                <div className="text-[15px] font-semibold tracking-[-0.01em]">{opt.label}</div>
                <div className="mt-[3px] text-[13.5px] leading-[1.5] text-white/50">{opt.body}</div>
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={!name.trim() || saveMutation.isPending}
            className="w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
          >
            {isSetup ? 'Next' : saveMutation.isPending ? 'Saving…' : 'Save changes'}
          </button>

          {!isSetup && (
            <>
              <div className="my-[26px] h-px bg-white/[0.07]" />
              <div className="mb-2.5 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">
                Danger zone
              </div>
              <button
                type="button"
                onClick={() => setConfirming('archive')}
                className="mb-2.5 w-full cursor-pointer rounded-[14px] border border-white/[0.09] bg-white/[0.05] px-4 py-3.5 text-left transition-transform duration-100 ease-out active:scale-[0.99]"
              >
                <div className="text-[15.5px] font-semibold tracking-[-0.01em]">Archive event</div>
                <div className="mt-[5px] text-[14px] leading-[1.5] text-white/50 text-pretty">
                  Photos stay viewable and downloadable, but no one new can join and no more photos can be added.
                </div>
              </button>
              <button
                type="button"
                onClick={() => setConfirming('delete')}
                className="w-full cursor-pointer rounded-[14px] border border-[rgba(255,89,89,0.25)] bg-[rgba(255,89,89,0.08)] px-4 py-3.5 text-left text-[#FF8A8A] transition-transform duration-100 ease-out active:scale-[0.99]"
              >
                <div className="text-[15.5px] font-semibold tracking-[-0.01em]">Delete permanently</div>
                <div className="mt-[5px] text-[14px] leading-[1.5] text-white/50 text-pretty">
                  Every photo and match is destroyed. There's no trash and no undo.
                </div>
              </button>
            </>
          )}
        </form>
      )}

      <ConfirmDialog
        open={confirming === 'archive'}
        title="Archive event?"
        body="Photos stay viewable and downloadable by everyone, but no one new can join and no more photos can be added. This can't be undone. There's no un-archiving."
        cta="Archive"
        onCancel={() => setConfirming(null)}
        onConfirm={archiveMutation.isPending ? undefined : archiveMutation.mutate}
      />
      <ConfirmDialog
        open={confirming === 'delete'}
        title="Delete event permanently?"
        body="Every photo and match is destroyed. There's no trash and no undo."
        cta="Delete forever"
        danger
        onCancel={() => setConfirming(null)}
        onConfirm={deleteMutation.isPending ? undefined : deleteMutation.mutate}
      />
    </div>
  )
}

export default EventSettings
