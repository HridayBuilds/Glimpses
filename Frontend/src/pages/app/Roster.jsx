import { useParams } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import AppHeader from '../../components/app/AppHeader'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { getAttendees, admitAttendee, denyAttendee, ejectAttendee } from '../../lib/membershipApi'

function Roster() {
  const { eventId } = useParams()
  const queryClient = useQueryClient()

  const {
    data: pending,
    isLoading: loadingPending,
    isError: errorPending,
  } = useQuery({
    queryKey: ['events', eventId, 'attendees', 'PENDING'],
    queryFn: () => getAttendees(eventId, 'PENDING'),
  })
  const {
    data: attendees,
    isLoading: loadingAttendees,
    isError: errorAttendees,
  } = useQuery({
    queryKey: ['events', eventId, 'attendees', 'ATTENDEE'],
    queryFn: () => getAttendees(eventId, 'ATTENDEE'),
  })

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ['events', eventId, 'attendees'] })

  const admitMutation = useMutation({ mutationFn: (userId) => admitAttendee(eventId, userId), onSuccess: invalidate })
  const denyMutation = useMutation({ mutationFn: (userId) => denyAttendee(eventId, userId), onSuccess: invalidate })
  const ejectMutation = useMutation({ mutationFn: (userId) => ejectAttendee(eventId, userId), onSuccess: invalidate })

  const hasPending = (pending?.length ?? 0) > 0

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="Event Lobby" backTo={`/app/events/${eventId}`} />

      <div className="mx-auto max-w-[560px] px-5 pb-20 pt-4">
        {loadingPending && loadingAttendees && (
          <LoadingSpinner messages={['Loading the lobby…', 'Fetching attendees…']} />
        )}
        {(errorPending || errorAttendees) && (
          <p className="text-[15px] text-white/45">Couldn't load attendees. Try again shortly.</p>
        )}

        {hasPending && (
          <div className="mb-[30px]">
            <div className="mb-3 text-[12px] font-semibold uppercase tracking-[0.09em] text-[#FF9578]">
              Waiting for approval: {pending.length}
            </div>
            <div className="flex flex-col gap-2">
              {pending.map((p) => (
                <div
                  key={p.userID}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-[14px] border border-[rgba(255,122,89,0.22)] bg-[rgba(255,122,89,0.07)] px-[15px] py-3.5"
                >
                  <div className="min-w-0">
                    <div className="text-[15.5px] font-semibold leading-[1.4] tracking-[-0.01em]">{p.displayName}</div>
                    <div className="overflow-hidden text-ellipsis text-[13.5px] leading-[1.55] text-white/45">{p.email}</div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => denyMutation.mutate(p.userID)}
                      disabled={denyMutation.isPending || admitMutation.isPending}
                      className="cursor-pointer rounded-[10px] border border-white/10 bg-white/[0.07] px-3.5 py-2.5 text-[14px] text-white/75 transition-transform duration-[90ms] ease-out active:scale-95"
                    >
                      Deny
                    </button>
                    <button
                      onClick={() => admitMutation.mutate(p.userID)}
                      disabled={denyMutation.isPending || admitMutation.isPending}
                      className="cursor-pointer rounded-[10px] border-none bg-[#FF7A59] px-[15px] py-2.5 text-[14px] font-semibold text-[#200C05] transition-transform duration-[90ms] ease-out active:scale-95"
                    >
                      Admit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mb-1.5 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">
          Admitted: {attendees?.length ?? 0}
        </div>
        <div>
          {attendees?.length === 0 && !loadingAttendees && !errorAttendees && (
            <p className="pt-2 text-[14px] text-white/45">No attendees yet.</p>
          )}
          {attendees?.map((a) => (
            <div
              key={a.userID}
              className="flex items-center justify-between gap-3 border-b border-white/[0.06] py-[15px]"
            >
              <div className="min-w-0">
                <div className="text-[15.5px] font-semibold leading-[1.45] tracking-[-0.01em]">{a.displayName}</div>
                <div className="overflow-hidden text-ellipsis text-[13.5px] leading-[1.6] text-white/45">{a.email}</div>
              </div>
              <button
                onClick={() => ejectMutation.mutate(a.userID)}
                disabled={ejectMutation.isPending}
                className="flex-none cursor-pointer rounded-[10px] border border-[rgba(255,89,89,0.28)] bg-transparent px-[13px] py-2 text-[13.5px] text-[#FF8A8A] transition-transform duration-[90ms] ease-out active:scale-95"
              >
                Eject
              </button>
            </div>
          ))}
        </div>
        <p className="mt-[18px] text-[13.5px] leading-[1.6] text-white/38 text-pretty">
          Ejecting removes access immediately. Photos they've already uploaded stay in the event, still attributed to
          them.
        </p>
      </div>
    </div>
  )
}

export default Roster
