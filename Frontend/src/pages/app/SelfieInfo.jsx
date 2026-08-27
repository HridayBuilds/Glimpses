import AppHeader from '../../components/app/AppHeader'

const CONSENT_POINTS = [
  'It is used only inside the events you have joined. It is never compared across events and never treated as a global identity.',
  'Removing your selfie destroys the template immediately and stops any future matching.',
  'Matches already made stay in those events, even after you remove the selfie. Removing it does not undo matches you already have.',
]

function SelfieInfo() {
  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="About your selfie" backTo="/app/profile" />
      <div className="mx-auto max-w-[620px] px-6 pb-[60px] pt-5">
        <h1 className="mb-3.5 mt-2 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">Info</h1>
        <p className="mb-[22px] text-[15.5px] leading-[1.62] text-white/60 text-pretty">
          Glimpses turns your selfie into an unlabeled face template and compares it against photos in the events you
          join. Both the selfie and the template are stored until you remove them.
        </p>
        {CONSENT_POINTS.map((point) => (
          <div key={point} className="border-t border-white/[0.08] py-5">
            <div className="text-[15.5px] leading-[1.62] text-white/58 text-pretty">{point}</div>
          </div>
        ))}
        <div className="border-t border-white/[0.08]" />
      </div>
    </div>
  )
}

export default SelfieInfo
