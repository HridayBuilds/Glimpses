import { Link } from 'react-router-dom'

function AuthShell({ title, children, pt = 'pt-16' }) {
  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className={`mx-auto max-w-[460px] px-6 pb-10 ${pt}`}>
        <Link
          to="/"
          className="block text-center text-[15px] font-semibold uppercase tracking-[0.14em] text-white/40 transition-colors hover:text-white/60"
        >
          Glimpses
        </Link>
        <h1 className="mb-[26px] mt-6 text-center text-[34px] font-bold leading-[1.06] tracking-[-0.025em]">
          {title}
        </h1>
        {children}
      </div>
    </div>
  )
}

export default AuthShell
