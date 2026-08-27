import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { createEvent } from '../../lib/eventsApi'

function CreateEvent() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')

  const createMutation = useMutation({
    mutationFn: (name) => createEvent(name),
    onSuccess: (event) => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      navigate(`/app/events/${event.eventID}/settings`, { state: { setup: true } })
    },
    onError: () => toast.error('Could not create the event — try again.'),
  })

  const onSubmit = (e) => {
    e.preventDefault()
    if (!name.trim()) return
    createMutation.mutate(name.trim())
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 flex items-center gap-3.5 bg-[rgba(10,10,12,0.72)] px-5 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <button onClick={() => navigate('/app')} className="cursor-pointer border-none bg-transparent p-0.5 text-[16px] text-[#FF7A59]">
          ‹ My events
        </button>
      </div>
      <form onSubmit={onSubmit} className="mx-auto max-w-[460px] px-5 pb-10 pt-[22px]">
        <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">Name the event</h1>
        <p className="mb-[26px] text-[16px] leading-[1.55] text-white/55 text-pretty">
          Just a name to start. You'll set who can join and who can add photos in settings later.
        </p>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ellison & Pike, 12 June"
          className="mb-4 w-full rounded-xl border border-white/[0.09] bg-white/[0.06] px-4 py-4 text-[19px] tracking-[-0.01em] text-[#F5F5F7] outline-none"
        />
        <button
          type="submit"
          disabled={!name.trim() || createMutation.isPending}
          className="w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
        >
          {createMutation.isPending ? 'Creating…' : 'Create event'}
        </button>
      </form>
    </div>
  )
}

export default CreateEvent
