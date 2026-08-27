import { useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import AppHeader from '../../components/app/AppHeader'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { getEventDetail, getQrcodeUrl } from '../../lib/eventsApi'

function ShareEvent() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const isSetup = !!location.state?.setup
  const [copied, setCopied] = useState(false)

  const { data: event, isLoading: loadingEvent } = useQuery({
    queryKey: ['events', eventId, 'detail'],
    queryFn: () => getEventDetail(eventId),
  })
  const { data: qrcode, isLoading: loadingQr, isError: errorQr } = useQuery({
    queryKey: ['events', eventId, 'qrcode'],
    queryFn: () => getQrcodeUrl(eventId),
  })

  const copyCode = () => {
    if (!event?.accessCode) return
    navigator.clipboard.writeText(event.accessCode).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    })
  }

  const isLoading = loadingEvent || loadingQr

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
            <div className="mb-7 rounded-[20px] border border-white/[0.09] bg-white p-4">
              <img src={qrcode.qrcodeUrl} alt="Event QR code" className="h-[220px] w-[220px]" />
            </div>
          )}

          <div className="mb-2 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">Access code</div>
          <button
            onClick={copyCode}
            className="mb-8 flex items-center gap-3 rounded-2xl border border-white/[0.09] bg-white/[0.06] px-6 py-3.5 font-mono text-[26px] font-semibold tracking-[0.12em] transition-transform duration-100 ease-out active:scale-[0.97]"
          >
            {event?.accessCode}
          </button>
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
