import axios from 'axios'
import api from './api'

export async function getProfile() {
  const { data } = await api.get('/profile')
  return data
}

export async function updateProfile(displayName) {
  const { data } = await api.put('/profile', { displayName })
  return data
}

// Presigned-PUT flow: mint the URL, upload the bytes directly to S3 (no auth
// header, not through the `api` instance), then confirm so the backend can
// run face detection on what actually landed.
export async function uploadSelfie(file) {
  const {
    data: { uploadUrl },
  } = await api.put('/profile/selfie')
  await axios.put(uploadUrl, file, {
    headers: { 'Content-Type': file.type, 'Cache-Control': 'private, max-age=86400' },
  })
  const { data } = await api.post('/profile/selfie/confirm')
  return data
}

export async function deleteSelfie() {
  const { data } = await api.delete('/profile/selfie')
  return data
}
