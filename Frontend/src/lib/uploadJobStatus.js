const FINISHED_STATES = new Set(['SUCCESS', 'FAILED'])

export async function pollUploadJobs(jobIds, fetchStatus, previousJobs = {}) {
  const jobsById = { ...previousJobs }
  const pendingIds = jobIds.filter((id) => !FINISHED_STATES.has(jobsById[id]?.status))
  let unreachableCount = 0
  let nextIndex = 0

  // The account may allow only 10 concurrent Lambdas. Polling every batch at
  // once can throttle this API while ingestion Lambdas are also running.
  async function worker() {
    while (nextIndex < pendingIds.length) {
      const id = pendingIds[nextIndex++]
      try {
        jobsById[id] = await fetchStatus(id)
      } catch {
        unreachableCount += 1
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(2, pendingIds.length) }, () => worker()))

  return { jobsById, unreachableCount }
}
