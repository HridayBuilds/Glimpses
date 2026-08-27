import jsQR from 'jsqr'

// Matches the alphabet the backend actually generates access codes from
// (Backend/events/src/Manager/manager.py: ACCESS_CODE_ALPHABET) — excludes 0/1/I/O.
const CODE_CHARS = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
const JOIN_PATH_RE = new RegExp(`/j/([${CODE_CHARS}]{6})`, 'i')
const BARE_CODE_RE = new RegExp(`^[${CODE_CHARS}]{6}$`, 'i')

// The backend's QR image encodes a join URL (".../j/{code}"). The domain
// itself (e.g. a CloudFront default domain) can easily contain another run
// of 6 code-alphabet characters, so the code must be pulled from the /j/
// path specifically — a bare "first 6 matching chars anywhere" scan matches
// the domain before it ever reaches the real code. Fall back to treating
// the whole scanned string as a bare code only when it isn't a URL at all.
export function extractAccessCode(text) {
  if (!text) return null
  const trimmed = text.trim()
  const pathMatch = trimmed.match(JOIN_PATH_RE)
  if (pathMatch) return pathMatch[1].toUpperCase()
  return BARE_CODE_RE.test(trimmed) ? trimmed.toUpperCase() : null
}

export function decodeQRFromImageData(imageData) {
  return jsQR(imageData.data, imageData.width, imageData.height)?.data ?? null
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

export async function decodeQRFromFile(file) {
  const url = URL.createObjectURL(file)
  try {
    const img = await loadImage(url)
    const canvas = document.createElement('canvas')
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(img, 0, 0)
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    return decodeQRFromImageData(imageData)
  } finally {
    URL.revokeObjectURL(url)
  }
}
