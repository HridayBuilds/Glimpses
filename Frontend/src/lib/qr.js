import jsQR from 'jsqr'

// Matches the alphabet the backend actually generates access codes from
// (Backend/events/src/Manager/manager.py: ACCESS_CODE_ALPHABET) — excludes 0/1/I/O.
const ACCESS_CODE_RE = /[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{6}/i

// The backend's QR image encodes a join URL (".../j/{code}"), but that
// domain isn't wired to anything the browser can navigate to yet — so
// instead of following the URL, pull the access code straight out of
// whatever text the QR decodes to and feed it into the same join call
// the manual-entry tab uses.
export function extractAccessCode(text) {
  if (!text) return null
  const match = text.trim().match(ACCESS_CODE_RE)
  return match ? match[0].toUpperCase() : null
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
