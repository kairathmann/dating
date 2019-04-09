import { toAction } from 'src/common/utils'
import api from 'src/api'
import { unloadUser } from 'src/user/actions'
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

export function initAuth (user) {
  return {
    type: INIT_AUTH,
    payload: user,
  }
}

export function signInError () {
  return {
    type: SIGN_IN_ERROR,
  }
}

export function signInSuccess (result) {
  return {
    type: SIGN_IN_SUCCESS,
    payload: result.user,
  }
}

export function signInLocalSuccess (result) {
  return {
    type: SIGN_IN_LOCAL_SUCCESS,
    payload: result.data,
  }
}

export function signInLocalError (error) {
  return {
    type: SIGN_IN_LOCAL_ERROR,
    payload: error,
  }
}

export function signUp (signUpParams, redirect) {
  return dispatch => {
    return api.signup(signUpParams)
      .then(result => {
        dispatch(signUpSuccess(result.data, dispatch))
        if (redirect) { redirect() } // redirect to recommend profile page after signup
      })
      .catch(error => {
        const err = (error.response) ? error.response.data : error
        dispatch(signUpError(err))
      })
  }
}

export function signUpError (error) {
  const message = error.code || error
  return {
    type: SIGN_UP_ERROR,
    payload: message,
  }
}

export function signUpSuccess (result) {
  return {
    type: SIGN_UP_SUCCESS,
    payload: result.data,
  }
}

export function signInLocal (signInParams) {
  return dispatch => {
    return api.signin(signInParams)
      .then(result => {
        dispatch(signInLocalSuccess(result.data, dispatch))

        return result.data.data.reactivated
      })
      .catch(error => {
        const err = (error.response) ? error.response.data : error
        dispatch(signInLocalError(err))
      })
  }
}

export function forgotPasswordError (error) {
  return {
    type: FORGOT_PASSWORD_ERROR,
    payload: error,
  }
}

export function forgotPasswordSuccess (result) {
  return {
    type: FORGOT_PASSWORD_SUCCESS,
    payload: result.data,
  }
}

export function forgotPassword (email) {
  return dispatch => {
    return api.forgotPassword(email)
      .then(result => {
        if (!result.data.success) { throw (result.data)}
        dispatch(forgotPasswordSuccess(result, dispatch))
      })
      .catch(error => {
        const err = (error.response) ? error.response.data : error
        dispatch(forgotPasswordError(err))
      })
  }
}

export function resetPassword ({ password, token }, redirect) {
  return dispatch => {
    return api.resetPassword({ password, token })
      .then(() => {
        if (redirect) {
          setTimeout(() => {
            redirect()
          }, 0)
        }
      })
      .catch(error => {
        const err = (error.response) ? error.response.data : error
        dispatch(toAction(RESET_PASSWORD_ERROR, err))
      })
  }
}

export function confirmEmail (token) {
  // no state change or redirects (currently)
  return dispatch => {
    return api.confirmEmail({token})
  }
}

export function signOut () {
  return dispatch => {
    return api.logout()
      .then(result => {
        dispatch(unloadUser())
        dispatch(signOutSuccess(result.data, dispatch))
      })
      .catch(() => {})
  }
}

export function signOutSuccess () {
  return {
    type: SIGN_OUT_SUCCESS,
  }
}

export function clearLastError () {
  return {
    type: CLEAR_LAST_ERROR
  }
}
