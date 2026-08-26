import { Outlet } from 'react-router-dom'
import Header from './Header'

function MarketingLayout() {
  return (
    <div className="min-h-svh bg-[#08080A] text-[#F5F5F7]">
      <Header />
      <Outlet />
    </div>
  )
}

export default MarketingLayout
