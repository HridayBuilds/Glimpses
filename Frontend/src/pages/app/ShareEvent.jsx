import { useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import AppHeader from '../../components/app/AppHeader'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { getEventInfo } from '../../lib/membershipApi'

function ShareEvent() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const isSetup = !!location.state?.setup
  const [copied, setCopied] = useState(false)

  // GET /events/{id}/info (membership) rather than the events Lambda's
  // organizer-only detail/qrcode routes — this page is also reachable by an
  // admitted attendee (via the gallery's "Share Event" option), and membership
  // already returns accessCode + qrcodeUrl to any admitted member, not just the organizer.
  const {
    data: event,
    isLoading,
    isError: errorQr,
  } = useQuery({
    queryKey: ['events', eventId, 'info'],
    queryFn: () => getEventInfo(eventId),
  })
  const qrcode = event

  const copyCode = () => {
    if (!event?.accessCode) return
    navigator.clipboard.writeText(event.accessCode).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    })
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      {!isSetup && <AppHeader title="Share Event" backTo={`/app/events/${eventId}`} />}

      {isLoading && <LoadingSpinner messages={['Preparing your QR code…', 'Almost there…']} />}

      {!isLoading && (
        <div className="mx-auto flex max-w-[420px] flex-col items-center px-6 pb-14 pt-[26px] text-center">
          {isSetup && <h1 className="mb-2 text-[28px] font-bold leading-[1.1] tracking-[-0.024em]">Share the event</h1>}
          <p className="mb-7 text-pretty text-[15.5px] leading-[1.55] text-white/55">
            Anyone who scans this code or enters it manually can join.
          </p>

          {errorQr ? (
            <p className="mb-7 text-[14.5px] text-white/45">Couldn't load the QR code. Try again shortly.</p>
          ) : (
            <>
              <div className="mb-3 rounded-[20px] border border-white/[0.09] bg-white p-4">
                <img src={qrcode.qrcodeUrl} alt="Event QR code" className="h-[220px] w-[220px]" />
              </div>
              <a
                href={qrcode.qrcodeUrl}
                download="qrcode.png"
                className="mb-7 flex items-center gap-1.5 rounded-full border border-white/[0.1] bg-white/[0.06] px-4 py-2 text-[13.5px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 3v12m0 0-4.5-4.5M12 15l4.5-4.5M4 20h16"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Download QR
              </a>
            </>
          )}

          <div className="mb-2 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">Access code</div>
          <div className="mb-8 flex items-center gap-2.5 rounded-2xl border border-white/[0.09] bg-white/[0.06] py-3.5 pl-6 pr-3.5">
            <div className="font-mono text-[26px] font-semibold tracking-[0.12em]">{event?.accessCode}</div>
            <button
              onClick={copyCode}
              aria-label="Copy access code"
              title="Copy access code"
              className="flex h-9 w-9 flex-none cursor-pointer items-center justify-center rounded-full border border-white/[0.1] bg-white/[0.07] text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-90"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                <rect x="9" y="9" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="2" />
                <path d="M6 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v2" stroke="currentColor" strokeWidth="2" />
              </svg>
            </button>
          </div>
          {copied && <div className="-mt-6 mb-6 text-[13px] text-[#8FE3B8]">Copied</div>}

          {isSetup && (
            <button
              onClick={() => navigate(`/app/events/${eventId}`)}
              className="w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
            >
              Next
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default ShareEvent
