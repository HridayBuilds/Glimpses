import { Link } from 'react-router-dom'

function ComingSoon({ label }) {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-4 bg-[#08080A] px-6 text-center text-[#F5F5F7]">
      <div className="text-2xl font-semibold">{label} — coming soon</div>
      <p className="max-w-sm text-white/50">This screen is part of a later build phase.</p>
      <Link to="/" className="text-[#FF7A59]">
        Back to Glimpses
      </Link>
    </div>
  )
}

export default ComingSoon
