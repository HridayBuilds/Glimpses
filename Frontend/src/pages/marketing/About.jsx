import { useNavigate } from 'react-router-dom'
import ImageSlot from '../../components/common/ImageSlot'

const audiences = [
  { t: 'Weddings', b: 'Guest phones outnumber the photographer ten to one.', ph: 'Candid wedding moment', slot: 'site-aud-wedding' },
  { t: 'Conferences', b: 'Hundreds of attendees, hundreds of half-shared albums.', ph: 'Conference hallway candid', slot: 'site-aud-conf' },
  { t: 'Reunions', b: 'Everyone shooting, nobody collecting.', ph: 'Group reunion photo', slot: 'site-aud-reunion' },
  { t: 'Any gathering', b: 'Trips, parties, team offsites, race days.', ph: 'Friends on a trip', slot: 'site-aud-any' },
]

const pairs = [
  { no: 'A place to back up everything you own', yes: 'One event, every camera, pooled once' },
  { no: 'A folder you scroll and hope for the best', yes: 'Your own photos surfaced without asking anyone' },
  { no: 'A permanent library that follows you around', yes: 'Sorting that lives inside one event and stops there' },
]

function About() {
  const navigate = useNavigate()

  return (
    <div className="mx-auto max-w-[1080px] px-5 py-14 sm:px-6 md:py-24">
      <div className="max-w-[660px]">
        <div className="mb-[22px] text-[12.5px] font-semibold uppercase tracking-[0.16em] text-[#FF9578]/90">About</div>
        <h1 className="text-[36px] font-bold leading-[1.04] tracking-[-0.034em] text-balance md:text-[56px]">
          Photos of you, in other people's cameras.
        </h1>
      </div>

      <div className="mt-14 grid grid-cols-1 gap-9 border-t border-white/[0.08] pt-11 md:grid-cols-2 md:gap-14">
        <p className="text-[19.5px] leading-[1.6] tracking-[-0.011em] text-white/72 text-pretty">
          A hundred people at an event means a hundred camera rolls. The photos of you are in there somewhere, on phones belonging to people you may barely know, and almost none of them ever reach you.
        </p>
        <p className="text-[17px] leading-[1.65] text-white/50 text-pretty">
          Glimpses exists to close that gap. Every photo from the event lands in one shared place, and each person's photos are sorted out for them automatically. No group chats to scroll, no folders to dig through, no asking a stranger to send you the one where you were laughing.
        </p>
      </div>

      <div className="mt-14 h-[240px] overflow-hidden rounded-[22px] border border-white/[0.09] md:h-[380px]">
        <ImageSlot src="images/marketing/site-about-wide.jpg" label="Wide candid shot — guests photographing each other" />
      </div>

      <div className="mt-[72px]">
        <div className="mb-6.5 text-xs font-bold uppercase tracking-[0.11em] text-white/40">Who it's for</div>
        <div className="grid grid-cols-2 gap-3.5 md:grid-cols-4">
          {audiences.map((a) => (
            <div key={a.t} className="flex flex-col overflow-hidden rounded-[18px] border border-white/[0.08] bg-white/[0.04]">
              <div className="h-[132px]">
                <ImageSlot src={`images/marketing/${a.slot}.jpg`} label={a.ph} />
              </div>
              <div className="flex flex-col gap-2 px-[18px] pb-[22px] pt-[18px]">
                <div className="text-[19px] font-semibold tracking-[-0.018em]">{a.t}</div>
                <div className="text-[14.5px] leading-[1.55] text-white/50 text-pretty">{a.b}</div>
              </div>
            </div>
          ))}
        </div>
        <p className="mx-auto mt-[22px] max-w-[680px] text-center text-base leading-[1.6] text-white/45 text-pretty">
          Anywhere several people are taking photos at once, and nobody wants to chase everyone's camera roll afterwards.
        </p>
      </div>

      <div className="mt-[76px] border-t border-white/[0.08] pt-[38px]">
        <div className="mb-[34px] text-xs font-bold uppercase tracking-[0.11em] text-white/40">What makes it different</div>
        <div className="grid grid-cols-1 items-start gap-14 md:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="mb-[22px] text-[21px] font-semibold leading-[1.32] tracking-[-0.022em] text-pretty md:text-[26px]">
              Glimpses isn't a photo backup service or a shared drive. It's built around one problem: finding yourself in photos other people took.
            </p>
            <p className="text-[17px] leading-[1.65] text-white/52 text-pretty">
              It is not a replacement for Google Drive, iCloud, or any general cloud storage, and it isn't trying to be. Those hold everything you own. Glimpses does one narrower thing: it takes the photos from a single event, whoever took them, and hands each person the ones they appear in.
            </p>
          </div>
          <div className="flex flex-col gap-2.5">
            {pairs.map((c) => (
              <div key={c.no} className="overflow-hidden rounded-2xl border border-white/[0.09] bg-white/[0.02]">
                <div className="flex items-start gap-[11px] px-[18px] py-[15px]">
                  <div className="mt-px flex h-5 w-5 flex-none items-center justify-center rounded-full border border-white/[0.16] text-xs leading-[18px] text-white/40">
                    ✕
                  </div>
                  <div className="min-w-0">
                    <div className="mb-1.5 font-mono text-[10.5px] font-semibold uppercase tracking-[0.13em] text-white/30">Not this</div>
                    <div className="text-[15.5px] leading-[1.5] tracking-[-0.008em] text-white/50 text-pretty">{c.no}</div>
                  </div>
                </div>
                <div className="flex items-start gap-[11px] border-t border-[#FF7A59]/20 bg-[#FF7A59]/[0.07] px-[18px] py-[15px]">
                  <div className="mt-px flex h-5 w-5 flex-none items-center justify-center rounded-full border border-[#FF7A59]/45 bg-[#FF7A59]/20 text-[11px] leading-[18px] text-[#FF9578]">
                    ✓
                  </div>
                  <div className="min-w-0">
                    <div className="mb-1.5 font-mono text-[10.5px] font-semibold uppercase tracking-[0.13em] text-[#FF9578]/90">This</div>
                    <div className="text-[15.5px] leading-[1.5] tracking-[-0.008em] text-[#F5F5F7] text-pretty">{c.yes}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-[78px] flex flex-wrap items-end justify-between gap-10 border-t border-white/[0.08] pt-11">
        <h2 className="text-[28px] font-bold leading-[1.08] tracking-[-0.028em] md:text-[38px]">
          Find yourself in the photos.
        </h2>
        <button
          onClick={() => navigate('/signup')}
          className="flex-none whitespace-nowrap rounded-full bg-[#FF7A59] px-8 py-4 text-[16.5px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.97]"
        >
          Sign up
        </button>
      </div>
    </div>
  )
}

export default About
