import api from './api'

export async function getEventInfo(eventId) {
  const { data } = await api.get(`/events/${eventId}/info`)
  return data
}

export async function joinEvent(accessCode) {
  const { data } = await api.post('/events/join', { accessCode })
  return data
}

export async function leaveEvent(eventId) {
  const { data } = await api.post(`/events/${eventId}/leave`)
  return data
}

export async function getAttendees(eventId, status) {
  const { data } = await api.get(`/events/${eventId}/attendees`, { params: { status } })
  return data.attendees
}

export async function admitAttendee(eventId, userId) {
  const { data } = await api.post(`/events/${eventId}/attendees/${userId}/admit`)
  return data
}

export async function denyAttendee(eventId, userId) {
  const { data } = await api.post(`/events/${eventId}/attendees/${userId}/deny`)
  return data
}

export async function ejectAttendee(eventId, userId) {
  const { data } = await api.post(`/events/${eventId}/attendees/${userId}/eject`)
  return data
}
