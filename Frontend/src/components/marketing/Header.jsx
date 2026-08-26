import { Link, useLocation, useNavigate } from 'react-router-dom'

function NavButton({ to, active, children }) {
  return (
    <Link
      to={to}
      className={`whitespace-nowrap py-1 text-[13px] tracking-[-0.005em] transition-colors duration-150 sm:text-[15px] ${
        active ? 'font-semibold text-[#F5F5F7]' : 'font-medium text-[#F5F5F7]/55 hover:text-[#F5F5F7]/80'
      }`}
    >
      {children}
    </Link>
  )
}

function Header() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div
      data-glass
      className="sticky top-0 z-40 border-b border-white/[0.06] bg-[#08080A]/[0.68] backdrop-blur-2xl backdrop-saturate-[1.8]"
    >
      <div className="mx-auto flex max-w-[1080px] items-center gap-3 px-4 py-3.5 sm:gap-7 sm:px-6">
        <Link
          to="/"
          className="whitespace-nowrap py-0.5 text-[13px] font-bold uppercase tracking-[0.13em] text-[#F5F5F7] sm:text-[15px]"
        >
          Glimpses
        </Link>
        <div className="flex flex-1 items-center gap-3 sm:gap-[22px]">
          <NavButton to="/about" active={location.pathname === '/about'}>
            About
          </NavButton>
          <NavButton to="/how-it-works" active={location.pathname === '/how-it-works'}>
            How it works
          </NavButton>
        </div>
        <div className="flex items-center gap-2 sm:gap-3.5">
          <button
            onClick={() => navigate('/login')}
            className="whitespace-nowrap text-[13px] font-medium text-[#F5F5F7]/72 sm:text-[15px]"
          >
            Log in
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="whitespace-nowrap rounded-full bg-[#FF7A59] px-4 py-2 text-[13px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-95 sm:px-[22px] sm:py-2.5 sm:text-[14.5px]"
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  )
}

export default Header
