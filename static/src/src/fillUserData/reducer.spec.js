/* eslint no-throw-literal: 0 */
import { ASYNC_STATES } from '../enums'
import { START_FILL_DATA, UPDATE_DATA, UPDATE_DATA_ERROR, UPLOAD_USER_IMAGE_DONE } from './action-types'
import { SignupEditData, signupEditDataReducer, User } from './reducer'

describe('REDUCER', () => {

  it(`START_FILL_DATA should set fetchState as BEFORE`, () => {
    const nextState = signupEditDataReducer(SignupEditData, { type: START_FILL_DATA })
    expect(nextState.fetchState).toEqual(ASYNC_STATES.BEFORE)
    expect(nextState.user).toEqual(User)
  })

  it(`UPDATE_DATA should set fields to user`, () => {
    const nextState = signupEditDataReducer(SignupEditData,
      { type: UPDATE_DATA, payload: { firstName: 'test_name' } })
    expect(nextState.user.firstName).toEqual('test_name')
  })

  it(`UPDATE_DATA should set photoURL if gidIs and gidSeeking`, () => {
    const nextState = signupEditDataReducer(SignupEditData,
      { type: UPDATE_DATA, payload: { gidIs: 1, gidSeeking: 2 } })
    expect(nextState.user.gidIs).toEqual(1)
    expect(nextState.user.gidSeeking).toEqual(2)
    expect(nextState.user.photoURL).toEqual('default_male')
  })

  it(`UPDATE_DATA should set photoURL if gidIs and gidSeeking`, () => {
    const nextState = signupEditDataReducer(SignupEditData,
      { type: UPDATE_DATA, payload: { avatar: '123234.png' } })
    expect(nextState.user.photoURL).toBeDefined()
  })

  it('UPDATE_DATA_ERROR should clear user and set fetchState to FAIL', () => {
    const nextState = signupEditDataReducer(SignupEditData, { type: UPDATE_DATA_ERROR })
    expect(nextState.fetchState).toEqual(ASYNC_STATES.FAIL)
    expect(nextState.user).toEqual(User)
  })

  it('UPLOAD_USER_IMAGE_DONE should set imageUploadStart in user', () => {
    const nextState = signupEditDataReducer(SignupEditData,
      { type: UPLOAD_USER_IMAGE_DONE, payload: { status: ASYNC_STATES.FAIL } })
    expect(nextState.user.imageUploadState).toEqual(ASYNC_STATES.FAIL)
  })

})
