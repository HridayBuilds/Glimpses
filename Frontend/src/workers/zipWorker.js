import JSZip from 'jszip'

self.onmessage = async ({ data }) => {
  try {
    const zip = new JSZip()
    data.files.forEach((file, index) => {
      zip.file(`${String(index + 1).padStart(3, '0')}-${file.name}`, file)
    })
    const blob = await zip.generateAsync(
      { type: 'blob', compression: 'STORE', streamFiles: true },
      ({ percent }) => self.postMessage({ type: 'progress', percent: Math.round(percent) }),
    )
    self.postMessage({ type: 'done', blob })
  } catch (error) {
    self.postMessage({ type: 'error', message: error?.message || 'Could not prepare these photos' })
  }
}
