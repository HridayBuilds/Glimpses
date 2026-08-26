import { useNavigate } from 'react-router-dom'

function AppHeader({ title, backTo = '/app' }) {
  const navigate = useNavigate()

  return (
    <div className="sticky top-0 z-20 flex items-center gap-3.5 bg-[rgba(10,10,12,0.72)] px-5 py-3.5 backdrop-blur-2xl backdrop-saturate-[1.8]">
      <button
        onClick={() => navigate(backTo)}
        className="flex-none cursor-pointer border-none bg-transparent px-0.5 py-1 text-[16px] text-[#FF7A59]"
      >
        ‹ Back
      </button>
      <div className="flex-1 text-center text-[16px] font-semibold tracking-[-0.01em]">{title}</div>
      <div className="w-[52px] flex-none" />
    </div>
  )
}

export default AppHeader
