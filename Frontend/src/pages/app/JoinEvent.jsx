import { memo, useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { joinEvent } from '../../lib/membershipApi'
import { extractAccessCode, decodeQRFromFile } from '../../lib/qr'
import QRScanner from '../../components/join/QRScanner'

// Matches the alphabet the backend actually generates access codes from
// (Backend/events/src/Manager/manager.py: ACCESS_CODE_ALPHABET) — excludes 0/1/I/O.
const CODE_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'.split('')
const CODE_LENGTH = 6
const CODE_INPUT_RE = /[^23456789ABCDEFGHJKLMNPQRSTUVWXYZ]/gi

const Keypad = memo(function Keypad({ onKey, onBackspace }) {
  return (
    <div className="mb-5 flex flex-wrap gap-2">
      {CODE_ALPHABET.map((c) => (
        <button
          key={c}
          data-char={c}
          onClick={onKey}
          className="min-w-0 flex-[1_1_15%] rounded-[11px] border border-white/[0.08] bg-white/[0.06] py-3.5 font-mono text-[17px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
        >
          {c}
        </button>
      ))}
      <button
        onClick={onBackspace}
        className="min-w-0 flex-[1_1_15%] rounded-[11px] border border-white/[0.08] bg-white/[0.06] py-3.5 font-mono text-[17px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
      >
        ⌫
      </button>
    </div>
  )
})

function JoinEvent() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)

  const [tab, setTab] = useState('code')
  const [code, setCode] = useState('')
  const [error, setError] = useState(false)
  const [scannerOpen, setScannerOpen] = useState(false)
  const [qrError, setQrError] = useState(null)

  const joinMutation = useMutation({
    mutationFn: (accessCode) => joinEvent(accessCode),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      navigate(`/app/events/${result.eventID}`)
    },
    onError: () => {
      if (tab === 'qr') setQrError("That QR code doesn't match any event. Try a different one.")
      else setError(true)
    },
  })

  const selectTab = (next) => {
    setTab(next)
    setError(false)
    setQrError(null)
  }

  const onKey = useCallback((e) => {
    const v = e.currentTarget.dataset.char
    setError(false)
    setCode((c) => (c.length >= CODE_LENGTH ? c : c + v))
  }, [])

  const backspace = useCallback(() => {
    setError(false)
    setCode((c) => c.slice(0, -1))
  }, [])

  const onTypeCode = (e) => {
    setError(false)
    setCode(e.target.value.toUpperCase().replace(CODE_INPUT_RE, '').slice(0, CODE_LENGTH))
  }

  const submitJoin = () => {
    if (code.length !== CODE_LENGTH) return setError(true)
    joinMutation.mutate(code)
  }

  const handleDecoded = (text) => {
    setScannerOpen(false)
    const accessCode = extractAccessCode(text)
    if (!accessCode) {
      setQrError("Couldn't find an event code in that QR code. Try again.")
      return
    }
    setQrError(null)
    setCode(accessCode)
    joinMutation.mutate(accessCode)
  }

  const onQrFileChange = async (e) => {
    const file = e.target.files[0]
    e.target.value = ''
    if (!file) return
    const text = await decodeQRFromFile(file)
    const accessCode = extractAccessCode(text)
    if (!accessCode) {
      setQrError("Couldn't find an event code in that image.")
      return
    }
    setQrError(null)
    setCode(accessCode)
    joinMutation.mutate(accessCode)
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
        <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">Join an event</h1>
        <p className="mb-[22px] text-[16px] leading-[1.55] text-white/55 text-pretty">
          Enter the six-character code, or scan the event's QR code.
        </p>

        <div className="mb-[22px] flex gap-[3px] rounded-[11px] border border-white/[0.08] bg-white/[0.07] p-[3px]">
          <button
            onClick={() => selectTab('code')}
            className="flex-1 cursor-pointer rounded-[8px] border-none px-2 py-2.5 text-[14.5px] font-semibold tracking-[-0.005em] transition-colors duration-[180ms] ease-out"
            style={{
              background: tab === 'code' ? 'rgba(255,255,255,0.14)' : 'transparent',
              color: tab === 'code' ? '#F5F5F7' : 'rgba(245,245,247,0.5)',
            }}
          >
            Enter code
          </button>
          <button
            onClick={() => selectTab('qr')}
            className="flex-1 cursor-pointer rounded-[8px] border-none px-2 py-2.5 text-[14.5px] font-semibold tracking-[-0.005em] transition-colors duration-[180ms] ease-out"
            style={{
              background: tab === 'qr' ? 'rgba(255,255,255,0.14)' : 'transparent',
              color: tab === 'qr' ? '#F5F5F7' : 'rgba(245,245,247,0.5)',
            }}
          >
            Scan QR
          </button>
        </div>

        {tab === 'code' ? (
          <>
            <div className="relative mb-[18px]">
              <input
                type="text"
                inputMode="text"
                autoComplete="off"
                autoCapitalize="characters"
                spellCheck={false}
                maxLength={CODE_LENGTH}
                value={code}
                onChange={onTypeCode}
                aria-label="Six-character event code"
                className="absolute inset-0 z-10 h-full w-full cursor-default opacity-0"
              />
              <div className="flex gap-2 pointer-events-none">
                {Array.from({ length: CODE_LENGTH }, (_, i) => (
                  <div
                    key={i}
                    className="flex aspect-[0.8] flex-1 items-center justify-center rounded-xl font-mono text-[24px] font-semibold transition-colors duration-75"
                    style={{
                      background: code[i] ? 'rgba(255,255,255,0.09)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${error ? 'rgba(255,89,89,0.45)' : i === code.length ? 'rgba(255,122,89,0.7)' : 'rgba(255,255,255,0.09)'}`,
                    }}
                  >
                    {code[i] || ''}
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[#FF5959]/25 bg-[#FF5959]/[0.09] px-3.5 py-3">
                <span className="text-[14px] leading-[1.5] text-[#FFBEBE]/90">
                  That code doesn't match any event. Check it and try again.
                </span>
              </div>
            )}

            <Keypad onKey={onKey} onBackspace={backspace} />

            <button
              onClick={submitJoin}
              disabled={joinMutation.isPending}
              style={ready ? { background: '#FF7A59', color: '#200C05' } : { background: 'rgba(255,255,255,0.07)', color: '#F5F5F7' }}
              className="w-full rounded-xl py-4 text-[16px] font-semibold transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
            >
              Join event
            </button>
          </>
        ) : (
          <>
            {qrError && (
              <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[#FF5959]/25 bg-[#FF5959]/[0.09] px-3.5 py-3">
                <span className="text-[14px] leading-[1.5] text-[#FFBEBE]/90">{qrError}</span>
              </div>
            )}
            <div className="flex flex-col gap-2.5">
              <button
                onClick={() => setScannerOpen(true)}
                disabled={joinMutation.isPending}
                className="w-full rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
              >
                Scan with camera
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={joinMutation.isPending}
                className="w-full rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
              >
                Choose from files
              </button>
            </div>
          </>
        )}
      </div>

      <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={onQrFileChange} />

      <QRScanner open={scannerOpen} onCancel={() => setScannerOpen(false)} onDecode={handleDecoded} />
    </div>
  )
}

export default JoinEvent
