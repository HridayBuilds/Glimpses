function SelfieOptionsSheet({ open, onCancel, onTakeSelfie, onChooseFile }) {
  if (!open) return null

  return (
    <div onClick={onCancel} className="fixed inset-0 z-[95] flex items-end justify-center bg-black/60">
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-[520px] rounded-t-[24px] border-t border-white/[0.14] bg-[rgba(22,22,26,0.9)] p-[22px] pb-7 backdrop-blur-[30px] backdrop-saturate-[1.8]"
      >
        <div className="mx-auto mb-[18px] h-1 w-[38px] rounded-full bg-white/[0.22]" />
        <div className="mb-5 text-[22px] font-bold tracking-[-0.018em]">Add a selfie</div>
        <div className="flex flex-col gap-2.5">
          <button
            onClick={onTakeSelfie}
            className="w-full rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Take a selfie
          </button>
          <button
            onClick={onChooseFile}
            className="w-full rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Choose from files
          </button>
        </div>
        <button
          onClick={onCancel}
          className="mt-4 w-full py-1 text-[15px] font-medium text-white/50"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

export default SelfieOptionsSheet
