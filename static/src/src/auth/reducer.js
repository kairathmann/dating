import { Record } from 'immutable'
import {
  CLEAR_LAST_ERROR,
  FORGOT_PASSWORD_ERROR,
  FORGOT_PASSWORD_SUCCESS,
  INIT_AUTH,
  RESET_PASSWORD_ERROR,
  SIGN_IN_ERROR,
  SIGN_IN_LOCAL_ERROR,
  SIGN_IN_LOCAL_SUCCESS,
  SIGN_IN_SUCCESS,
  SIGN_OUT_SUCCESS,
  SIGN_UP_ERROR,
  SIGN_UP_SUCCESS
} from './action-types'

export const AuthState = new Record({
  authenticated: null,
  signInLastResult: null,
  signUpLastResult: null,
  forgotPasswordLastResult: null,
  resetPasswordLastResult: null
})

export function authReducer (state = new AuthState(), { payload, type }) {
  switch (type) {
    case INIT_AUTH:
    case SIGN_IN_SUCCESS:
      return state.merge({
        authenticated: !!payload,
      })

    case SIGN_OUT_SUCCESS:
    case SIGN_IN_ERROR:
      return state.set('authenticated', false)

    case SIGN_UP_SUCCESS:
      return state.merge({
        authenticated: !!payload,
      })

    case SIGN_IN_LOCAL_SUCCESS:
      return state.merge({
        authenticated: !!payload,
      })

    case FORGOT_PASSWORD_SUCCESS:
      return state.merge({ forgotPasswordLastResult: 'forgot.check_email' })

    case SIGN_IN_LOCAL_ERROR:
      return state.merge({ signInLastResult: payload })

    case SIGN_UP_ERROR:
      return state.merge({ signUpLastResult: payload })

    case FORGOT_PASSWORD_ERROR:
      return state.merge({ forgotPasswordLastResult: payload })

    case RESET_PASSWORD_ERROR:
      return state.merge({ resetPasswordLastResult: payload })

    case CLEAR_LAST_ERROR:
      return state.merge({
        resetPasswordLastResult: null,
        forgotPasswordLastResult: null,
        signUpLastResult: null,
        signInLastResult: null
      })

    default:
      return state
  }
}
