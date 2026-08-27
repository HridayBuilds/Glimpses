import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MarketingLayout from './components/marketing/MarketingLayout'
import Landing from './pages/marketing/Landing'
import About from './pages/marketing/About'
import HowItWorks from './pages/marketing/HowItWorks'
import MarketingPrivacy from './pages/marketing/Privacy'
import Signup from './pages/auth/Signup'
import Login from './pages/auth/Login'
import VerifyCode from './pages/auth/VerifyCode'
import ForgotPassword from './pages/auth/ForgotPassword'
import ResetPassword from './pages/auth/ResetPassword'
import RequireAuth from './components/auth/RequireAuth'
import Profile from './pages/app/Profile'
import SelfieInfo from './pages/app/SelfieInfo'
import Privacy from './pages/app/Privacy'
import Home from './pages/app/Home'
import CreateEvent from './pages/app/CreateEvent'
import JoinEvent from './pages/app/JoinEvent'
import JoinLink from './pages/app/JoinLink'
import EventEntry from './pages/app/EventEntry'
import Roster from './pages/app/Roster'
import EventSettings from './pages/app/EventSettings'
import ShareEvent from './pages/app/ShareEvent'
import EventAnalytics from './pages/app/EventAnalytics'
import UploadFlow from './pages/app/UploadFlow'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MarketingLayout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/about" element={<About />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/privacy" element={<MarketingPrivacy />} />
        </Route>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verify-email" element={<VerifyCode />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route
          path="/join"
          element={
            <RequireAuth>
              <JoinEvent />
            </RequireAuth>
          }
        />
        <Route
          path="/j/:code"
          element={
            <RequireAuth>
              <JoinLink />
            </RequireAuth>
          }
        />
        <Route
          path="/app"
          element={
            <RequireAuth>
              <Home />
            </RequireAuth>
          }
        />
        <Route
          path="/app/create"
          element={
            <RequireAuth>
              <CreateEvent />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId"
          element={
            <RequireAuth>
              <EventEntry />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId/roster"
          element={
            <RequireAuth>
              <Roster />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId/settings"
          element={
            <RequireAuth>
              <EventSettings />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId/share"
          element={
            <RequireAuth>
              <ShareEvent />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId/analytics"
          element={
            <RequireAuth>
              <EventAnalytics />
            </RequireAuth>
          }
        />
        <Route
          path="/app/events/:eventId/upload"
          element={
            <RequireAuth>
              <UploadFlow />
            </RequireAuth>
          }
        />
        <Route
          path="/app/profile"
          element={
            <RequireAuth>
              <Profile />
            </RequireAuth>
          }
        />
        <Route
          path="/app/profile/selfie-info"
          element={
            <RequireAuth>
              <SelfieInfo />
            </RequireAuth>
          }
        />
        <Route
          path="/app/privacy"
          element={
            <RequireAuth>
              <Privacy />
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
