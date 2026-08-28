import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

function ResetPassword() {
  const { confirmPassword } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const email = location.state?.email
  const [submitting, setSubmitting] = useState(false)
  const { register, handleSubmit } = useForm({ defaultValues: { code: '', password: '' } })

  useEffect(() => {
    if (!email) navigate('/forgot-password', { replace: true })
  }, [email, navigate])

  if (!email) return null

  const onSubmit = async ({ code, password }) => {
    setSubmitting(true)
    try {
      await confirmPassword(email, code, password)
      toast.success('Password reset — log in with your new password.')
      navigate('/login')
    } catch (err) {
      toast.error(err.message || 'Could not reset your password.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="mx-auto max-w-[440px] px-6 pb-10 pt-16">
        <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.022em]">New password</h1>
        <p className="mb-7 text-[16px] leading-[1.55] text-white/55">Enter your code and set a new password.</p>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-[7px]">
            <label className="text-[13.5px] font-semibold text-white/82">Six-digit code</label>
            <input
              {...register('code', { required: true })}
              className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[20px] tracking-[0.22em] tabular-nums text-[#F5F5F7] outline-none"
            />
          </div>
          <div className="flex flex-col gap-[7px]">
            <label className="text-[13.5px] font-semibold text-white/82">New password</label>
            <input
              type="password"
              {...register('password', { required: true })}
              className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="mt-1 w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
          >
            {submitting ? 'Setting password…' : 'Set password and log in'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default ResetPassword
