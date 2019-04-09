import { Record } from 'immutable'

import { avatarUrlToPhotoUrlObj, rewriteUrlImageForDefault } from 'src/common/utils'
import { LOAD_USER_SUCCESS, LOAD_VIEW_USER, UNLOAD_USER_SUCCESS, UPDATE_USER_SUCCESS } from './action-types'

export const Balance = new Record({
  confirmedBalance: 0,
  unconfirmedBalance: 0,
})

export const UserState = new Record({
  isNotFetchedYet: true,
  authenticated: false,
  id: null,
  name: null,
  email: null,
  photoURL: null,
  tagline: null,
  bio: null,
  gender: null,
  sexuality: null,
  birthday: null,
  age: 0,
  inboxSize: 0,
  wantedAgeFrom: 18,
  wantedAgeTo: 80,
  balance: new Balance(),
  state: 0
})

const ViewUserState = new Record({
  bio: '',
  firstName: '',
  photoURL: '',
  tagline: '',
  viewerHid: '',
  targetHid: '',
  age: 0
})

export function viewUserReducer (state = new ViewUserState(), { payload, type }) {

  switch (type) {
    case LOAD_VIEW_USER:
      let { photoURL } = avatarUrlToPhotoUrlObj(payload.avatarUrl)
      photoURL = rewriteUrlImageForDefault(photoURL, payload.gidIs)

      const user = new ViewUserState({
        ...payload,
        photoURL
      })
      return state.merge(user)

    default:
      return state
  }

}

export default function userReducer (state = new UserState(), { payload, type }) {
  switch (type) {
    case LOAD_USER_SUCCESS:
      let { photoURL } = avatarUrlToPhotoUrlObj(payload.avatarUrl)
      photoURL = rewriteUrlImageForDefault(photoURL, payload.gidIs)
      return state.merge({
        isNotFetchedYet: false,
        id: payload ? payload.targetHid : null,
        name: payload ? payload.firstName : null,
        email: payload ? payload.email : null,
        photoURL: payload ? photoURL : null,
        tagline: payload ? payload.tagline : null,
        bio: payload ? payload.bio : null,
        gender: payload ? payload.gidIs : null,
        sexuality: payload ? payload.gidSeeking : null,
        age: payload ? payload.age : null,
        inboxSize: payload ? payload.maxIntros : 1,
        wantedAgeFrom: payload ? payload.wantedAgeFrom : 18,
        wantedAgeTo: payload ? payload.wantedAgeTo : 88,
        state: payload ? payload.state : 0,
        balance: payload ? (new Balance().merge({
          'confirmedBalance': parseFloat(payload.balance.confirmed),
          'unconfirmedBalance': parseFloat(payload.balance.unconfirmed)
        })) : null,
      })

    case UPDATE_USER_SUCCESS:
      return state
    case UNLOAD_USER_SUCCESS:
      return new UserState()

    default:
      return state
  }
}
