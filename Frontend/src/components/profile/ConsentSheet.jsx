const CONSENT_POINTS = [
  'It is used only inside the events you have joined, never across events and never as a global identity.',
  'Removing it destroys the template immediately and stops future matching.',
  'Matches already made stay in those events — removing the selfie is not retroactive.',
]

function ConsentSheet({ open, onCancel, onAccept }) {
  if (!open) return null

  return (
    <div onClick={onCancel} className="fixed inset-0 z-[95] flex items-end justify-center bg-black/60">
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-[520px] rounded-t-[24px] border-t border-white/[0.14] bg-[rgba(22,22,26,0.9)] p-[22px] pb-7 backdrop-blur-[30px] backdrop-saturate-[1.8]"
      >
        <div className="mx-auto mb-[18px] h-1 w-[38px] rounded-full bg-white/[0.22]" />
        <div className="mb-2.5 text-[22px] font-bold tracking-[-0.018em]">Before you add a selfie</div>
        <div className="mb-4 text-[15.5px] leading-[1.62] text-white/60 text-pretty">
          Glimpses turns your selfie into an unlabeled face template and compares it against photos in the events
          you join. The selfie and the template are stored until you remove them.
        </div>
        <div className="mb-[22px] flex flex-col gap-2.5">
          {CONSENT_POINTS.map((point) => (
            <div key={point} className="flex items-start gap-2.5">
              <span className="text-[14px] leading-[1.6] text-[#FF9578]">—</span>
              <span className="text-[14.5px] leading-[1.6] text-white/55">{point}</span>
            </div>
          ))}
        </div>
        <div className="flex gap-2.5">
          <button
            onClick={onCancel}
            className="flex-1 rounded-xl border border-white/[0.11] bg-white/[0.08] py-[15px] text-[15px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Not now
          </button>
          <button
            onClick={onAccept}
            className="flex-1 rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Take a selfie
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConsentSheet
