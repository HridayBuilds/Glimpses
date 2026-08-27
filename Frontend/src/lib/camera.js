export function cameraErrorMessage(err) {
  if (err?.name === 'NotFoundError' || err?.name === 'OverconstrainedError') {
    return 'No camera found on this device.'
  }
  if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
    return 'Camera access was denied.'
  }
  return 'Could not access your camera.'
}
