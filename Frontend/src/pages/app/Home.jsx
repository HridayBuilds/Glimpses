import { useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getOrganizedEvents, getMyEvents } from '../../lib/eventsApi'

const STATE_STYLE = {
  ACTIVE: { label: 'Active', color: '#8FE3B8', bg: 'rgba(111,216,176,0.14)' },
  PENDING: { label: 'Pending', color: '#FF9578', bg: 'rgba(255,122,89,0.16)' },
  ARCHIVED: { label: 'Archived', color: 'rgba(245,245,247,0.55)', bg: 'rgba(255,255,255,0.07)' },
}

function eventCardState(event) {
  if (event.attendeeStatus === 'PENDING') return STATE_STYLE.PENDING
  return STATE_STYLE[event.status] || STATE_STYLE.ACTIVE
}

function EventCard({ event, onOpen }) {
  const { label, color, bg } = eventCardState(event)
  return (
    <button
      onClick={onOpen}
      className="rounded-2xl border border-white/[0.08] bg-white/[0.05] p-4 pb-3.5 text-left text-[#F5F5F7] transition-transform duration-[120ms] ease-out active:scale-[0.985] active:bg-white/[0.09]"
    >
      <div className="flex items-start justify-between gap-2.5">
        <div className="text-[19px] font-semibold leading-[1.2] tracking-[-0.016em]">{event.name}</div>
        <div
          style={{ color, background: bg }}
          className="whitespace-nowrap rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.08em]"
        >
          {label}
        </div>
      </div>
      <div className="mt-2 text-[14px] leading-[1.5] text-white/50">{event.description || 'No description'}</div>
    </button>
  )
}

function Home() {
  const navigate = useNavigate()

  const {
    data: organized,
    isLoading: loadingOrganized,
    isError: errorOrganized,
  } = useQuery({
    queryKey: ['events', 'organized'],
    queryFn: getOrganizedEvents,
  })
  const {
    data: joined,
    isLoading: loadingJoined,
    isError: errorJoined,
  } = useQuery({
    queryKey: ['events', 'my-events'],
    queryFn: getMyEvents,
  })

  const openEvent = (eventId) => () => navigate(`/app/events/${eventId}`)

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 flex items-center justify-between bg-[rgba(10,10,12,0.7)] px-5 pb-3.5 pt-4 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <div className="w-[34px] flex-none" />
        <div className="flex-1 text-center text-[13px] font-semibold uppercase tracking-[0.14em] text-white/42">
          Glimpses
        </div>
        <button
          onClick={() => navigate('/app/profile')}
          className="h-[34px] w-[34px] flex-none rounded-full border border-white/[0.12] bg-white/[0.09] text-[13px] font-semibold text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.94]"
        >
          ME
        </button>
      </div>

      <div className="mx-auto max-w-[900px] px-5 pb-[120px] pt-2">
        <h1 className="mb-[26px] mt-1.5 text-[34px] font-bold leading-[1.06] tracking-[-0.026em]">My events</h1>

        <div className="mb-3 flex items-baseline justify-between">
          <div className="text-[13px] font-bold uppercase tracking-[0.08em] text-white/90">Events I organize</div>
          <button onClick={() => navigate('/app/create')} className="p-0.5 text-[14.5px] font-semibold text-[#FF7A59]">
            New event
          </button>
        </div>
        <div className="mb-8 grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-2.5">
          {loadingOrganized && <p className="text-[14px] text-white/45">Loading…</p>}
          {errorOrganized && <p className="text-[14px] text-white/45">Couldn't load your events. Try again shortly.</p>}
          {organized?.length === 0 && <p className="text-[14px] text-white/45">You haven't created an event yet.</p>}
          {organized?.map((event) => (
            <EventCard key={event.eventID} event={event} onOpen={openEvent(event.eventID)} />
          ))}
        </div>

        <div className="mb-3 text-[13px] font-bold uppercase tracking-[0.08em] text-white/90">Events I joined</div>
        <div className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-2.5">
          {loadingJoined && <p className="text-[14px] text-white/45">Loading…</p>}
          {errorJoined && <p className="text-[14px] text-white/45">Couldn't load your events. Try again shortly.</p>}
          {joined?.length === 0 && <p className="text-[14px] text-white/45">You haven't joined an event yet.</p>}
          {joined?.map((event) => (
            <EventCard key={event.eventID} event={event} onOpen={openEvent(event.eventID)} />
          ))}
        </div>

        <button
          onClick={() => navigate('/join')}
          className="mt-[22px] w-full rounded-2xl border border-dashed border-white/[0.16] bg-white/[0.05] py-[17px] text-[15.5px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.985]"
        >
          Join an event with a code
        </button>
        <div className="mt-[26px] text-center">
          <Link to="/app/privacy" className="text-[13.5px] text-white/40">
            Privacy
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home
