import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import AuthShell from '../../components/auth/AuthShell'
import { useAuth } from '../../context/AuthContext'

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitting, setSubmitting] = useState(false)
  const { register, handleSubmit } = useForm({ defaultValues: { email: location.state?.email || '', password: '' } })

  const onSubmit = async ({ email, password }) => {
    setSubmitting(true)
    try {
      await login(email, password)
      const dest = location.state?.from?.pathname || '/app'
      navigate(dest, { replace: true, state: { promptSelfie: true } })
    } catch (err) {
      if (err.code === 'UserNotConfirmedException') {
        toast.error('Verify your email before logging in.')
        navigate('/verify-email', { state: { email } })
        return
      }
      toast.error(err.message || 'Could not log in.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell title="Login">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3.5">
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
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="mt-1.5 w-full rounded-xl bg-[#FF7A59] py-4 text-[16px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
        >
          {submitting ? 'Logging in…' : 'Log in'}
        </button>
        <Link to="/forgot-password" className="mt-1 block w-full text-center text-[14.5px] text-white/55">
          Forgot password
        </Link>
      </form>
      <div className="my-7 h-px bg-white/[0.07]" />
      <div className="text-center text-[15px] text-white/55">
        New here?{' '}
        <Link to="/signup" className="font-semibold">
          Create an account
        </Link>
      </div>
    </AuthShell>
  )
}

export default Login
