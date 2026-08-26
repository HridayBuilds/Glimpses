function ConfirmDialog({ open, title, body, cta, danger, onCancel, onConfirm }) {
  if (!open) return null

  const ctaStyle = danger
    ? { background: 'rgba(255,89,89,0.16)', border: '1px solid rgba(255,89,89,0.34)', color: '#FF8A8A' }
    : { background: '#FF7A59', border: '1px solid #FF7A59', color: '#200C05' }

  return (
    <div
      onClick={onCancel}
      className="fixed inset-0 z-[96] flex items-center justify-center bg-black/62 p-6"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-[400px] rounded-[20px] border border-white/[0.13] bg-[rgba(24,24,28,0.92)] p-[22px] shadow-[0_30px_70px_rgba(0,0,0,0.6)] backdrop-blur-[30px] backdrop-saturate-[1.8]"
      >
        <div className="mb-2.5 text-[19px] font-bold tracking-[-0.016em]">{title}</div>
        <div className="mb-5 text-[15px] leading-[1.6] text-white/58 text-pretty">{body}</div>
        <div className="flex gap-2.5">
          <button
            onClick={onCancel}
            className="flex-1 rounded-xl border border-white/[0.11] bg-white/[0.08] py-3.5 text-[15px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            Keep it
          </button>
          <button
            onClick={onConfirm}
            style={ctaStyle}
            className="flex-1 rounded-xl py-3.5 text-[15px] font-semibold transition-transform duration-100 ease-out active:scale-[0.975]"
          >
            {cta}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDialog
