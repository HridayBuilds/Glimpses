export const MAX_BATCH_FILES = 25
export const MAX_BATCH_BYTES = 50 * 1024 * 1024

export function planUploadBatches(files) {
  const batches = []
  let batch = []
  let bytes = 0
  for (const file of files) {
    if (batch.length && (batch.length >= MAX_BATCH_FILES || bytes + file.size > MAX_BATCH_BYTES)) {
      batches.push(batch)
      batch = []
      bytes = 0
    }
    batch.push(file)
    bytes += file.size
  }
  if (batch.length) batches.push(batch)
  return batches
}

export function zipFilesInWorker(files, onProgress) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL('../workers/zipWorker.js', import.meta.url), { type: 'module' })
    worker.onmessage = ({ data }) => {
      if (data.type === 'progress') onProgress(data.percent)
      if (data.type === 'done') {
        worker.terminate()
        resolve(data.blob)
      }
      if (data.type === 'error') {
        worker.terminate()
        reject(new Error(data.message))
      }
    }
    worker.onerror = (error) => {
      worker.terminate()
      reject(error)
    }
    worker.postMessage({ files })
  })
}
