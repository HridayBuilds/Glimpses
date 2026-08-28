// cascadeDelete runs asynchronously (fire-and-forget Lambda invoke), so refetching
// right after a delete call races against work that hasn't landed in DynamoDB yet.
// Removing the known-deleted IDs from the cache directly sidesteps that race.
export function removePhotosFromCache(queryClient, eventId, deletedPhotoIDs) {
  if (!deletedPhotoIDs.length) return
  const deletedSet = new Set(deletedPhotoIDs)

  queryClient.setQueryData(['events', eventId, 'photos', 'mine'], (old) =>
    old ? { ...old, photos: old.photos.filter((p) => !deletedSet.has(p.photoID)) } : old,
  )
  queryClient.setQueryData(['events', eventId, 'photos', 'all'], (old) =>
    old
      ? { ...old, pages: old.pages.map((page) => ({ ...page, photos: page.photos.filter((p) => !deletedSet.has(p.photoID)) })) }
      : old,
  )
}
