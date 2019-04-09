/* eslint no-throw-literal: 0 */
import { ASYNC_STATES } from '../enums'
import {
  CLEAR_EDIT_DATA_FOR_USER,
  LOAD_EDIT_DATA_FOR_USER_ERROR,
  LOAD_EDIT_DATA_FOR_USER_START,
  LOAD_EDIT_DATA_FOR_USER_SUCCESS, UPLOAD_USER_IMAGE_DONE
} from './action-types'
import { User, UserEditData, userEditDataReducer } from './reducer'

describe('REDUCER', () => {

  it(`LOAD_EDIT_DATA_FOR_USER_START should set fetchState as DURING`, () => {
    const nextState = userEditDataReducer(new UserEditData(), { type: LOAD_EDIT_DATA_FOR_USER_START })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.DURING)
  })

  it(`LOAD_EDIT_DATA_FOR_USER_ERROR should set fetchState as FAIL and clean user`, () => {
    const nextState = userEditDataReducer(new UserEditData(), { type: LOAD_EDIT_DATA_FOR_USER_ERROR })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.FAIL)
    expect(nextState.get('user')).toEqual(new User())
  })

  it(`LOAD_EDIT_DATA_FOR_USER_SUCCESS should set user with processed urls`, () => {
    const nextState = userEditDataReducer(new UserEditData(),
      { type: LOAD_EDIT_DATA_FOR_USER_SUCCESS, payload: { avatarUrl: 'hydra/img/src/', gidIs: 3, maxIntros: 2 } })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.BEFORE)
    expect(nextState.get('user')).toEqual(new User({ maxIntros: 2, inboxSize: 2, gidIs: 3, photoURL: 'default_other' }))
  })
  it('UPLOAD_USER_IMAGE_DONE should set imageUploadStart in user', () => {
    const nextState = userEditDataReducer(new UserEditData(),
      { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.FAIL} })
    expect(nextState.get('user').get('imageUploadState')).toEqual(ASYNC_STATES.FAIL)
  })
  it('CLEAR_EDIT_DATA_FOR_USER should clear user', () => {
    const nextState = userEditDataReducer(new UserEditData(),
      { type: CLEAR_EDIT_DATA_FOR_USER })
    expect(nextState.get('user')).toEqual(new User())
  })
})
