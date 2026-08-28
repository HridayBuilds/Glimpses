function EventMenu({ open, isOrganizer, onClose, onSettings, onShare, onLobby, onAnalytics, onLeave }) {
  if (!open) return null

  const items = isOrganizer
    ? [
        { label: 'Event Settings', onClick: onSettings },
        { label: 'Share Event', onClick: onShare },
        { label: 'Event Lobby', onClick: onLobby },
        { label: 'Event Analytics', onClick: onAnalytics },
      ]
    : [
        { label: 'Share Event', onClick: onShare },
        { label: 'Leave Event', onClick: onLeave, danger: true },
      ]

  return (
    <div onClick={onClose} className="fixed inset-0 z-[95] flex items-end justify-center bg-black/60">
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-[520px] rounded-t-[24px] border-t border-white/[0.14] bg-[rgba(22,22,26,0.9)] p-[22px] pb-7 backdrop-blur-[30px] backdrop-saturate-[1.8]"
      >
        <div className="mx-auto mb-[18px] h-1 w-[38px] rounded-full bg-white/[0.22]" />
        <div className="flex flex-col gap-2">
          {items.map(({ label, onClick, danger }) => (
            <button
              key={label}
              onClick={onClick}
              className={
                danger
                  ? 'w-full rounded-xl border border-[rgba(255,89,89,0.3)] bg-[rgba(255,89,89,0.14)] py-[15px] text-[15px] font-semibold text-[#FF8A8A] transition-transform duration-100 ease-out active:scale-[0.975]'
                  : 'w-full rounded-xl border border-white/[0.09] bg-white/[0.06] py-[15px] text-[15px] font-semibold text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]'
              }
            >
              {label}
            </button>
          ))}
        </div>
        <button onClick={onClose} className="mt-4 w-full py-1 text-[15px] font-medium text-white/50">
          Cancel
        </button>
      </div>
    </div>
  )
}

export default EventMenu
