function SelfieToast({ visible, onAddSelfie, onDismiss }) {
  return (
    <div
      className={`${visible ? 'animate-enter' : 'animate-leave'} w-[min(360px,92vw)] rounded-2xl border border-white/[0.12] bg-[rgba(22,22,26,0.96)] p-4 shadow-[0_10px_40px_rgba(0,0,0,0.5)] backdrop-blur-[30px] backdrop-saturate-[1.8]`}
    >
      <div className="mb-1.5 text-[15.5px] font-semibold tracking-[-0.012em] text-[#F5F5F7]">
        You don't have a selfie yet
      </div>
      <div className="mb-3.5 text-[13.5px] leading-[1.55] text-white/60 text-pretty">
        Upload one for a seamless experience — Glimpses can then show you just the photos you're in.
      </div>
      <div className="flex gap-2">
        <button
          onClick={onDismiss}
          className="flex-1 rounded-lg border border-white/[0.11] bg-white/[0.08] py-2.5 text-[13.5px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]"
        >
          Later
        </button>
        <button
          onClick={onAddSelfie}
          className="flex-1 rounded-lg bg-[#FF7A59] py-2.5 text-[13.5px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
        >
          Upload selfie now
        </button>
      </div>
    </div>
  )
}

export default SelfieToast
