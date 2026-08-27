function AddSelfiePrompt({ open, onAddSelfie, onDismiss }) {
  if (!open) return null

  return (
    <div onClick={onDismiss} className="fixed inset-0 z-[95] flex items-end justify-center bg-black/60">
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-[520px] rounded-t-[24px] border-t border-white/[0.14] bg-[rgba(22,22,26,0.9)] p-[22px] pb-7 backdrop-blur-[30px] backdrop-saturate-[1.8]"
      >
        <div className="mx-auto mb-[18px] h-1 w-[38px] rounded-full bg-white/[0.22]" />
        <div className="mb-2.5 text-[22px] font-bold tracking-[-0.018em]">Add a profile selfie?</div>
        <div className="mb-[22px] text-[15.5px] leading-[1.62] text-white/60 text-pretty">
          It's what makes "just the photos I'm in" possible. You can always add it later from your profile.
        </div>
        <div className="flex gap-2.5">
          <button
            onClick={onDismiss}
            className="flex-1 rounded-xl border border-white/[0.11] bg-white/[0.08] py-[15px] text-[15px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Maybe later
          </button>
          <button
            onClick={onAddSelfie}
            className="flex-1 rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Add a selfie
          </button>
        </div>
      </div>
    </div>
  )
}

export default AddSelfiePrompt
