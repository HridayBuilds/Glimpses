import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { joinEvent } from '../../lib/membershipApi'

// Matches the alphabet the backend actually generates access codes from
// (Backend/events/src/Manager/manager.py: ACCESS_CODE_ALPHABET) — excludes 0/1/I/O.
const CODE_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'.split('')
const CODE_LENGTH = 6

function JoinEvent() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [code, setCode] = useState('')
  const [error, setError] = useState(false)

  const joinMutation = useMutation({
    mutationFn: (accessCode) => joinEvent(accessCode),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      navigate(`/app/events/${result.eventID}`)
    },
    onError: () => setError(true),
  })

  const tapKey = (v) => () => {
    setError(false)
    setCode((c) => (c.length >= CODE_LENGTH ? c : c + v))
  }

  const backspace = () => {
    setError(false)
    setCode((c) => c.slice(0, -1))
  }

  const submitJoin = () => {
    if (code.length !== CODE_LENGTH) return setError(true)
    joinMutation.mutate(code)
  }

  const ready = code.length === CODE_LENGTH

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="sticky top-0 z-20 flex items-center gap-3.5 bg-[rgba(10,10,12,0.72)] px-5 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
        <button onClick={() => navigate('/app')} className="cursor-pointer border-none bg-transparent p-0.5 text-[16px] text-[#FF7A59]">
          ‹ My events
        </button>
      </div>
      <div className="mx-auto max-w-[520px] px-5 pb-10 pt-[22px]">
        <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">Enter the event code</h1>
        <p className="mb-[26px] text-[16px] leading-[1.55] text-white/55 text-pretty">
          Enter six characters, or scan a QR code instead.
        </p>

        <div className="mb-[18px] flex gap-2">
          {Array.from({ length: CODE_LENGTH }, (_, i) => (
            <div
              key={i}
              className="flex aspect-[0.8] flex-1 items-center justify-center rounded-xl font-mono text-[24px] font-semibold transition-colors duration-150"
              style={{
                background: code[i] ? 'rgba(255,255,255,0.09)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${error ? 'rgba(255,89,89,0.45)' : i === code.length ? 'rgba(255,122,89,0.7)' : 'rgba(255,255,255,0.09)'}`,
              }}
            >
              {code[i] || ''}
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[#FF5959]/25 bg-[#FF5959]/[0.09] px-3.5 py-3">
            <span className="text-[14px] leading-[1.5] text-[#FFBEBE]/90">
              That code doesn't match any event. Check it and try again.
            </span>
          </div>
        )}

        <div className="mb-5 flex flex-wrap gap-2">
          {CODE_ALPHABET.map((c) => (
            <button
              key={c}
              onClick={tapKey(c)}
              className="min-w-0 flex-[1_1_15%] rounded-[11px] border border-white/[0.08] bg-white/[0.06] py-3.5 font-mono text-[17px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
            >
              {c}
            </button>
          ))}
          <button
            onClick={backspace}
            className="min-w-0 flex-[1_1_15%] rounded-[11px] border border-white/[0.08] bg-white/[0.06] py-3.5 font-mono text-[17px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
          >
            ⌫
          </button>
        </div>

        <button
          onClick={submitJoin}
          disabled={joinMutation.isPending}
          style={ready ? { background: '#FF7A59', color: '#200C05' } : { background: 'rgba(255,255,255,0.07)', color: '#F5F5F7' }}
          className="w-full rounded-xl py-4 text-[16px] font-semibold transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
        >
          Join event
        </button>
      </div>
    </div>
  )
}

export default JoinEvent
