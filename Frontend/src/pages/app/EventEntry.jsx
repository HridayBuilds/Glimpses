import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getEventInfo } from '../../lib/membershipApi'
import { getOrganizedEvents } from '../../lib/eventsApi'
import Gallery from '../../components/gallery/Gallery'
import LoadingSpinner from '../../components/common/LoadingSpinner'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' })
}

function EventEntry() {
  const { eventId } = useParams()
  const navigate = useNavigate()

  const { data: info, isLoading, isError } = useQuery({
    queryKey: ['events', eventId, 'info'],
    queryFn: () => getEventInfo(eventId),
  })

  // GET /events/{id}/info doesn't carry a role field, so organizer-ness is read off
  // the same organized-events list Home.jsx fetches (GET /events, organizer-only).
  const { data: organized } = useQuery({
    queryKey: ['events', 'organized'],
    queryFn: getOrganizedEvents,
  })
  const isOrganizer = organized?.some((e) => e.eventID === eventId) ?? false

  // The reduced shape (no accessCode) is what GET /events/{id}/info returns for a PENDING caller.
  const isPending = info && !info.accessCode

  if (info && !isPending) {
    return (
      <Gallery
        eventId={eventId}
        eventName={info.name}
        isOrganizer={isOrganizer}
        isArchived={info.status !== 'ACTIVE'}
        canUpload={info.status === 'ACTIVE' && (isOrganizer || info.contributionPolicy !== 'ORGANIZER_ONLY')}
      />
    )
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 flex items-center gap-3.5 bg-[rgba(10,10,12,0.72)] px-5 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <button onClick={() => navigate('/app')} className="cursor-pointer border-none bg-transparent p-0.5 text-[16px] text-[#FF7A59]">
          ‹ My events
        </button>
      </div>

      {isLoading && <LoadingSpinner messages={['Loading this event…', 'Fetching the details…', 'Almost there…']} />}
      {isError && <p className="px-5 pt-6 text-[15px] text-white/45">Couldn't load this event. Try again shortly.</p>}

      {info && isPending && (
        <div className="mx-auto flex w-full max-w-[520px] flex-col px-6 pb-[60px] pt-[26px]">
          <div className="mb-[18px] flex items-center gap-2.5">
            <div className="h-[9px] w-[9px] animate-pulse rounded-full bg-[#FF7A59]" />
            <div className="text-[13px] font-semibold uppercase tracking-[0.06em] text-[#FF9578]">
              Waiting to be admitted
            </div>
          </div>
          <h1 className="mb-3 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">{info.name}</h1>
          {info.description && (
            <p className="mb-[22px] text-[16.5px] leading-[1.6] text-white/58 text-pretty">{info.description}</p>
          )}
          <div className="text-[14px] tracking-[0.01em] text-white/42">Created {formatDate(info.createdAt)}</div>
          <div className="my-[26px] h-px bg-white/[0.07]" />
          <p className="text-[15px] leading-[1.6] text-white/50 text-pretty">
            You'll get access to the gallery once the organizer approves you. No action needed on your end.
          </p>
        </div>
      )}
    </div>
  )
}

export default EventEntry
