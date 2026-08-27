import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { joinEvent } from '../../lib/membershipApi'

function JoinLink() {
  const { code } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const joinMutation = useMutation({
    mutationFn: () => joinEvent(code),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      navigate(`/app/events/${result.eventID}`, { replace: true })
    },
  })

  useEffect(() => {
    joinMutation.mutate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-4 bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] px-6 text-center text-[#F5F5F7]">
      {joinMutation.isError ? (
        <>
          <p className="text-[16px] leading-[1.55] text-white/60 text-pretty">
            That code doesn't match any event. Check it and try again.
          </p>
          <button
            onClick={() => navigate('/join')}
            className="rounded-xl bg-[#FF7A59] px-6 py-3.5 text-[15px] font-semibold text-[#200C05]"
          >
            Enter a code
          </button>
        </>
      ) : (
        <p className="text-[16px] text-white/60">Joining event…</p>
      )}
    </div>
  )
}

export default JoinLink
