import { test } from 'node:test'
import assert from 'node:assert/strict'
import { getUploadUrlWithRetry } from './uploadUrlRetry.js'

test('a temporary upload API throttle retries without pausing the batch', async () => {
  let calls = 0
  const delays = []
  const result = await getUploadUrlWithRetry('event-1', async () => {
    calls += 1
    if (calls === 1) throw { response: { status: 503 } }
    return { jobId: 'job-1', uploadUrl: 'https://example.invalid/upload' }
  }, async (ms) => delays.push(ms))

  assert.equal(calls, 2)
  assert.deepEqual(delays, [1500])
  assert.equal(result.jobId, 'job-1')
})

test('permission errors are not retried', async () => {
  let calls = 0
  await assert.rejects(getUploadUrlWithRetry('event-1', async () => {
    calls += 1
    throw { response: { status: 403 } }
  }, async () => {}))
  assert.equal(calls, 1)
})

test('persistent upload API failures stop after a bounded number of attempts', async () => {
  let calls = 0
  await assert.rejects(getUploadUrlWithRetry('event-1', async () => {
    calls += 1
    throw { response: { status: 500 } }
  }, async () => {}))
  assert.equal(calls, 4)
})
