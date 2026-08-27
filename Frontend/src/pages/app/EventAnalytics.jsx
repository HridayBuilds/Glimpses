import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import AppHeader from '../../components/app/AppHeader'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { getEventStats } from '../../lib/eventsApi'
import { formatBytes } from '../../lib/format'

function StatCard({ label, value }) {
  return (
    <div className="rounded-[18px] border border-white/[0.09] bg-white/[0.05] p-5">
      <div className="text-[34px] font-bold leading-[1.1] tracking-[-0.02em] tabular-nums">{value}</div>
      <div className="mt-1.5 text-[13px] font-semibold uppercase tracking-[0.08em] text-white/45">{label}</div>
    </div>
  )
}

function EventAnalytics() {
  const { eventId } = useParams()

  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ['events', eventId, 'stats'],
    queryFn: () => getEventStats(eventId),
  })

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="Event Analytics" backTo={`/app/events/${eventId}`} />

      {isLoading && <LoadingSpinner messages={['Crunching the numbers…', 'Almost there…']} />}
      {isError && <p className="px-5 pt-6 text-[15px] text-white/45">Couldn't load analytics. Try again shortly.</p>}

      {!isLoading && !isError && (
        <div className="mx-auto grid max-w-[560px] grid-cols-2 gap-2.5 px-5 pb-20 pt-4">
          <StatCard label="Attendees" value={stats.attendeeCount} />
          <StatCard label="Photos" value={stats.photoCount} />
          <div className="col-span-2">
            <StatCard label="Storage used" value={formatBytes(stats.storageBytes)} />
          </div>
        </div>
      )}
    </div>
  )
}

export default EventAnalytics
