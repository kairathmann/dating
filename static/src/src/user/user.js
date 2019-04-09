import { Record } from 'immutable'

export const User = new Record({
  id: null,
  firstName: null,
  email: null,
  photoURL: null,
  createdAt: new Date(),
  tagline: null,
  bio: null,
  gender: null,
  sexuality: null,
  age: 0, //TODO: when moving to new backend - this is not needed - can use birthday
  birthday: null,
  inboxSize: 0,
  wantedAgeFrom: 18,
  wantedAgeTo: 80,
  state: 0
})

function isNullOrEmpty (val) {
  return val === null
    || val === '' // since val is saved as empty string. todo: stricter typing required
    || val === 0 // for age init
}

export function isUserExist (user) {
  // since user is initialized as empty User in reducer.UserState.
  // this checks if user is registered. might be some better way
  if (!user.hid && !user.firstName) { return false }
  return !!user.hid || !!user.firstName
}

export function isUserMissingCriticalDetails (user) {
  if (!isUserExist(user)) { return false }

  return (
    isNullOrEmpty(user.gidSeeking)
    ||
    isNullOrEmpty(user.gidIs)
    // ||
    // isNullOrEmpty(user.age) //todo: this is disabled just for mean time - let's talk about the flow
    // ||
    // user.tagline.length < 1 // todo: proposal - let's consult with product
  )
}
