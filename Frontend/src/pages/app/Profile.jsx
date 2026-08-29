import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import AppHeader from '../../components/app/AppHeader'
import ImageSlot from '../../components/common/ImageSlot'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import SelfieOptionsSheet from '../../components/profile/SelfieOptionsSheet'
import CameraCapture from '../../components/profile/CameraCapture'
import { useAuth } from '../../context/AuthContext'
import { getProfile, updateProfile, uploadSelfie, deleteSelfie } from '../../lib/profileApi'

function Profile() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)

  const [optionsOpen, setOptionsOpen] = useState(false)
  const [cameraOpen, setCameraOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  const { data: profile, isLoading, isError } = useQuery({ queryKey: ['profile'], queryFn: getProfile })

  const {
    register,
    handleSubmit,
    formState: { isDirty, isSubmitting },
  } = useForm({ values: { displayName: profile?.displayName ?? '' } })

  const invalidateProfile = () => queryClient.invalidateQueries({ queryKey: ['profile'] })

  const saveNameMutation = useMutation({
    mutationFn: (displayName) => updateProfile(displayName),
    onSuccess: () => {
      invalidateProfile()
      toast.success('Name updated')
    },
    onError: () => toast.error('Could not update your name.'),
  })

  const uploadSelfieMutation = useMutation({
    mutationFn: (file) => uploadSelfie(file),
    onSuccess: () => {
      invalidateProfile()
      toast.success('Selfie saved — matching starts now')
    },
    onError: () => toast.error('Something went wrong — try a different selfie.'),
  })

  const deleteSelfieMutation = useMutation({
    mutationFn: deleteSelfie,
    onSuccess: () => {
      invalidateProfile()
      toast.success('Selfie deleted — matching stopped')
    },
    onError: () => toast.error('Could not delete your selfie.'),
  })

  const onSaveName = handleSubmit(({ displayName }) => saveNameMutation.mutateAsync(displayName))

  const onTakeSelfie = () => {
    setOptionsOpen(false)
    setCameraOpen(true)
  }

  const onChooseFile = () => {
    setOptionsOpen(false)
    fileInputRef.current?.click()
  }

  const saveSelfieFile = async (file) => {
    setUploading(true)
    try {
      await uploadSelfieMutation.mutateAsync(file)
    } finally {
      setUploading(false)
    }
  }

  const onFileChange = async (e) => {
    const file = e.target.files[0]
    e.target.value = ''
    if (!file) return
    await saveSelfieFile(file)
  }

  const onCameraCapture = async (file) => {
    setCameraOpen(false)
    await saveSelfieFile(file)
  }

  const onConfirmDelete = async () => {
    setDeleteOpen(false)
    await deleteSelfieMutation.mutateAsync()
  }

  const onSignOut = () => {
    logout()
    navigate('/login')
  }

  const hasSelfie = Boolean(profile?.selfieUrl)
  const selfieTitle = hasSelfie ? 'Your selfie' : 'No selfie yet'
  const selfieBody = hasSelfie
    ? "Matching runs automatically across every event you're part of. You can replace your selfie anytime — your previous face template is deleted as soon as the new one is created."
    : 'Without one, you still see everything in an event; you just cannot filter to the photos you appear in.'
  const selfieCta = hasSelfie ? 'Replace selfie' : 'Add a selfie'

  return (
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="Account" />
      <div className="mx-auto max-w-[460px] px-5 pb-20 pt-[22px]">
        {isLoading && <LoadingSpinner messages={['Loading your profile…', 'Almost there…']} />}
        {isError && <p className="text-[15px] text-white/45">Couldn't load your profile. Try again shortly.</p>}

        {profile && (
          <>
            <div className="mb-3 text-[12px] font-semibold uppercase tracking-[0.09em] text-white/36">
              Profile selfie
            </div>
            <div className="flex items-center gap-4 rounded-[18px] border border-white/[0.08] bg-white/[0.05] p-[18px]">
              <div className="h-[76px] w-[76px] flex-none overflow-hidden rounded-2xl">
                <ImageSlot src={profile.selfieUrl} label={hasSelfie ? 'selfie' : 'none'} />
              </div>
              <div className="min-w-0">
                <div className="mb-[5px] text-[15.5px] font-semibold tracking-[-0.01em]">{selfieTitle}</div>
                <div className="text-[14px] leading-[1.55] text-white/50">
                  {selfieBody}{' '}
                  <Link to="/app/profile/selfie-info" className="font-medium text-[#FF7A59]">
                    info
                  </Link>
                </div>
              </div>
            </div>
            <div className="mt-3 flex gap-2.5">
              <button
                onClick={() => setOptionsOpen(true)}
                disabled={uploading}
                className="flex-1 rounded-xl border border-white/10 bg-white/[0.07] py-3.5 text-[15px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
              >
                {uploading ? 'Checking your selfie…' : selfieCta}
              </button>
              {hasSelfie && (
                <button
                  onClick={() => setDeleteOpen(true)}
                  disabled={uploading}
                  className="flex-1 rounded-xl border border-[#FF5959]/28 bg-[#FF5959]/10 py-3.5 text-[15px] font-medium text-[#FF8A8A] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
                >
                  Delete selfie
                </button>
              )}
            </div>
            <p className="my-3.5 mb-[30px] text-[13.5px] leading-[1.6] text-white/40 text-pretty">
              Deleting your selfie removes your face template and stops future matching. Photos you've already been
              matched to won't be affected.
            </p>

            <form onSubmit={onSaveName}>
              <div className="mb-3.5 flex flex-col gap-[7px]">
                <label className="text-[13.5px] font-semibold text-white/82">Full Name</label>
                <input
                  {...register('displayName', { required: true })}
                  className="w-full rounded-xl border border-white/[0.09] bg-white/[0.06] px-4 py-[14px] text-[16px] text-[#F5F5F7] outline-none"
                />
                {isDirty && (
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="mt-1 w-full rounded-md bg-[#FF7A59] py-3 text-[15px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.975] disabled:opacity-60"
                  >
                    Save
                  </button>
                )}
              </div>
            </form>
            <div className="mb-[30px] flex flex-col gap-[7px]">
              <label className="text-[13.5px] font-semibold text-white/82">Email</label>
              <div className="w-full rounded-xl border border-white/[0.07] bg-white/[0.03] px-4 py-[14px] text-[16px] text-white/45">
                {profile.email}
              </div>
            </div>

            <div className="mb-[22px] h-px bg-white/[0.07]" />
            <Link to="/app/privacy" className="text-[15px] font-medium">
              What Glimpses does with faces
            </Link>
            <button
              onClick={onSignOut}
              className="mt-[26px] block w-full rounded-xl border border-white/10 bg-white/[0.07] py-[15px] text-[15.5px] font-medium text-[#F5F5F7] transition-transform duration-100 ease-out active:scale-[0.98]"
            >
              Sign out
            </button>
          </>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.heic,image/jpeg,image/png,image/heic"
        className="hidden"
        onChange={onFileChange}
      />

      <SelfieOptionsSheet
        open={optionsOpen}
        onCancel={() => setOptionsOpen(false)}
        onTakeSelfie={onTakeSelfie}
        onChooseFile={onChooseFile}
      />

      <CameraCapture open={cameraOpen} onCancel={() => setCameraOpen(false)} onCapture={onCameraCapture} />

      <ConfirmDialog
        open={deleteOpen}
        title="Delete your selfie?"
        body="The face template is destroyed and no new photos will be matched to you. Photos you were already matched to stay in their events. You can add a new selfie later."
        cta="Delete selfie"
        danger
        onCancel={() => setDeleteOpen(false)}
        onConfirm={onConfirmDelete}
      />
    </div>
  )
}

export default Profile
