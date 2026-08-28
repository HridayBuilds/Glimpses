import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

function ForgotPassword() {
  const { forgotPassword } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const { register, handleSubmit } = useForm({ defaultValues: { email: '' } })

  const onSubmit = async ({ email }) => {
    setSubmitting(true)
    try {
      await forgotPassword(email)
      navigate('/reset-password', { state: { email } })
    } catch (err) {
      toast.error(err.message || 'Could not send a reset code.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <div className="mx-auto max-w-[440px] px-6 pb-10 pt-16">
        <h1 className="mb-2.5 text-[32px] font-bold leading-[1.08] tracking-[-0.022em]">Reset your password</h1>
        <p className="mb-[30px] text-[16px] leading-[1.55] text-white/55 text-pretty">
          A six-digit code will be sent to the email associated with your account.
        </p>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-5 flex flex-col gap-[7px]">
            <label className="text-[13.5px] font-semibold text-white/82">Email</label>
            <input
              type="email"
              {...register('email', { required: true })}
              className="w-full rounded-xl border border-white/[0.16] bg-white/[0.09] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
          >
            {submitting ? 'Sending…' : 'Send code'}
          </button>
        </form>
        <Link to="/login" className="mt-[18px] block text-center text-[14.5px] text-white/55">
          Back to sign in
        </Link>
      </div>
    </div>
  )
}

export default ForgotPassword
