const RETRYABLE_STATUSES = new Set([408, 429, 500, 502, 503, 504])

export async function getUploadUrlWithRetry(
  eventId,
  request,
  wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
) {
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      return await request(eventId)
    } catch (error) {
      const status = error.response?.status
      const retryable = error.code !== 'ERR_CANCELED' && (status == null || RETRYABLE_STATUSES.has(status))
      if (!retryable || attempt === 3) throw error
      await wait(1500 * 2 ** attempt)
    }
  }
}
