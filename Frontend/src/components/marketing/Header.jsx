import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

function NavButton({ to, active, children, onClick }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`whitespace-nowrap py-1 text-[13px] tracking-[-0.005em] transition-colors duration-150 sm:text-[15px] ${
        active ? 'font-semibold text-[#F5F5F7]' : 'font-medium text-[#F5F5F7]/55 hover:text-[#F5F5F7]/80'
      }`}
    >
      {children}
    </Link>
  )
}

function Header() {
  const [menuOpen, setMenuOpen] = useState(false)
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
        <div className="hidden flex-1 items-center gap-[22px] sm:flex">
          <NavButton to="/about" active={location.pathname === '/about'}>
            About
          </NavButton>
          <NavButton to="/how-it-works" active={location.pathname === '/how-it-works'}>
            How it works
          </NavButton>
          <NavButton to="/privacy" active={location.pathname === '/privacy'}>
            Privacy
          </NavButton>
        </div>
        <div className="hidden items-center gap-3.5 sm:ml-0 sm:flex">
          <button
            onClick={() => navigate('/login')}
            className="whitespace-nowrap text-[15px] font-medium text-[#F5F5F7]/72"
          >
            Log in
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="whitespace-nowrap rounded-full bg-[#FF7A59] px-[16px] py-[7px] text-[13.5px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-95"
          >
            Sign up
          </button>
        </div>
        <button
          onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          className="ml-auto flex h-9 w-9 flex-none items-center justify-center rounded-full text-[#F5F5F7]/80 sm:hidden"
        >
          {menuOpen ? (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 4L16 16M16 4L4 16" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 5.5H17M3 10H17M3 14.5H17" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
          )}
        </button>
      </div>
      {menuOpen && (
        <div className="flex flex-col gap-1 border-t border-white/[0.06] px-4 py-3 sm:hidden">
          <NavButton to="/about" active={location.pathname === '/about'} onClick={() => setMenuOpen(false)}>
            About
          </NavButton>
          <NavButton
            to="/how-it-works"
            active={location.pathname === '/how-it-works'}
            onClick={() => setMenuOpen(false)}
          >
            How it works
          </NavButton>
          <NavButton to="/privacy" active={location.pathname === '/privacy'} onClick={() => setMenuOpen(false)}>
            Privacy
          </NavButton>
          <button
            onClick={() => {
              setMenuOpen(false)
              navigate('/login')
            }}
            className="whitespace-nowrap py-1 text-left text-[13px] font-medium text-[#F5F5F7]/72"
          >
            Log in
          </button>
          <button
            onClick={() => {
              setMenuOpen(false)
              navigate('/signup')
            }}
            className="whitespace-nowrap py-1 text-left text-[13px] font-medium text-[#F5F5F7]/72"
          >
            Sign up
          </button>
        </div>
      )}
    </div>
  )
}

export default Header
