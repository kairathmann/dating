import { avatarUrlToPhotoUrlObj, rewriteUrlImageForDefault } from 'src/common/utils'
import { ASYNC_STATES } from '../enums'
import { START_FILL_DATA, UPDATE_DATA, UPDATE_DATA_ERROR, UPLOAD_USER_IMAGE_DONE } from './action-types'

export const User = {
  firstName: '',
  photoURL: '',
  tagline: '',
  birthDate: '',
  seekingAgeFrom: 18,
  seekingAgeTo: 45,
  email: '',
  gidIs: null,
  gidSeeking: null,
  inboxSize: 4,
  imageUploadState: ASYNC_STATES.BEFORE
}

export const SignupEditData = {
  user: User,
  fetchState: ASYNC_STATES.BEFORE,
}

export function signupEditDataReducer (state = SignupEditData, { payload, type }) {
  switch (type) {
    case START_FILL_DATA:
      return {
        ...state,
        user: User
      }
    case UPDATE_DATA:
      if (payload.gidIs && payload.gidSeeking) {
        payload = { ...payload, photoURL: rewriteUrlImageForDefault('hydra/img/src/', payload.gidIs) }
      }
      if (payload.avatar) {
        const { photoURL } = avatarUrlToPhotoUrlObj(payload.avatar)
        payload = {
          ...payload,
          photoURL
        }
      }
      return {
        ...state,
        user: {
          ...state.user,
          ...payload
        }
      }

    case UPDATE_DATA_ERROR:
      return {
        user: User,
        fetchState: ASYNC_STATES.FAIL
      }

    case UPLOAD_USER_IMAGE_DONE:
      return {
        ...state,
        user: {
          ...state.user,
          imageUploadState: payload.status
        }
      }

    default:
      return state
  }
}
