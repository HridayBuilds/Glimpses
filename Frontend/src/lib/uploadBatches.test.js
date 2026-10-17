import { test } from 'node:test'
import assert from 'node:assert/strict'
import { planUploadBatches } from './uploadBatches.js'

test('a 177-photo selection stays in bounded, ordered batches', () => {
  const files = Array.from({ length: 177 }, (_, index) => ({ name: `${index}.jpg`, size: 1024 }))
  const batches = planUploadBatches(files)
  assert.deepEqual(batches.map((batch) => batch.length), [25, 25, 25, 25, 25, 25, 25, 2])
  assert.deepEqual(batches.flat(), files)
})

test('large iPhone photos split before a batch exceeds the byte budget', () => {
  const files = Array.from({ length: 5 }, (_, index) => ({ name: `${index}.heic`, size: 20 * 1024 * 1024 }))
  assert.deepEqual(planUploadBatches(files).map((batch) => batch.length), [2, 2, 1])
})
