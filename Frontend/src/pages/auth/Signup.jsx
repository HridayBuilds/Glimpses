import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import AuthShell from '../../components/auth/AuthShell'
import { useAuth } from '../../context/AuthContext'

function passwordChecks(pw) {
  return [/[a-z]/.test(pw), /[A-Z]/.test(pw), /[0-9]/.test(pw), pw.length >= 8]
}

function Signup() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({ defaultValues: { name: '', email: '', password: '', confirmPassword: '' } })

  const pw = watch('password') || ''
  const pw2 = watch('confirmPassword') || ''
  const checks = passwordChecks(pw)
  const score = checks.filter(Boolean).length
  const missing = []
  if (!checks[3]) missing.push('8 characters')
  if (!checks[1]) missing.push('an uppercase letter')
  if (!checks[0]) missing.push('a lowercase letter')
  if (!checks[2]) missing.push('a number')
  const segColor = ['rgba(255,255,255,0.12)', '#FF6B6B', '#E0C15C', '#E0C15C', '#6FD8B0'][pw.length ? score : 0]
  const pwOk = score === 4
  const pwMismatch = pw2.length > 0 && pw2 !== pw
  const pwMatch = pwOk && pw2 === pw

  const onSubmit = async ({ name, email, password }) => {
    if (!pwOk) return toast.error('Password needs ' + missing.join(', '))
    if (pw2 !== pw) return toast.error('Both passwords need to match')
    setSubmitting(true)
    try {
      await signUp(name, email, password)
      navigate('/verify-email', { state: { email } })
    } catch (err) {
      toast.error(err.message || 'Could not create your account.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell title="Sign up" pt="pt-14">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <div className="flex flex-col gap-[7px]">
          <label className="text-[13.5px] font-semibold text-white/82">Full Name</label>
          <input
            {...register('name', { required: true })}
            className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
          />
          <div className="text-[12.5px] text-white/35">Shown on photos you upload.</div>
        </div>
        <div className="flex flex-col gap-[7px]">
          <label className="text-[13.5px] font-semibold text-white/82">Email</label>
          <input
            type="email"
            {...register('email', { required: true })}
            className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
          />
        </div>
        <div className="flex flex-col gap-[7px]">
          <label className="text-[13.5px] font-semibold text-white/82">Password</label>
          <input
            type="password"
            {...register('password', { required: true })}
            className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
          />
          <div className="mt-[3px] flex gap-[5px]">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-1 flex-1 rounded-full transition-colors duration-200"
                style={{ background: pw.length && i < score ? segColor : 'rgba(255,255,255,0.12)' }}
              />
            ))}
          </div>
          <div className="mt-1 flex justify-between gap-2.5">
            <div className="text-[12.5px] text-white/40">
              {missing.length ? 'Needs ' + missing.join(', ') : 'Meets every requirement'}
            </div>
            <div
              className="whitespace-nowrap text-[12.5px] font-semibold"
              style={{ color: score < 3 ? '#FF8A8A' : score < 4 ? '#E8CE74' : '#8FE3B8' }}
            >
              {!pw.length ? '' : score < 3 ? 'Weak' : score < 4 ? 'Almost there' : 'Strong'}
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-[7px]">
          <label className="text-[13.5px] font-semibold text-white/82">Confirm Password</label>
          <input
            type="password"
            {...register('confirmPassword', { required: true })}
            className="w-full rounded-xl border bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none transition-colors duration-150"
            style={{
              borderColor: pw2.length === 0 ? 'rgba(255,255,255,0.09)' : pw2 === pw ? 'rgba(111,216,176,0.45)' : 'rgba(255,89,89,0.45)',
            }}
          />
          {pwMismatch && <div className="text-[12.5px] text-[#FF8A8A]">Both passwords need to match.</div>}
        </div>
        {errors.name || errors.email ? (
          <div className="text-[12.5px] text-[#FF8A8A]">Name and email are required.</div>
        ) : null}
        <button
          type="submit"
          disabled={submitting}
          className="mt-1.5 w-full rounded-xl py-4 text-[16px] font-semibold tracking-[-0.005em] transition-transform duration-100 ease-out active:scale-[0.975] disabled:cursor-not-allowed"
          style={{
            background: pwMatch ? '#FF7A59' : 'rgba(255,255,255,0.07)',
            color: pwMatch ? '#200C05' : 'rgba(245,245,247,0.4)',
          }}
        >
          {submitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <div className="my-7 h-px bg-white/[0.07]" />
      <div className="text-center text-[15px] text-white/55">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold">
          Log in
        </Link>
      </div>
    </AuthShell>
  )
}

export default Signup
