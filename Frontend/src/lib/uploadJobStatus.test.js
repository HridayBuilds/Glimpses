import { test } from 'node:test'
import assert from 'node:assert/strict'
import { pollUploadJobs } from './uploadJobStatus.js'

test('one failed status request does not hide completed batches', async () => {
  const ids = Array.from({ length: 11 }, (_, index) => `job-${index}`)
  const fetchStatus = async (id) => {
    if (id === 'job-3') throw new Error('HTTP 500')
    return { jobId: id, status: 'SUCCESS', succeededCount: 1, failedCount: 0 }
  }

  const first = await pollUploadJobs(ids, fetchStatus)
  assert.equal(Object.keys(first.jobsById).length, 10)
  assert.equal(first.unreachableCount, 1)

  const requested = []
  const second = await pollUploadJobs(ids, async (id) => {
    requested.push(id)
    return { jobId: id, status: 'SUCCESS', succeededCount: 1, failedCount: 0 }
  }, first.jobsById)
  assert.deepEqual(requested, ['job-3'])
  assert.equal(Object.keys(second.jobsById).length, 11)
  assert.equal(second.unreachableCount, 0)
})

test('status polling never starts more than two Lambda requests at once', async () => {
  const ids = Array.from({ length: 11 }, (_, index) => `job-${index}`)
  let active = 0
  let peak = 0
  const result = await pollUploadJobs(ids, async (id) => {
    active += 1
    peak = Math.max(peak, active)
    await new Promise((resolve) => setTimeout(resolve, 1))
    active -= 1
    return { jobId: id, status: 'SUCCESS' }
  })

  assert.equal(peak <= 2, true)
  assert.equal(Object.keys(result.jobsById).length, 11)
})

test('a later uploaded batch can be added without losing earlier results', async () => {
  const first = await pollUploadJobs(['job-1'], async (id) => ({ jobId: id, status: 'SUCCESS' }))
  const requested = []
  const second = await pollUploadJobs(['job-1', 'job-2'], async (id) => {
    requested.push(id)
    return { jobId: id, status: 'EXTRACTING' }
  }, first.jobsById)

  assert.deepEqual(requested, ['job-2'])
  assert.equal(second.jobsById['job-1'].status, 'SUCCESS')
  assert.equal(second.jobsById['job-2'].status, 'EXTRACTING')
})
