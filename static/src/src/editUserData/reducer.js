import { Record } from 'immutable'
import { avatarUrlToPhotoUrlObj, rewriteUrlImageForDefault } from 'src/common/utils'
import { ASYNC_STATES, GENDER } from 'src/enums'
import {
  CLEAR_EDIT_DATA_FOR_USER,
  LOAD_EDIT_DATA_FOR_USER_ERROR,
  LOAD_EDIT_DATA_FOR_USER_START,
  LOAD_EDIT_DATA_FOR_USER_SUCCESS,
  UPLOAD_USER_IMAGE_DONE
} from './action-types'

export const User = Record({
  bio: '',
  firstName: '',
  photoURL: '',
  tagline: '',
  viewerHid: '',
  targetHid: '',
  age: 18,
  seekingAgeFrom: 18,
  seekingAgeTo: 80,
  birthday: '',
  email: '',
  gidIs: GENDER.MALE,
  gidSeeking: GENDER.FEMALE,
  inboxSize: 1,
  imageUploadState: ASYNC_STATES.BEFORE
})
export const UserEditData = new Record({
  user: new User(),
  fetchState: ASYNC_STATES.BEFORE,
})

export function userEditDataReducer (state = new UserEditData(), { payload, type }) {
  switch (type) {
    case LOAD_EDIT_DATA_FOR_USER_START:
      return state.set('fetchState', ASYNC_STATES.DURING)

    case LOAD_EDIT_DATA_FOR_USER_ERROR:
      return state.merge({
        user: state.user.clear(),
        fetchState: ASYNC_STATES.FAIL
      })

    case LOAD_EDIT_DATA_FOR_USER_SUCCESS:

      let { photoURL } = avatarUrlToPhotoUrlObj(payload.avatarUrl)
      photoURL = rewriteUrlImageForDefault(photoURL, payload.gidIs)

      const user = {
        ...payload,
        photoURL,
        inboxSize: payload.maxIntros
      }

      return state.merge({
        user: new User(user),
        fetchState: ASYNC_STATES.BEFORE
      })

    case UPLOAD_USER_IMAGE_DONE:
      return state.merge({
        user: state.get('user').set('imageUploadState', payload.status)
      })

    case CLEAR_EDIT_DATA_FOR_USER:
      return state.merge({
        user: state.user.clear()
      })

    default:
      return state
  }
}
