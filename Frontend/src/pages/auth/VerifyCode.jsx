import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'del']

function VerifyCode() {
  const { confirmSignUp, resendConfirmationCode } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const email = location.state?.email

  const [code, setCode] = useState('')
  const [codeErr, setCodeErr] = useState(false)
  const [verifyDone, setVerifyDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!email) navigate('/signup', { replace: true })
  }, [email, navigate])

  useEffect(() => {
    if (email && !verifyDone) inputRef.current?.focus()
  }, [email, verifyDone])

  if (!email) return null

  const tapKey = (v) => () => {
    if (v === 'del') return setCode((c) => c.slice(0, -1))
    setCodeErr(false)
    setCode((c) => (c.length >= 6 ? c : c + v))
  }

  const onTypeCode = (e) => {
    setCodeErr(false)
    setCode(e.target.value.replace(/\D/g, '').slice(0, 6))
  }

  const submitCode = async () => {
    if (code.length !== 6) return setCodeErr(true)
    setSubmitting(true)
    try {
      await confirmSignUp(email, code)
      setVerifyDone(true)
    } catch {
      setCodeErr(true)
    } finally {
      setSubmitting(false)
    }
  }

  const resendCode = async () => {
    setCode('')
    setCodeErr(false)
    try {
      await resendConfirmationCode(email)
      toast.success(`New code sent to ${email}`)
    } catch (err) {
      toast.error(err.message || 'Could not resend the code.')
    }
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="mx-auto max-w-[440px] px-6 pb-10 pt-16">
        {verifyDone ? (
          <div className="pt-10">
            <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[#FF7A59]/40 bg-[#FF7A59]/[0.16] text-[26px] text-[#FF9578]">
              ✓
            </div>
            <h1 className="mb-2.5 mt-6 text-[32px] font-bold leading-[1.08] tracking-[-0.022em]">Email confirmed</h1>
            <p className="mb-8 text-[16px] leading-[1.55] text-white/55 text-pretty">
              {email} is verified. Log in to get started.
            </p>
            <div className="flex flex-col gap-2.5">
              <button
                onClick={() => navigate('/login', { state: { email, justVerified: true } })}
                className="w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975]"
              >
                Log in
              </button>
            </div>
          </div>
        ) : (
          <div>
            <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.022em]">
              Enter the code we emailed
            </h1>
            <p className="mb-[30px] text-[16px] leading-[1.55] text-white/55 text-pretty">
              Enter the six-digit code sent to {email}
            </p>
            <div className="relative mb-4">
              <input
                ref={inputRef}
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                autoComplete="one-time-code"
                maxLength={6}
                value={code}
                onChange={onTypeCode}
                aria-label="Six-digit verification code"
                className="absolute inset-0 z-10 h-full w-full cursor-default opacity-0"
              />
              <div className="flex gap-2.5">
                {[0, 1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="flex aspect-[0.78] flex-1 items-center justify-center rounded-xl text-[26px] font-semibold tabular-nums transition-colors duration-75"
                    style={{
                      background: code[i] ? 'rgba(255,255,255,0.09)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${codeErr ? 'rgba(255,89,89,0.45)' : i === code.length ? 'rgba(255,122,89,0.7)' : 'rgba(255,255,255,0.09)'}`,
                    }}
                  >
                    {code[i] || ''}
                  </div>
                ))}
              </div>
            </div>
            {codeErr && (
              <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-[#FF5959]/25 bg-[#FF5959]/[0.09] px-3.5 py-3">
                <span className="text-[14px] leading-[1.5] text-[#FFBEBE]/90">
                  That code has expired or is incorrect. Request a new one.
                </span>
              </div>
            )}
            <div className="mb-[26px] flex flex-wrap gap-2">
              {KEYS.map((k) => (
                <button
                  key={k}
                  onClick={tapKey(k)}
                  className="min-w-0 flex-[1_1_28%] rounded-xl border border-white/[0.16] bg-white/[0.09] py-[15px] text-[19px] font-medium tabular-nums text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-95"
                >
                  {k === 'del' ? '⌫' : k}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button
                onClick={resendCode}
                className="flex-1 rounded-xl border border-white/[0.09] bg-white/[0.07] py-[15px] text-[15px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975]"
              >
                Send a new code
              </button>
              <button
                onClick={submitCode}
                disabled={submitting}
                className="flex-1 rounded-xl bg-[#FF7A59] py-[15px] text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
              >
                Confirm
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default VerifyCode
