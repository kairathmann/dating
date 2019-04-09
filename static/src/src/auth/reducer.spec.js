/* eslint no-throw-literal: 0 */
import {
  CLEAR_LAST_ERROR,
  FORGOT_PASSWORD_ERROR,
  FORGOT_PASSWORD_SUCCESS,
  INIT_AUTH, RESET_PASSWORD_ERROR, SIGN_IN_LOCAL_ERROR,
  SIGN_IN_LOCAL_SUCCESS,
  SIGN_IN_SUCCESS, SIGN_UP_ERROR,
  SIGN_UP_SUCCESS
} from './action-types'
import {authReducer, AuthState } from './reducer'

describe('REDUCER', () => {

  [INIT_AUTH, SIGN_IN_LOCAL_SUCCESS, SIGN_IN_SUCCESS, SIGN_UP_SUCCESS].forEach(type => {
    it(`${type} should set authenticated as false if no payload`, () => {
      const nextState = authReducer(new AuthState(), { type, payload: null })
      expect(nextState.get('authenticated')).toEqual(false)
    })
    it(`${type} should set authenticated as true if payload equals true`, () => {
      const nextState = authReducer(new AuthState(), { type, payload: true })
      expect(nextState.get('authenticated')).toEqual(true)
    })
    it(`${type} should set authenticated as false if payload false`, () => {
      const nextState = authReducer(new AuthState(), { type, payload: false })
      expect(nextState.get('authenticated')).toEqual(false)
    })
  })

  it('FORGOT_PASSWORD_SUCCESS', () => {
    const nextState = authReducer(new AuthState(), {type: FORGOT_PASSWORD_SUCCESS })
    expect(nextState.get('forgotPasswordLastResult')).toEqual('forgot.check_email')
  })

  it('SIGN_IN_LOCAL_ERROR', () => {
    const nextState = authReducer(new AuthState(), { type: SIGN_IN_LOCAL_ERROR, payload: 'error'})
    expect(nextState.get('signInLastResult')).toEqual('error')
  })

  it('SIGN_UP_ERROR', () => {
    const nextState = authReducer(new AuthState(), { type: SIGN_UP_ERROR, payload: 'error'})
    expect(nextState.get('signUpLastResult')).toEqual('error')
  })

  it('FORGOT_PASSWORD_ERROR', () => {
    const nextState = authReducer(new AuthState(), { type: FORGOT_PASSWORD_ERROR, payload: 'error'})
    expect(nextState.get('forgotPasswordLastResult')).toEqual('error')
  })
  it('RESET_PASSWORD', () => {
    const nextState = authReducer(new AuthState(), { type: RESET_PASSWORD_ERROR, payload: 'error'})
    expect(nextState.get('resetPasswordLastResult')).toEqual('error')
  })
  it('CLEAR_LAST_ERROR', () => {
    const nextState = authReducer(new AuthState(), { type: CLEAR_LAST_ERROR})
    expect(nextState).toEqual(new AuthState())
  })
})
