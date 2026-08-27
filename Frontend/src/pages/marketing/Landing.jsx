import { useNavigate } from 'react-router-dom'
import ImageSlot from '../../components/common/ImageSlot'

const steps = [
  {
    title: 'Join with a code or QR',
    body: 'Scan a QR code or type in a short code to join any event.',
    icon: (
      <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="#FF9578" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1.5"></rect>
        <rect x="14" y="3" width="7" height="7" rx="1.5"></rect>
        <rect x="3" y="14" width="7" height="7" rx="1.5"></rect>
        <path d="M14 14h3M20 14h1M14 18v3M17.5 17.5h3.5M18 21h3"></path>
      </svg>
    ),
  },
  {
    title: 'Add a selfie once',
    body: "One selfie is all it takes. It's used only to find you in this event's photos.",
    icon: (
      <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="#FF9578" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="11" r="6.5"></circle>
        <path d="M9.6 9.6h.01M14.4 9.6h.01M9.9 13.4c1.2 1.1 3 1.1 4.2 0"></path>
        <path d="M4.2 20.5c1.4-2.5 4.4-4 7.8-4s6.4 1.5 7.8 4"></path>
      </svg>
    ),
  },
  {
    title: "Everyone's photos get sorted automatically",
    body: "As photos come in from every phone, they're automatically matched to the right people.",
    icon: (
      <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="#FF9578" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 8V5.5A2.5 2.5 0 0 1 5.5 3H8M16 3h2.5A2.5 2.5 0 0 1 21 5.5V8M21 16v2.5A2.5 2.5 0 0 1 18.5 21H16M8 21H5.5A2.5 2.5 0 0 1 3 18.5V16"></path>
        <path d="M12 8.2l.9 2.2 2.2.9-2.2.9-.9 2.2-.9-2.2-2.2-.9 2.2-.9.9-2.2z"></path>
      </svg>
    ),
  },
  {
    title: "See just the ones you're in",
    body: 'Skip the scrolling. Open your gallery and see only your photos, ready to save or share.',
    icon: (
      <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="#FF9578" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="14" rx="2.5"></rect>
        <path d="M3 14.5l4.2-3.6 3.3 2.8"></path>
        <circle cx="15.6" cy="9.2" r="1.4"></circle>
        <path d="M9.6 20.6l1.9 1.9 3.9-4.2"></path>
      </svg>
    ),
  },
]

const heroPhotos = [
  { src: 'images/marketing/site-hero-1.jpg', label: 'Candid group shot at an event', objectPosition: '50% 32%' },
  { src: 'images/marketing/site-hero-3.jpg', label: 'Two friends laughing', objectPosition: '50% 28%' },
  { src: 'images/marketing/site-hero-2.jpg', label: 'Guest holding up a phone', objectPosition: '50% 42%' },
  { src: 'images/marketing/site-hero-4.jpg', label: 'Table toast, candid', objectPosition: '50% 22%' },
]

function Landing() {
  const navigate = useNavigate()

  return (
    <div>
      <div className="relative overflow-hidden border-b border-white/[0.06]">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              'radial-gradient(70% 90% at 78% -10%, rgba(255,122,89,0.18) 0%, rgba(255,122,89,0) 62%), radial-gradient(60% 80% at 8% 110%, rgba(122,162,255,0.09) 0%, rgba(122,162,255,0) 60%)',
          }}
        />
        <div className="relative mx-auto grid max-w-[1080px] grid-cols-1 items-center gap-9 px-5 py-14 sm:px-6 md:grid-cols-[1.1fr_0.9fr] md:gap-14 md:py-24">
          <div>
            <div className="mb-[22px] text-[12.5px] font-semibold uppercase tracking-[0.16em] text-[#FF9578]/90">
              Event photos, sorted by face
            </div>
            <h1 className="mb-[22px] max-w-[620px] text-[40px] font-bold leading-[1.02] tracking-[-0.035em] text-balance md:text-[64px]">
              Every phone at the event took photos.
            </h1>
            <p className="mb-9 max-w-[490px] text-[17.5px] leading-[1.5] tracking-[-0.01em] text-white/60 text-pretty md:text-[21px]">
              This is the one place they all land, sorted down to just the ones you're actually in.
            </p>
            <div className="flex flex-col items-stretch gap-3.5 sm:flex-row sm:items-center">
              <button
                onClick={() => navigate('/signup')}
                className="whitespace-nowrap rounded-full bg-[#FF7A59] px-[30px] py-4 text-center text-[16.5px] font-semibold tracking-[-0.008em] text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.97]"
              >
                Get started
              </button>
              <button
                onClick={() => navigate('/join')}
                className="whitespace-nowrap rounded-full border border-white/[0.14] px-[30px] py-4 text-center text-[16px] font-medium text-white/70 transition-[transform,background] duration-100 ease-out hover:bg-white/[0.06] active:scale-[0.97]"
              >
                Have an event code?
              </button>
            </div>
          </div>
          <div className="relative grid grid-cols-2 gap-3 md:gap-3.5">
            <div className="pointer-events-none absolute -left-[10%] -top-[14%] h-[55%] w-[55%] rounded-full bg-[#FF7A59]/20 blur-[70px]" />
            {heroPhotos.map((p) => (
              <div
                key={p.src}
                className="relative aspect-[4/5] overflow-hidden rounded-lg border border-white/[0.14] shadow-[0_24px_56px_rgba(0,0,0,0.55)]"
              >
                <ImageSlot src={p.src} label={p.label} objectPosition={p.objectPosition} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1080px] px-5 pb-4 pt-14 sm:px-6 md:pb-6 md:pt-24">
        <div className="mb-11 text-xs font-bold uppercase tracking-[0.11em] text-white/40">How it goes</div>
        <div className="grid grid-cols-1 gap-[30px] md:grid-cols-2 md:gap-x-14 md:gap-y-11">
          {steps.map((s) => (
            <div key={s.title} className="flex items-start gap-[22px]">
              <div className="flex h-[60px] w-[60px] flex-none items-center justify-center rounded-[18px] border border-[#FF7A59]/30 bg-[#FF7A59]/[0.12]">
                {s.icon}
              </div>
              <div>
                <div className="mb-2 text-xl font-semibold tracking-[-0.018em]">{s.title}</div>
                <div className="max-w-[40ch] text-base leading-[1.6] text-white/[0.52] text-pretty">{s.body}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-12">
          <button
            onClick={() => navigate('/how-it-works')}
            className="text-base font-semibold tracking-[-0.008em] text-[#FF7A59]"
          >
            See how the matching works →
          </button>
        </div>
      </div>

      <div className="mx-auto max-w-[1080px] px-6 pb-[110px] pt-24">
        <div className="flex flex-wrap items-end justify-between gap-10 border-t border-white/[0.08] pt-[46px]">
          <h2 className="max-w-[460px] text-[28px] font-bold leading-[1.06] tracking-[-0.03em] md:text-[38px]">
            Start your first event.
          </h2>
          <button
            onClick={() => navigate('/signup')}
            className="flex-none whitespace-nowrap rounded-full bg-[#FF7A59] px-8 py-4 text-[16.5px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.97]"
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  )
}

export default Landing
